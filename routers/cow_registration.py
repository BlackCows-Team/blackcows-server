# routers/cow_registration.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
import os
import httpx
import xml.etree.ElementTree as ET

from routers.auth_firebase import get_current_user
from services.cow_firebase_service import CowFirebaseService
from schemas.cow import CowCreate, CowResponse, HealthStatus, BreedingStatus
from config.firebase_config import get_firestore_client

router = APIRouter()

class EarTagCheckRequest(BaseModel):
    ear_tag_number: str
    
    @validator('ear_tag_number')
    def validate_ear_tag_number(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('이표번호는 필수입니다')
        clean_number = v.strip()
        if len(clean_number) != 12:
            raise ValueError('이표번호는 12자리여야 합니다')
        if not clean_number.isdigit():
            raise ValueError('이표번호는 숫자만 입력 가능합니다')
        return clean_number

class LivestockTraceRegisterRequest(BaseModel):
    ear_tag_number: str
    user_cow_name: Optional[str] = None  # 사용자가 원하는 젖소 이름

# ===== API 엔드포인트 =====

@router.post("/check-ear-tag",
             summary="이표번호 확인 및 축산물이력제 조회",
             description="이표번호 중복 확인 후 축산물품질평가원에서 소 정보를 조회합니다.")
async def check_ear_tag_and_get_livestock_info(
    request: EarTagCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    이표번호 확인 및 축산물이력제 조회
    
    **반환값:**
    - can_register: 등록 가능 여부
    - has_trace_info: 축산물이력제 정보 보유 여부
    - trace_info: 축산물이력제 소 정보 (있는 경우)
    """
    try:
        farm_id = current_user.get("farm_id")
        
        # 1. 이표번호 중복 확인
        db = get_firestore_client()
        existing_cow_query = db.collection('cows')\
            .where(filter=('farm_id', '==', farm_id))\
            .where(filter=('ear_tag_number', '==', request.ear_tag_number))\
            .where(filter=('is_active', '==', True))\
            .get()
        
        if existing_cow_query:
            return {
                "success": False,
                "can_register": False,
                "message": f"이표번호 '{request.ear_tag_number}'는 이미 등록되어 있습니다.",
                "error_type": "duplicate"
            }
        
        # 2. 축산물품질평가원 API 조회
        service_key = os.getenv("LIVESTOCK_TRACE_API_ENCODING_EKEY")
        if not service_key:
            return {
                "success": True,
                "can_register": True,
                "has_trace_info": False,
                "message": "축산물이력제 API가 설정되지 않아 수동 등록만 가능합니다."
            }
        
        try:
            # API 호출
            base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
            params = {
                "ServiceKey": service_key,
                "traceNo": request.ear_tag_number,
                "optionNo": "1"  # 개체 정보 조회
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(base_url, params=params, timeout=30.0)
                
                if response.status_code != 200:
                    raise Exception(f"API 호출 실패: {response.status_code}")
                
                # XML 응답 파싱
                root = ET.fromstring(response.text)
                
                # 응답 상태 확인
                header = root.find('header')
                if header is not None:
                    result_code = header.find('resultCode')
                    if result_code is not None and result_code.text != "00":
                        result_msg = header.find('resultMsg')
                        error_msg = result_msg.text if result_msg is not None else "알 수 없는 오류"
                        raise Exception(f"API 오류: {error_msg}")
                
                # 데이터 파싱
                items = root.find('.//items')
                if items is None or len(items.findall('item')) == 0:
                    # 축산물이력제에 정보 없음
                    return {
                        "success": True,
                        "can_register": True,
                        "has_trace_info": False,
                        "message": "축산물이력제에서 소 정보를 찾을 수 없습니다."
                    }
                
                # 소 정보 추출
                item = items.find('item')
                trace_info = {}
                
                for element in item:
                    value = element.text
                    if element.tag == 'birthYmd':
                        # YYYYMMDD → YYYY-MM-DD 변환
                        if value and len(value) == 8:
                            trace_info['birth_date'] = f"{value[:4]}-{value[4:6]}-{value[6:8]}"
                    elif element.tag == 'sexNm':
                        trace_info['gender'] = value
                    elif element.tag == 'lsTypeNm':
                        trace_info['breed'] = value
                    elif element.tag == 'farmAddr':
                        trace_info['farm_address'] = value
                    elif element.tag == 'farmerNm':
                        trace_info['farm_owner'] = value
                    elif element.tag == 'cattleNo':
                        trace_info['cattle_no'] = value
                    elif element.tag == 'farmUniqueNo':
                        trace_info['farm_unique_no'] = value
                
                return {
                    "success": True,
                    "can_register": True,
                    "has_trace_info": True,
                    "message": "축산물이력제에서 소 정보를 찾았습니다.",
                    "trace_info": trace_info
                }
                
        except Exception as api_error:
            # API 호출 실패 시
            return {
                "success": True,
                "can_register": True,
                "has_trace_info": False,
                "message": f"축산물이력제 조회 중 오류가 발생했습니다: {str(api_error)}"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이표번호 확인 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/register-with-trace",
             response_model=CowResponse,
             summary="축산물이력제 정보로 젖소 등록",
             description="축산물이력제에서 조회된 정보를 사용하여 젖소를 등록합니다.")
async def register_cow_with_trace_info(
    request: LivestockTraceRegisterRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    축산물이력제 정보로 젖소 등록
    
    이표번호로 축산물이력제를 다시 조회한 후 젖소를 등록합니다.
    (보안상 프론트엔드에서 전달받은 정보 대신 서버에서 직접 재조회)
    
    **반환값:**
    - 성공 시 등록된 젖소 정보
    - 실패 시 오류 메시지
    """
    try:
        # 1. 축산물이력제 정보 재조회 (보안상 중요)
        service_key = os.getenv("LIVESTOCK_TRACE_API_ENCODING_EKEY")
        if not service_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="축산물이력제 API가 설정되지 않았습니다"
            )
        
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        params = {
            "ServiceKey": service_key,
            "traceNo": request.ear_tag_number,
            "optionNo": "1"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, timeout=30.0)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="축산물이력제 조회에 실패했습니다"
                )
            
            # XML 파싱
            root = ET.fromstring(response.text)
            items = root.find('.//items')
            if items is None or len(items.findall('item')) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="축산물이력제에서 소 정보를 찾을 수 없습니다"
                )
            
            # 소 정보 추출
            item = items.find('item')
            birth_date = None
            breed = None
            cattle_no = None
            farm_owner = None
            
            for element in item:
                if element.tag == 'birthYmd' and element.text:
                    # YYYYMMDD → YYYY-MM-DD 변환
                    if len(element.text) == 8:
                        birth_date = f"{element.text[:4]}-{element.text[4:6]}-{element.text[6:8]}"
                elif element.tag == 'lsTypeNm':
                    breed = element.text
                elif element.tag == 'cattleNo':
                    cattle_no = element.text
                elif element.tag == 'farmerNm':
                    farm_owner = element.text
        
        # 2. 젖소 이름 결정
        cow_name = request.user_cow_name or f"소-{request.ear_tag_number[-4:]}"
        
        # 3. 젖소 등록
        notes_parts = ["축산물이력제 연동 등록"]
        if cattle_no:
            notes_parts.append(f"개체번호: {cattle_no}")
        if farm_owner:
            notes_parts.append(f"원농장주: {farm_owner}")
        
        cow_create_data = CowCreate(
            ear_tag_number=request.ear_tag_number,
            name=cow_name,
            birthdate=birth_date,
            breed=breed,
            notes=" | ".join(notes_parts)
        )
        
        registered_cow = CowFirebaseService.create_cow(cow_create_data, current_user)
        
        return registered_cow
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"축산물이력제 연동 등록 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/api-status",
            summary="축산물이력제 API 상태 확인",
            description="축산물품질평가원 API 연결 상태를 확인합니다.")
