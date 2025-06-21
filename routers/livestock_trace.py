# routers/livestock_trace.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
import httpx
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta

from routers.auth_firebase import get_current_user

router = APIRouter()

class LivestockTraceRequest(BaseModel):
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

class CattleBasicInfo(BaseModel):
    cattle_no: Optional[str] = None              # 개체번호
    ear_tag_number: str                          # 이표번호
    birth_date: Optional[str] = None             # 출생년월일 (YYYY-MM-DD)
    age_months: Optional[int] = None             # 개월령
    breed: Optional[str] = None                  # 소의 종류 (한우, 홀스타인 등)
    gender: Optional[str] = None                 # 성별
    import_elapsed_months: Optional[int] = None  # 수입경과월
    import_country: Optional[str] = None         # 수입국가
    farm_unique_no: Optional[str] = None         # 농장식별번호
    farm_no: Optional[str] = None                # 농장번호
    lumpy_skin_last_vaccination: Optional[str] = None  # 럼피스킨 최종접종일

class FarmRegistrationInfo(BaseModel):
    farm_address: Optional[str] = None           # 사육지 주소
    farmer_name: Optional[str] = None            # 농장경영자명
    registration_type: Optional[str] = None      # 신고구분
    registration_date: Optional[str] = None      # 신고 년월일
    farm_no: Optional[str] = None                # 농장번호

class SlaughterInfo(BaseModel):
    slaughter_place_address: Optional[str] = None  # 도축장 주소
    slaughter_place_name: Optional[str] = None     # 도축장명
    slaughter_date: Optional[str] = None           # 도축일자
    grade: Optional[str] = None                    # 등급
    marbling_score: Optional[str] = None           # 근내지방도
    inspection_result: Optional[str] = None        # 위생검사 결과

class PackagingInfo(BaseModel):
    processing_place_address: Optional[str] = None  # 포장처리업소 주소
    processing_place_name: Optional[str] = None     # 포장처리업소명

class VaccinationInfo(BaseModel):
    fmd_injection_days: Optional[str] = None         # 구제역 백신접종경과일
    fmd_injection_date: Optional[str] = None         # 구제역 백신접종일
    fmd_vaccine_order: Optional[str] = None          # 구제역 백신접종 차수

class HealthInspectionInfo(BaseModel):
    disease_status: Optional[str] = None             # 질병유무

class BrucellaInfo(BaseModel):
    brucella_inspection_date: Optional[str] = None   # 브루셀라 검사일
    brucella_result: Optional[str] = None            # 브루셀라 검사결과
    brucella_days_elapsed: Optional[int] = None      # 브루셀라 검사일로부터 경과일

class TuberculosisInfo(BaseModel):
    tb_inspection_date: Optional[str] = None         # 결핵 검사일
    tb_result: Optional[str] = None                  # 결핵 검사결과

class LivestockTraceResponse(BaseModel):
    success: bool
    message: str
    ear_tag_number: str
    
    # 기본 개체 정보
    basic_info: Optional[CattleBasicInfo] = None
    
    # 농장 등록 정보 (여러 농장 이력 가능)
    farm_registrations: List[FarmRegistrationInfo] = []
    
    # 도축 정보
    slaughter_info: Optional[SlaughterInfo] = None
    
    # 포장 처리 정보
    packaging_info: Optional[PackagingInfo] = None
    
    # 구제역 백신 정보
    vaccination_info: Optional[VaccinationInfo] = None
    
    # 질병 정보
    health_inspection: Optional[HealthInspectionInfo] = None
    
    # 브루셀라 검사 정보
    brucella_info: Optional[BrucellaInfo] = None
    
    # 결핵 검사 정보
    tuberculosis_info: Optional[TuberculosisInfo] = None

@router.get("/livestock-trace/{ear_tag_number}",
            response_model=LivestockTraceResponse,
            summary="축산물이력정보 전체 조회",
            description="""
            이표번호를 통해 축산물품질평가원 OpenAPI에서 소의 전체 이력정보를 조회합니다.
            
            **조회 정보:**
            - 기본 개체정보 (이력번호, 출생일, 품종, 성별 등)
            - 농장 등록 정보 (사육지, 농장경영자, 신고이력 등)
            - 도축 및 포장 처리 정보
            - 구제역 백신 접종 정보
            - 브루셀라 검사 정보 (검사일로부터 경과일 포함)
            - 결핵 검사 정보
            - 질병 정보
            
            **참고사항:**
            - 모든 정보가 존재하지 않을 수 있으며, 해당 없는 정보는 null로 반환됩니다
            - 브루셀라 검사는 검사일로부터 경과일을 자동 계산합니다
            - 개월령은 출생일 기준으로 자동 계산됩니다
            """)