async def check_livestock_trace_api_status():
    """축산물이력제 API 상태 확인"""
    service_key = os.getenv("LIVESTOCK_TRACE_API_ENCODING_EKEY")
    
    if not service_key:
        return {
            "api_available": False,
            "message": "축산물이력제 API 키가 설정되지 않았습니다.",
            "recommendation": "수동 등록만 사용 가능합니다."
        }
    
    try:
        # 테스트용 API 호출 (존재하지 않는 이표번호로 테스트)
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        params = {
            "ServiceKey": service_key,
            "traceNo": "000000000001",  # 테스트용 이표번호
            "optionNo": "1"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                return {
                    "api_available": True,
                    "message": "축산물이력제 API가 정상 작동 중입니다.",
                    "recommendation": "이표번호 연동 등록을 사용할 수 있습니다."
                }
            else:
                return {
                    "api_available": False,
                    "message": f"API 응답 오류: {response.status_code}",
                    "recommendation": "수동 등록만 사용 가능합니다."
                }
    
    except Exception as e:
        return {
            "api_available": False,
            "message": f"API 연결 실패: {str(e)}",
            "recommendation": "수동 등록만 사용 가능합니다."
        }

# ===== 디버깅 및 테스트용 엔드포인트 =====

@router.get("/test-trace/{ear_tag_number}",
            summary="축산물이력제 조회 테스트",
            description="개발/테스트용 - 이표번호로 축산물이력제 원본 응답을 확인합니다.")
async def test_livestock_trace_lookup(ear_tag_number: str):
    """개발/테스트용 축산물이력제 조회"""
    service_key = os.getenv("LIVESTOCK_TRACE_API_ENCODING_EKEY")
    if not service_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="축산물이력제 API 키가 설정되지 않았습니다"
        )
    
    try:
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        params = {
            "ServiceKey": service_key,
            "traceNo": ear_tag_number,
            "optionNo": "1"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, timeout=30.0)
            
            return {
                "ear_tag_number": ear_tag_number,
                "status_code": response.status_code,
                "raw_xml": response.text,
                "request_params": params
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"테스트 조회 실패: {str(e)}"
        )
        
        