async def get_livestock_trace_info(
    ear_tag_number: str,
    current_user: dict = Depends(get_current_user)
):
    """축산물이력정보 전체 조회"""
    try:
        service_key = os.getenv("LIVESTOCK_TRACE_API_DECODING_KEY")
        if not service_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="축산물이력제 API 키가 설정되지 않았습니다"
            )
        
        # 이표번호 검증
        if len(ear_tag_number) != 12 or not ear_tag_number.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이표번호는 12자리 숫자여야 합니다"
            )
        
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        
        # 응답 데이터 초기화
        response_data = LivestockTraceResponse(
            success=True,
            message="축산물이력정보 조회 완료",
            ear_tag_number=ear_tag_number,
            farm_registrations=[]
        )
        
        # 1. 기본 개체정보 조회 (optionNo=1)
        basic_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "1")
        if basic_info:
            response_data.basic_info = _parse_basic_info(basic_info, ear_tag_number)
        
        # 2. 출생 등 신고정보 조회 (optionNo=2) - 여러 농장 이력
        farm_registrations = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "2")
        if farm_registrations:
            response_data.farm_registrations = _parse_farm_registrations(farm_registrations)
        
        # 3. 도축정보 조회 (optionNo=3)
        slaughter_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "3")
        if slaughter_info:
            response_data.slaughter_info = _parse_slaughter_info(slaughter_info)
        
        # 4. 포장정보 조회 (optionNo=4)
        packaging_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "4")
        if packaging_info:
            response_data.packaging_info = _parse_packaging_info(packaging_info)
        
        # 5. 구제역백신 정보 조회 (optionNo=5)
        vaccination_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "5")
        if vaccination_info:
            response_data.vaccination_info = _parse_vaccination_info(vaccination_info)
        
        # 6. 질병정보 조회 (optionNo=6)
        health_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "6")
        if health_info:
            response_data.health_inspection = _parse_health_info(health_info)
        
        # 7. 브루셀라 정보 조회 (optionNo=7)
        brucella_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "7")
        if brucella_info:
            response_data.brucella_info = _parse_brucella_info(brucella_info)
            response_data.tuberculosis_info = _parse_tuberculosis_info(brucella_info)
        
        # 기본 정보가 없으면 데이터를 찾을 수 없는 것으로 판단
        if not response_data.basic_info:
            response_data.success = False
            response_data.message = "축산물이력제에서 해당 이표번호의 정보를 찾을 수 없습니다"
        
        return response_data
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"축산물이력정보 조회 중 오류가 발생했습니다: {str(e)}"
        )

async def _fetch_livestock_data(base_url: str, service_key: str, ear_tag_number: str, option_no: str) -> Optional[List[Dict]]:
    """축산물이력제 API 호출 - corpNo 파라미터 제거"""
    try:
        # URL을 직접 구성하여 이중 인코딩 방지
        import urllib.parse
        
        # 환경변수의 API 키가 이미 인코딩된 상태인지 확인하고 디코딩
        if '%' in service_key:
            # 이미 인코딩된 키라면 디코딩
            decoded_service_key = urllib.parse.unquote(service_key)
            print(f"API 키 디코딩됨: {service_key[:20]}... -> {decoded_service_key[:20]}...")
        else:
            decoded_service_key = service_key
        
        params = {
            "serviceKey": decoded_service_key,
            "traceNo": ear_tag_number,
            "optionNo": option_no
        }
        
        print(f"API 호출 - URL: {base_url}")
        print(f"API 호출 - Params: {params}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, timeout=30.0)
            
            print(f"응답 상태 코드: {response.status_code}")
            print(f"최종 요청 URL: {response.url}")
            print(f"응답 내용 (처음 500자): {response.text[:500]}")
            
            if response.status_code != 200:
                print(f"API 호출 실패 - 상태 코드: {response.status_code}")
                return None
            
            # XML 파싱
            try:
                root = ET.fromstring(response.text)
            except ET.ParseError as e:
                print(f"XML 파싱 오류: {str(e)}")
                return None
            
            # 응답 상태 확인
            header = root.find('header')
            if header is not None:
                result_code = header.find('resultCode')
                result_msg = header.find('resultMsg')
                if result_code is not None:
                    print(f"API 결과 코드: {result_code.text}")
                    if result_msg is not None:
                        print(f"API 결과 메시지: {result_msg.text}")
                    
                    if result_code.text != "00":
                        print(f"API 오류 - 코드: {result_code.text}, 메시지: {result_msg.text if result_msg is not None else 'N/A'}")
                        return None
            
            # 데이터 추출
            items = root.find('.//items')
            if items is None:
                print("items 요소를 찾을 수 없습니다")
                return None
                
            item_elements = items.findall('item')
            if len(item_elements) == 0:
                print("item 요소가 없습니다")
                return None
            
            # 모든 item을 리스트로 반환
            item_list = []
            for item in item_elements:
                item_data = {}
                for element in item:
                    if element.text:  # 빈 값이 아닌 경우만 추가
                        item_data[element.tag] = element.text.strip()
                item_list.append(item_data)
                
            print(f"파싱된 아이템 수: {len(item_list)}")
            if item_list:
                print(f"첫 번째 아이템 키: {list(item_list[0].keys())}")
            
            return item_list
            
    except Exception as e:
        print(f"API 호출 오류 (optionNo={option_no}): {str(e)}")
        return None

def _parse_basic_info(items: List[Dict], ear_tag_number: str) -> CattleBasicInfo:
    """기본 개체정보 파싱"""
    if not items:
        return CattleBasicInfo(ear_tag_number=ear_tag_number)
    
    item = items[0]  # 첫 번째 아이템 사용
    
    # 출생일 파싱 및 개월령 계산
    birth_date = None
    age_months = None
    if item.get('birthYmd') and len(item['birthYmd']) == 8:
        birth_date = f"{item['birthYmd'][:4]}-{item['birthYmd'][4:6]}-{item['birthYmd'][6:8]}"
        try:
            birth_datetime = datetime.strptime(birth_date, '%Y-%m-%d')
            today = datetime.now()
            age_months = (today.year - birth_datetime.year) * 12 + (today.month - birth_datetime.month)
            if age_months < 0:
                age_months = 0
        except:
            pass
    
    return CattleBasicInfo(
        cattle_no=item.get('cattleNo'),
        ear_tag_number=ear_tag_number,
        birth_date=birth_date,
        age_months=age_months,
        breed=item.get('lsTypeNm'),
        gender=item.get('sexNm'),
        import_elapsed_months=int(item['monthDiff']) if item.get('monthDiff') and item['monthDiff'].isdigit() else None,
        import_country=item.get('nationNm'),
        farm_unique_no=item.get('farmUniqueNo'),
        farm_no=item.get('farmNo'),
        lumpy_skin_last_vaccination=_parse_date(item.get('lsdYmd'))
    )

def _parse_farm_registrations(items: List[Dict]) -> List[FarmRegistrationInfo]:
    """농장 등록 정보 파싱 (여러 농장 이력)"""
    registrations = []
    
    for item in items:
        registration = FarmRegistrationInfo(
            farm_address=item.get('farmAddr'),
            farmer_name=item.get('farmerNm'),
            registration_type=item.get('regType'),
            registration_date=_parse_date(item.get('regYmd')),
            farm_no=item.get('farmNo')
        )
        registrations.append(registration)
    
    return registrations

def _parse_slaughter_info(items: List[Dict]) -> Optional[SlaughterInfo]:
    """도축 정보 파싱"""
    if not items:
        return None
    
    item = items[0]
    
    return SlaughterInfo(
        slaughter_place_address=item.get('butcheryPlaceAddr'),
        slaughter_place_name=item.get('butcheryPlaceNm'),
        slaughter_date=_parse_date(item.get('butcheryYmd')),
        grade=item.get('gradeNm'),
        marbling_score=item.get('insfat'),
        inspection_result=item.get('inspectPassYn')
    )

def _parse_packaging_info(items: List[Dict]) -> Optional[PackagingInfo]:
    """포장 처리 정보 파싱"""
    if not items:
        return None
    
    item = items[0]
    
    return PackagingInfo(
        processing_place_address=item.get('processPlaceAddr'),
        processing_place_name=item.get('processPlaceNm')
    )

def _parse_vaccination_info(items: List[Dict]) -> Optional[VaccinationInfo]:
    """구제역 백신 정보 파싱"""
    if not items:
        return None
    
    item = items[0]
    
    return VaccinationInfo(
        fmd_injection_days=item.get('injectionDayCnt'),
        fmd_injection_date=_parse_date(item.get('injectionYmd')),
        fmd_vaccine_order=item.get('vaccineorder')
    )

def _parse_health_info(items: List[Dict]) -> Optional[HealthInspectionInfo]:
    """질병 정보 파싱"""
    if not items:
        return None
    
    item = items[0]
    
    return HealthInspectionInfo(
        disease_status=item.get('inspectDesc')
    )

def _parse_brucella_info(items: List[Dict]) -> Optional[BrucellaInfo]:
    """브루셀라 검사 정보 파싱"""
    if not items:
        return None
    
    item = items[0]
    
    # 브루셀라 검사일로부터 경과일 계산
    brucella_days_elapsed = None
    inspection_date = item.get('inspectDt')
    if inspection_date and len(inspection_date) == 8:
        try:
            inspection_datetime = datetime.strptime(inspection_date, '%Y%m%d')
            today = datetime.now()
            delta = today - inspection_datetime
            brucella_days_elapsed = delta.days
        except:
            pass
    
    return BrucellaInfo(
        brucella_inspection_date=_parse_date(inspection_date),
        brucella_result=item.get('inspectYn'),
        brucella_days_elapsed=brucella_days_elapsed
    )

def _parse_tuberculosis_info(items: List[Dict]) -> Optional[TuberculosisInfo]:
    """결핵 검사 정보 파싱"""
    if not items:
        return None
    
    item = items[0]
    
    return TuberculosisInfo(
        tb_inspection_date=_parse_date(item.get('tbcInspectYmd')),
        tb_result=item.get('tbcInspectRsltNm')
    )

def _parse_date(date_str: Optional[str]) -> Optional[str]:
    """YYYYMMDD 형식을 YYYY-MM-DD 형식으로 변환"""
    if not date_str or len(date_str) != 8:
        return None
    
    try:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    except:
        return None

# 빠른 기본정보 확인 엔드포인트
@router.get("/livestock-quick-check/{ear_tag_number}",
            summary="축산물 기본정보 빠른 확인",
            description="""
            이표번호의 유효성과 기본 개체정보만 빠르게 확인합니다.
            
            **조회 정보:**
            - 기본 개체정보 (개체번호, 출생일, 품종, 성별, 개월령 자동계산)
            - 수입 관련 정보 (수입경과월, 수입국가)
            - 농장 식별정보 (농장식별번호, 농장번호)
            - 럼피스킨 최종접종일
            
            **참고사항:**
            - 전체 조회보다 빠른 응답 속도를 제공합니다
            - 기본 개체정보만 필요한 경우 이 엔드포인트를 사용하세요
            - 개월령은 출생일 기준으로 자동 계산됩니다
            
            **사용 시나리오:**
            1. 사용자가 이표번호 입력
            2. 빠른 확인으로 기본정보 표시
            3. 사용자 확인 후 전체정보 조회 진행
            """)
async def quick_livestock_check(
    ear_tag_number: str,
    current_user: dict = Depends(get_current_user)
):
    """빠른 기본정보 확인 - optionNo=1만 조회"""
    try:
        service_key = os.getenv("LIVESTOCK_TRACE_API_DECODING_KEY")
        if not service_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="축산물이력제 API 키가 설정되지 않았습니다"
            )
        
        # 이표번호 검증
        if len(ear_tag_number) != 12 or not ear_tag_number.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이표번호는 12자리 숫자여야 합니다"
            )
        
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        
        # 기본 개체정보만 조회 (가장 빠름)
        basic_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "1")
        
        if not basic_info:
            return {
                "success": False,
                "message": "축산물이력제에서 해당 이표번호의 정보를 찾을 수 없습니다",
                "ear_tag_number": ear_tag_number,
                "is_valid": False
            }
        
        parsed_info = _parse_basic_info(basic_info, ear_tag_number)
        
        return {
            "success": True,
            "message": "기본 정보 확인 완료",
            "ear_tag_number": ear_tag_number,
            "is_valid": True,
            "basic_info": parsed_info,
            "next_step": "전체 정보가 필요하면 /livestock-trace-async/{ear_tag_number} 호출"
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기본 정보 확인 중 오류가 발생했습니다: {str(e)}"
        )