# 테스트용 엔드포인트
@router.post("/test-check-ear-tag",
             summary="테스트용: 인증 없는 이표번호 확인",
             description="개발/테스트용 - 인증 없이 이표번호 확인 및 축산물이력제 조회")
async def test_check_ear_tag_no_auth(request: EarTagCheckRequest):
    """
    테스트용: 인증 없는 이표번호 확인
    실제 배포시에는 제거해야 함
    """
    try:
        # 인증 없이 축산물이력제만 조회
        service_key = os.getenv("LIVESTOCK_TRACE_API_ENCODING_EKEY")
        if not service_key:
            return {
                "success": True,
                "can_register": True,
                "has_trace_info": False,
                "message": "축산물이력제 API가 설정되지 않아 수동 등록만 가능합니다."
            }
        
        try:
            # API 호출
            base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
            params = {
                "ServiceKey": service_key,
                "traceNo": request.ear_tag_number,
                "optionNo": "1"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(base_url, params=params, timeout=30.0)
                
                if response.status_code != 200:
                    raise Exception(f"API 호출 실패: {response.status_code}")
                
                # XML 응답 파싱
                root = ET.fromstring(response.text)
                
                # 응답 상태 확인
                header = root.find('header')
                if header is not None:
                    result_code = header.find('resultCode')
                    if result_code is not None and result_code.text != "00":
                        result_msg = header.find('resultMsg')
                        error_msg = result_msg.text if result_msg is not None else "알 수 없는 오류"
                        raise Exception(f"API 오류: {error_msg}")
                
                # 데이터 파싱
                items = root.find('.//items')
                if items is None or len(items.findall('item')) == 0:
                    return {
                        "success": True,
                        "can_register": True,
                        "has_trace_info": False,
                        "message": "축산물이력제에서 소 정보를 찾을 수 없습니다.",
                        "test_mode": True
                    }
                
                # 소 정보 추출
                item = items.find('item')
                trace_info = {}
                
                for element in item:
                    value = element.text
                    if element.tag == 'birthYmd':
                        if value and len(value) == 8:
                            trace_info['birth_date'] = f"{value[:4]}-{value[4:6]}-{value[6:8]}"
                    elif element.tag == 'sexNm':
                        trace_info['gender'] = value
                    elif element.tag == 'lsTypeNm':
                        trace_info['breed'] = value
                    elif element.tag == 'farmAddr':
                        trace_info['farm_address'] = value
                    elif element.tag == 'farmerNm':
                        trace_info['farm_owner'] = value
                    elif element.tag == 'cattleNo':
                        trace_info['cattle_no'] = value
                
                return {
                    "success": True,
                    "can_register": True,
                    "has_trace_info": True,
                    "message": "축산물이력제에서 소 정보를 찾았습니다.",
                    "trace_info": trace_info,
                    "test_mode": True
                }
                
        except Exception as api_error:
            return {
                "success": True,
                "can_register": True,
                "has_trace_info": False,
                "message": f"축산물이력제 조회 중 오류가 발생했습니다: {str(api_error)}",
                "test_mode": True
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"테스트 조회 중 오류가 발생했습니다: {str(e)}"
        )