# 비동기 전체정보 조회 (백그라운드 처리)
@router.post("/livestock-trace-async/{ear_tag_number}",
             summary="축산물이력정보 비동기 전체 조회",
             description="""
             전체 이력정보를 백그라운드에서 조회합니다.
             
             **처리 방식:**
             1. 즉시 task_id 반환
             2. 백그라운드에서 전체 데이터 수집
             3. /livestock-trace-status/{task_id}로 진행상황 확인
             """)
async def async_livestock_trace_info(
    ear_tag_number: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """비동기 전체정보 조회"""
    import uuid
    
    # 이표번호 검증
    if len(ear_tag_number) != 12 or not ear_tag_number.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이표번호는 12자리 숫자여야 합니다"
        )
    
    task_id = str(uuid.uuid4())
    
    # 백그라운드 작업 시작
    background_tasks.add_task(
        _process_full_livestock_data, 
        task_id, 
        ear_tag_number
    )
    
    return {
        "success": True,
        "message": "전체 정보 조회를 시작했습니다",
        "task_id": task_id,
        "ear_tag_number": ear_tag_number,
        "status": "processing",
        "check_status_url": f"/api/livestock-trace-status/{task_id}"
    }

# 작업 상태 확인
@router.get("/livestock-trace-status/{task_id}",
            summary="축산물이력정보 조회 상태 확인",
            description="비동기 조회 작업의 진행상황과 결과를 확인합니다.")
async def get_livestock_trace_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """조회 작업 상태 확인"""
    # 메모리에 저장된 작업 결과 확인 (실제로는 Redis나 DB 사용 권장)
    if task_id in _task_results:
        return _task_results[task_id]
    
    return {
        "success": False,
        "message": "해당 작업을 찾을 수 없습니다",
        "task_id": task_id,
        "status": "not_found"
    }

# 작업 결과 저장을 위한 메모리 딕셔너리 (실제로는 Redis 사용 권장)
_task_results = {}

async def _process_full_livestock_data(task_id: str, ear_tag_number: str):
    """백그라운드에서 전체 데이터 처리"""
    try:
        # 진행상황 업데이트
        _task_results[task_id] = {
            "success": True,
            "status": "processing",
            "message": "전체 정보를 수집 중입니다...",
            "progress": 10,
            "ear_tag_number": ear_tag_number
        }
        
        service_key = os.getenv("LIVESTOCK_TRACE_API_DECODING_KEY")
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        
        response_data = LivestockTraceResponse(
            success=True,
            message="축산물이력정보 조회 완료",
            ear_tag_number=ear_tag_number,
            farm_registrations=[]
        )
        
        # 1. 기본 개체정보 (20%)
        basic_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "1")
        if basic_info:
            response_data.basic_info = _parse_basic_info(basic_info, ear_tag_number)
        
        _task_results[task_id]["progress"] = 20
        _task_results[task_id]["message"] = "기본 정보 수집 완료"
        
        # 2. 농장 등록 정보 (40%)
        farm_registrations = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "2")
        if farm_registrations:
            response_data.farm_registrations = _parse_farm_registrations(farm_registrations)
        
        _task_results[task_id]["progress"] = 40
        _task_results[task_id]["message"] = "농장 정보 수집 완료"
        
        # 3-7. 나머지 정보들 (각각 실패해도 계속 진행)
        option_names = {
            "3": ("도축 정보", 60),
            "4": ("포장 정보", 70), 
            "5": ("백신 정보", 80),
            "6": ("질병 정보", 90),
            "7": ("검사 정보", 100)
        }
        
        for option_no, (name, progress) in option_names.items():
            try:
                info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, option_no)
                if info:
                    if option_no == "3":
                        response_data.slaughter_info = _parse_slaughter_info(info)
                    elif option_no == "4":
                        response_data.packaging_info = _parse_packaging_info(info)
                    elif option_no == "5":
                        response_data.vaccination_info = _parse_vaccination_info(info)
                    elif option_no == "6":
                        response_data.health_inspection = _parse_health_info(info)
                    elif option_no == "7":
                        response_data.brucella_info = _parse_brucella_info(info)
                        response_data.tuberculosis_info = _parse_tuberculosis_info(info)
                
                _task_results[task_id]["progress"] = progress
                _task_results[task_id]["message"] = f"{name} 수집 완료"
                
            except Exception as e:
                print(f"Option {option_no} 조회 실패: {str(e)} - 계속 진행")
                continue
        
        # 최종 결과 저장
        _task_results[task_id] = {
            "success": True,
            "status": "completed",
            "message": "전체 정보 수집 완료",
            "progress": 100,
            "data": response_data,
            "ear_tag_number": ear_tag_number
        }
        
    except Exception as e:
        _task_results[task_id] = {
            "success": False,
            "status": "failed", 
            "message": f"오류가 발생했습니다: {str(e)}",
            "progress": 0,
            "error": str(e),
            "ear_tag_number": ear_tag_number
        }

# ===== 개발/테스트용 인증 없는 엔드포인트 =====

@router.get("/test-quick-check-no-auth/{ear_tag_number}",
            summary="개발 테스트용 빠른 기본정보 확인 (인증 없음)",
            description="개발/테스트용 - 인증 없이 기본정보만 빠르게 확인합니다.")
async def test_quick_check_no_auth(ear_tag_number: str):
    """개발 테스트용 - 인증 없는 빠른 기본정보 확인"""
    try:
        service_key = os.getenv("LIVESTOCK_TRACE_API_DECODING_KEY")
        if not service_key:
            return {
                "success": False,
                "message": "축산물이력제 API 키가 설정되지 않았습니다",
                "ear_tag_number": ear_tag_number,
                "test_mode": True
            }
        
        # 이표번호 검증
        if len(ear_tag_number) != 12 or not ear_tag_number.isdigit():
            return {
                "success": False,
                "message": "이표번호는 12자리 숫자여야 합니다",
                "ear_tag_number": ear_tag_number,
                "test_mode": True
            }
        
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        
        # 기본 개체정보만 조회 (가장 빠름)
        basic_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "1")
        
        if not basic_info:
            return {
                "success": False,
                "message": "축산물이력제에서 해당 이표번호의 정보를 찾을 수 없습니다 (테스트 모드)",
                "ear_tag_number": ear_tag_number,
                "is_valid": False,
                "test_mode": True
            }
        
        parsed_info = _parse_basic_info(basic_info, ear_tag_number)
        
        return {
            "success": True,
            "message": "기본 정보 확인 완료 (테스트 모드)",
            "ear_tag_number": ear_tag_number,
            "is_valid": True,
            "basic_info": parsed_info,
            "test_mode": True,
            "next_step": "전체 정보가 필요하면 /test-async-no-auth/{ear_tag_number} 호출"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"기본 정보 확인 중 오류가 발생했습니다: {str(e)}",
            "ear_tag_number": ear_tag_number,
            "test_mode": True,
            "error_details": str(e)
        }

@router.post("/test-async-no-auth/{ear_tag_number}",
             summary="개발 테스트용 비동기 전체 조회 (인증 없음)",
             description="""
             **개발/테스트 전용** - 인증 없이 전체 이력정보를 비동기로 조회합니다.
             
             **작동 방식:**
             1. 즉시 task_id 반환 (응답 시간: ~100ms)
             2. 백그라운드에서 7개 옵션 순차 조회 (소요 시간: 10-30초)
             3. /test-status-no-auth/{task_id}로 진행상황 실시간 확인
             
             **장점:**
             - 사용자는 즉시 다른 작업 가능
             - 일부 API 실패해도 나머지 정보 수집 계속
             - 실시간 진행률 표시 가능
             """)
async def test_async_livestock_trace_no_auth(
    ear_tag_number: str,
    background_tasks: BackgroundTasks
):
    """개발 테스트용 - 인증 없는 비동기 전체정보 조회"""
    import uuid
    
    # 이표번호 검증
    if len(ear_tag_number) != 12 or not ear_tag_number.isdigit():
        return {
            "success": False,
            "message": "이표번호는 12자리 숫자여야 합니다",
            "ear_tag_number": ear_tag_number,
            "test_mode": True
        }
    
    task_id = str(uuid.uuid4())
    
    # 백그라운드 작업 시작
    background_tasks.add_task(
        _process_full_livestock_data_test, 
        task_id, 
        ear_tag_number
    )
    
    return {
        "success": True,
        "message": "전체 정보 조회를 시작했습니다 (테스트 모드)",
        "task_id": task_id,
        "ear_tag_number": ear_tag_number,
        "status": "processing",
        "test_mode": True,
        "check_status_url": f"/api/livestock-trace/test-status-no-auth/{task_id}",
        "how_to_check": f"GET /api/livestock-trace/test-status-no-auth/{task_id} 를 호출해서 진행상황 확인"
    }

@router.get("/test-status-no-auth/{task_id}",
            summary="개발 테스트용 작업 상태 확인 (인증 없음)",
            description="""
            비동기 조회 작업의 진행상황과 결과를 확인합니다.
            
            **응답 상태:**
            - processing: 진행 중 (progress: 0-100)
            - completed: 완료 (data 포함)
            - failed: 실패 (error 포함)
            - not_found: 작업 없음
            """)
async def test_get_livestock_trace_status_no_auth(task_id: str):
    """개발 테스트용 - 조회 작업 상태 확인"""
    # 메모리에 저장된 작업 결과 확인
    if task_id in _task_results:
        result = _task_results[task_id].copy()
        result["test_mode"] = True
        return result
    
    return {
        "success": False,
        "message": "해당 작업을 찾을 수 없습니다",
        "task_id": task_id,
        "status": "not_found",
        "test_mode": True
    }

async def _process_full_livestock_data_test(task_id: str, ear_tag_number: str):
    """테스트용 백그라운드에서 전체 데이터 처리"""
    try:
        # 진행상황 업데이트
        _task_results[task_id] = {
            "success": True,
            "status": "processing",
            "message": "전체 정보를 수집 중입니다... (테스트 모드)",
            "progress": 10,
            "ear_tag_number": ear_tag_number,
            "test_mode": True,
            "start_time": datetime.now().isoformat()
        }
        
        service_key = os.getenv("LIVESTOCK_TRACE_API_DECODING_KEY")
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        
        response_data = LivestockTraceResponse(
            success=True,
            message="축산물이력정보 조회 완료 (테스트 모드)",
            ear_tag_number=ear_tag_number,
            farm_registrations=[]
        )
        
        # 1. 기본 개체정보 (20%)
        basic_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "1")
        if basic_info:
            response_data.basic_info = _parse_basic_info(basic_info, ear_tag_number)
        
        _task_results[task_id]["progress"] = 20
        _task_results[task_id]["message"] = "기본 정보 수집 완료 (테스트 모드)"
        
        # 2. 농장 등록 정보 (40%)
        farm_registrations = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "2")
        if farm_registrations:
            response_data.farm_registrations = _parse_farm_registrations(farm_registrations)
        
        _task_results[task_id]["progress"] = 40
        _task_results[task_id]["message"] = "농장 정보 수집 완료 (테스트 모드)"
        
        # 3-7. 나머지 정보들 (각각 실패해도 계속 진행)
        option_names = {
            "3": ("도축 정보", 60),
            "4": ("포장 정보", 70), 
            "5": ("백신 정보", 80),
            "6": ("질병 정보", 90),
            "7": ("검사 정보", 100)
        }
        
        collected_info = {}
        
        for option_no, (name, progress) in option_names.items():
            try:
                print(f"[테스트] {name} 수집 시작... (옵션 {option_no})")
                info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, option_no)
                
                if info:
                    if option_no == "3":
                        response_data.slaughter_info = _parse_slaughter_info(info)
                        collected_info["slaughter"] = "수집됨"
                    elif option_no == "4":
                        response_data.packaging_info = _parse_packaging_info(info)
                        collected_info["packaging"] = "수집됨"
                    elif option_no == "5":
                        response_data.vaccination_info = _parse_vaccination_info(info)
                        collected_info["vaccination"] = "수집됨"
                    elif option_no == "6":
                        response_data.health_inspection = _parse_health_info(info)
                        collected_info["health"] = "수집됨"
                    elif option_no == "7":
                        response_data.brucella_info = _parse_brucella_info(info)
                        response_data.tuberculosis_info = _parse_tuberculosis_info(info)
                        collected_info["brucella"] = "수집됨"
                        collected_info["tuberculosis"] = "수집됨"
                else:
                    collected_info[name] = "데이터 없음"
                
                _task_results[task_id]["progress"] = progress
                _task_results[task_id]["message"] = f"{name} 수집 완료 (테스트 모드)"
                _task_results[task_id]["collected_info"] = collected_info
                
                print(f"[테스트] {name} 수집 완료 ({progress}%)")
                
            except Exception as e:
                print(f"[테스트] Option {option_no} 조회 실패: {str(e)} - 계속 진행")
                collected_info[name] = f"수집 실패: {str(e)}"
                continue
        
        # 최종 결과 저장
        _task_results[task_id] = {
            "success": True,
            "status": "completed",
            "message": "전체 정보 수집 완료 (테스트 모드)",
            "progress": 100,
            "data": response_data,
            "ear_tag_number": ear_tag_number,
            "test_mode": True,
            "collected_info": collected_info,
            "end_time": datetime.now().isoformat()
        }
        
        print(f"[테스트] 비동기 작업 완료 - task_id: {task_id}")
        
    except Exception as e:
        _task_results[task_id] = {
            "success": False,
            "status": "failed", 
            "message": f"오류가 발생했습니다: {str(e)} (테스트 모드)",
            "progress": 0,
            "error": str(e),
            "ear_tag_number": ear_tag_number,
            "test_mode": True,
            "end_time": datetime.now().isoformat()
        }
        print(f"[테스트] 비동기 작업 실패 - task_id: {task_id}, error: {str(e)}")

@router.get("/test-no-auth/{ear_tag_number}",
            summary="개발 테스트용 축산물이력정보 조회 (인증 없음)",
            description="""
            **개발/테스트 전용 엔드포인트** - 인증 없이 축산물이력정보를 조회할 수 있습니다.
            
            **주의사항:**
            - 이 엔드포인트는 개발 및 테스트 목적으로만 사용해야합니다.
            - 프로덕션 환경에서는 인증이 필요한 정식 엔드포인트를 사용헤야합니다.
            
            **조회 정보:**
            - 기본 개체정보 (이표번호, 출생일, 품종, 성별, 개월령 자동계산)
            - 농장 등록 정보 (사육지, 농장경영자, 신고이력)
            - 도축 및 포장 처리 정보
            - 구제역/럼피스킨 백신 접종 정보
            - 브루셀라/결핵 검사 정보
            """)
async def test_livestock_trace_no_auth(ear_tag_number: str):
    """개발 테스트용 - 인증 없는 축산물이력정보 조회"""
    try:
        service_key = os.getenv("LIVESTOCK_TRACE_API_DECODING_KEY")
        if not service_key:
            return {
                "success": False,
                "message": "축산물이력제 API 키가 설정되지 않았습니다",
                "ear_tag_number": ear_tag_number,
                "test_mode": True
            }
        
        # 이표번호 검증
        if len(ear_tag_number) != 12 or not ear_tag_number.isdigit():
            return {
                "success": False,
                "message": "이표번호는 12자리 숫자여야 합니다",
                "ear_tag_number": ear_tag_number,
                "test_mode": True
            }
        
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        
        # 응답 데이터 초기화
        response_data = {
            "success": True,
            "message": "축산물이력정보 조회 완료 (테스트 모드)",
            "ear_tag_number": ear_tag_number,
            "test_mode": True,
            "farm_registrations": []
        }
        
        # 1. 기본 개체정보 조회 (optionNo=1)
        basic_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "1")
        if basic_info:
            response_data["basic_info"] = _parse_basic_info(basic_info, ear_tag_number)
        else:
            response_data["basic_info"] = None
        
        # 2. 출생 등 신고정보 조회 (optionNo=2)
        farm_registrations = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "2")
        if farm_registrations:
            response_data["farm_registrations"] = _parse_farm_registrations(farm_registrations)
        
        # 3. 도축정보 조회 (optionNo=3)
        slaughter_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "3")
        if slaughter_info:
            response_data["slaughter_info"] = _parse_slaughter_info(slaughter_info)
        else:
            response_data["slaughter_info"] = None
        
        # 4. 포장정보 조회 (optionNo=4)
        packaging_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "4")
        if packaging_info:
            response_data["packaging_info"] = _parse_packaging_info(packaging_info)
        else:
            response_data["packaging_info"] = None
        
        # 5. 구제역백신 정보 조회 (optionNo=5)
        vaccination_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "5")
        if vaccination_info:
            response_data["vaccination_info"] = _parse_vaccination_info(vaccination_info)
        else:
            response_data["vaccination_info"] = None
        
        # 6. 질병정보 조회 (optionNo=6)
        health_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "6")
        if health_info:
            response_data["health_inspection"] = _parse_health_info(health_info)
        else:
            response_data["health_inspection"] = None
        
        # 7. 브루셀라 정보 조회 (optionNo=7)
        brucella_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "7")
        if brucella_info:
            response_data["brucella_info"] = _parse_brucella_info(brucella_info)
            response_data["tuberculosis_info"] = _parse_tuberculosis_info(brucella_info)
        else:
            response_data["brucella_info"] = None
            response_data["tuberculosis_info"] = None
        
        # 검색 결과가 없는 경우
        if not response_data["basic_info"]:
            response_data["success"] = False
            response_data["message"] = "축산물이력제에서 해당 이표번호의 정보를 찾을 수 없습니다 (테스트 모드)"
        
        return response_data
        
    except Exception as e:
        return {
            "success": False,
            "message": f"축산물이력정보 조회 중 오류가 발생했습니다: {str(e)}",
            "ear_tag_number": ear_tag_number,
            "test_mode": True,
            "error_details": str(e)
        }

@router.get("/test-basic-no-auth/{ear_tag_number}",
            summary="개발 테스트용 기본 정보 조회 (인증 없음)",
            description="개발/테스트용 - 인증 없이 기본 개체정보만 빠르게 조회합니다.")
async def test_basic_livestock_info_no_auth(ear_tag_number: str):
    """개발 테스트용 - 인증 없는 기본 개체정보 조회"""
    try:
        service_key = os.getenv("LIVESTOCK_TRACE_API_DECODING_KEY")
        if not service_key:
            return {
                "success": False,
                "message": "축산물이력제 API 키가 설정되지 않았습니다",
                "ear_tag_number": ear_tag_number,
                "test_mode": True
            }
        
        # 이표번호 검증
        if len(ear_tag_number) != 12 or not ear_tag_number.isdigit():
            return {
                "success": False,
                "message": "이표번호는 12자리 숫자여야 합니다",
                "ear_tag_number": ear_tag_number,
                "test_mode": True
            }
        
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        
        # 기본 개체정보만 조회
        basic_info = await _fetch_livestock_data(base_url, service_key, ear_tag_number, "1")
        
        if not basic_info:
            return {
                "success": False,
                "message": "축산물이력제에서 해당 이표번호의 정보를 찾을 수 없습니다 (테스트 모드)",
                "ear_tag_number": ear_tag_number,
                "test_mode": True
            }
        
        parsed_info = _parse_basic_info(basic_info, ear_tag_number)
        
        return {
            "success": True,
            "message": "기본 정보 조회 완료 (테스트 모드)",
            "ear_tag_number": ear_tag_number,
            "basic_info": parsed_info,
            "test_mode": True
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"기본 정보 조회 중 오류가 발생했습니다: {str(e)}",
            "ear_tag_number": ear_tag_number,
            "test_mode": True,
            "error_details": str(e)
        }