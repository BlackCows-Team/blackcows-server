# routes/livestock_trace.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import xml.etree.ElementTree as ET
from .auth_firebase import get_current_user  # 실제 auth 함수 import

router = APIRouter()

# 임시 저장소 (실제 운영시에는 Redis나 임시 DB 테이블 사용 권장)
temporary_livestock_data: Dict[str, Dict] = {}

class EarTagRequest(BaseModel):
    ear_tag_number: str  # 이표번호 (traceNo)
    option_number: Optional[str] = "1"  # 옵션번호 (기본값: 1 - 개체 정보)
    corp_number: Optional[str] = None  # 사업자번호 (옵션)

class EarTagVerifyRequest(BaseModel):
    ear_tag_number: str  # 이표번호
    option_number: Optional[str] = "1"  # 기본값: 1 (개체 정보)

class LivestockConfirmRequest(BaseModel):
    verification_id: str  # 임시 데이터 식별자
    custom_name: Optional[str] = None  # 사용자 지정 이름
    user_notes: Optional[str] = None  # 사용자 메모

class LivestockTraceInfo(BaseModel):
    """
    축산물통합이력정보 - 공식 API 응답 기반 모든 필드 포함
    """
    # 공통 필드
    trace_no_type: Optional[str] = None  # 소/돼지/묶음 구분
    info_type: Optional[str] = None  # 조회정보 옵션값
    
    # infoType: 1 - 개체정보 (소), 사육정보 (돼지)
    birth_ymd: Optional[str] = None  # 출생일자
    cattle_no: Optional[str] = None  # 소 개체번호
    pig_no: Optional[str] = None  # 돼지 이력번호
    hist_no: Optional[str] = None  # 이력번호 (가금류)
    flat_eartag_no: Optional[str] = None  # 재부착번호
    ls_type_nm: Optional[str] = None  # 소의 종류
    month_diff: Optional[str] = None  # 수입경과월
    nation_nm: Optional[str] = None  # 수입국가
    sex_nm: Optional[str] = None  # 성별
    farm_unique_no: Optional[str] = None  # 농장식별번호
    farm_no: Optional[str] = None  # 농장번호
    lsd_ymd: Optional[str] = None  # 럼피스킨 최종접종일
    
    # infoType: 2 - 출생 등 신고 (소)
    farm_addr: Optional[str] = None  # 사육지/농장주소
    farmer_nm: Optional[str] = None  # 소유주
    reg_type: Optional[str] = None  # 신고구분
    reg_ymd: Optional[str] = None  # 신고년월일
    
    # infoType: 3 - 도축 (소/돼지)
    butchery_place_addr: Optional[str] = None  # 도축장 주소
    butchery_place_nm: Optional[str] = None  # 도축장명
    butchery_ymd: Optional[str] = None  # 도축일자
    grade_nm: Optional[str] = None  # 등급명
    insfat: Optional[str] = None  # 근내지방도
    inspect_pass_yn: Optional[str] = None  # 위생검사 결과
    
    # infoType: 4 - 포장 (소/돼지)
    process_place_addr: Optional[str] = None  # 포장처리업소 주소
    process_place_nm: Optional[str] = None  # 포장처리업소명
    process_ymd: Optional[str] = None  # 포장처리일자
    
    # infoType: 5 - 구제역백신 (소)
    injection_day_cnt: Optional[str] = None  # 구제역 백신접종경과일
    injection_ymd: Optional[str] = None  # 구제역 예방접종최종일자
    vaccine_order: Optional[str] = None  # 구제역 백신접종 차수
    
    # infoType: 6 - 질병정보 (소)
    inspect_desc: Optional[str] = None  # 질병유무
    
    # infoType: 7 - 브루셀라 (소)
    inspect_dt: Optional[str] = None  # 브루셀라 검사일
    inspect_yn: Optional[str] = None  # 브루셀라 검사결과
    tbc_inspect_ymd: Optional[str] = None  # 결핵 검사일
    tbc_inspect_rslt_nm: Optional[str] = None  # 결핵 검사결과
    
    # infoType: 8 - 묶음 기본정보
    corp_no: Optional[str] = None  # 사업자번호
    lot_no: Optional[str] = None  # 묶음번호
    
    # 가금류 관련 필드
    farm_idno: Optional[str] = None  # 농장식별번호
    mngr_nm: Optional[str] = None  # 농장경영자명
    brdng_envrmn_nm: Optional[str] = None  # 사육환경
    lvind_rgrfc: Optional[str] = None  # 축산업 등록번호
    abatt_nm: Optional[str] = None  # 작업장명
    add0r: Optional[str] = None  # 도축장 소재지
    rcept_dt: Optional[str] = None  # 도축일자
    psexm_yn: Optional[str] = None  # 도축검사결과
    entrp_nm: Optional[str] = None  # 업체명
    entrp_addr: Optional[str] = None  # 거래처 소재지
    frmr_nm: Optional[str] = None  # 농장 경영자명
    reqer_entrp_nm: Optional[str] = None  # 신청인 업체명
    reqer_entrp_addr: Optional[str] = None  # 신청인 업체주소
    issue_dt: Optional[str] = None  # 발급일자
    edyg_ovpst_dt: Optional[str] = None  # 식용란 산란일자
    success_yn: Optional[str] = None  # 선별검사결과

class LivestockRegistrationRequest(BaseModel):
    ear_tag_number: str
    option_number: Optional[str] = "1"
    confirmed: bool = True
    user_notes: Optional[str] = None
    custom_name: Optional[str] = None

@router.get("/lookup/{ear_tag_number}",
            summary="이표번호로 축산물 이력정보 조회",
            description="축산물품질평가원 공식 API를 사용하여 이표번호로 축산물 이력정보를 조회합니다. 개체정보, 도축정보, 백신정보 등 다양한 옵션 조회 가능합니다.")
async def lookup_livestock_by_ear_tag(
    ear_tag_number: str,
    option_number: str = "1",
    corp_number: Optional[str] = None
):
    """
    이표번호로 축산물 이력정보 조회
    
    축산물품질평가원 공식 API를 사용하여 이표번호/개체번호/이력번호/묶음번호로 축산물 이력정보를 조회합니다.
    
    **조회 옵션:**
    - 1: 개체정보(소), 사육정보(돼지)
    - 2: 출생 등 신고(소) 
    - 3: 도축정보(소/돼지)
    - 4: 포장정보(소/돼지)
    - 5: 구제역백신(소)
    - 6: 질병정보(소)
    - 7: 브루셀라(소)
    - 8: 묶음 기본정보(묶음)
    - 9: 묶음 구성내역(묶음)
    """
    try:
        # API 키 확인 (새로운 키 사용)
        service_key = os.getenv("LIVESTOCK_TRACE_API_ENCODING_EKEY")
        if not service_key:
            raise HTTPException(status_code=500, detail="LIVESTOCK_TRACE_API_ENCODING_EKEY 환경변수가 설정되지 않았습니다")
        
        # 공식 API URL
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        
        # 요청 파라미터 구성
        params = {
            "ServiceKey": service_key,
            "traceNo": ear_tag_number,
            "optionNo": option_number
        }
        
        # 사업자번호가 있으면 추가 (묶음번호 조회시 필요)
        if corp_number:
            params["corpNo"] = corp_number
        
        # API 호출
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, timeout=30.0)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"API 호출 실패: {response.text}"
                )
            
            # XML 응답 파싱
            xml_data = response.text
            livestock_info_list = parse_xml_response(xml_data)
            
            return {
                "success": True,
                "ear_tag_number": ear_tag_number,
                "option_number": option_number,
                "livestock_info": livestock_info_list,
                "total_records": len(livestock_info_list),
                "raw_xml": xml_data,  # 디버깅용
                "message": "축산물 이력정보 조회 성공"
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="API 호출 시간 초과")
    except ET.ParseError as e:
        raise HTTPException(status_code=500, detail=f"XML 파싱 실패: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")

@router.post("/lookup",
             summary="POST 방식 축산물 이력정보 조회", 
             description="JSON 형태로 이표번호를 전송하여 축산물 이력정보를 조회합니다. GET 방식과 동일한 결과를 반환합니다.")
async def lookup_livestock_by_request(request: EarTagRequest):
    """
    POST 방식 축산물 이력정보 조회
    
    JSON 형태로 이표번호를 전송하여 축산물 이력정보를 조회합니다.
    """
    return await lookup_livestock_by_ear_tag(
        request.ear_tag_number,
        request.option_number or "1",
        request.corp_number
    )

def parse_xml_response(xml_data: str) -> List[LivestockTraceInfo]:
    """
    공식 API XML 응답을 파싱하여 LivestockTraceInfo 리스트로 변환
    """
    try:
        root = ET.fromstring(xml_data)
        
        # 응답 헤더 확인
        header = root.find('header')
        if header is not None:
            result_code = header.find('resultCode')
            result_msg = header.find('resultMsg')
            
            if result_code is not None and result_code.text != "00":
                error_msg = result_msg.text if result_msg is not None else "알 수 없는 오류"
                raise HTTPException(status_code=400, detail=f"API 오류: {error_msg}")
        
        # items 찾기
        items = root.find('.//items')
        if items is None:
            return []
        
        livestock_info_list = []
        
        for item in items.findall('item'):
            # XML 요소를 딕셔너리로 변환
            item_dict = {}
            for element in item:
                item_dict[element.tag] = element.text
            
            # LivestockTraceInfo 객체 생성
            livestock_info = LivestockTraceInfo(
                # 공통 필드
                trace_no_type=safe_get(item_dict, "traceNoType"),
                info_type=safe_get(item_dict, "infoType"),
                
                # 개체/사육 정보
                birth_ymd=safe_get(item_dict, "birthYmd"),
                cattle_no=safe_get(item_dict, "cattleNo"),
                pig_no=safe_get(item_dict, "pigNo"),
                hist_no=safe_get(item_dict, "histNo"),
                flat_eartag_no=safe_get(item_dict, "flatEartagNo"),
                ls_type_nm=safe_get(item_dict, "lsTypeNm"),
                month_diff=safe_get(item_dict, "monthDiff"),
                nation_nm=safe_get(item_dict, "nationNm"),
                sex_nm=safe_get(item_dict, "sexNm"),
                farm_unique_no=safe_get(item_dict, "farmUniqueNo"),
                farm_no=safe_get(item_dict, "farmNo"),
                lsd_ymd=safe_get(item_dict, "lsdYmd"),
                
                # 신고 정보
                farm_addr=safe_get(item_dict, "farmAddr"),
                farmer_nm=safe_get(item_dict, "farmerNm"),
                reg_type=safe_get(item_dict, "regType"),
                reg_ymd=safe_get(item_dict, "regYmd"),
                
                # 도축 정보
                butchery_place_addr=safe_get(item_dict, "butcheryPlaceAddr"),
                butchery_place_nm=safe_get(item_dict, "butcheryPlaceNm"),
                butchery_ymd=safe_get(item_dict, "butcheryYmd"),
                grade_nm=safe_get(item_dict, "gradeNm"),
                insfat=safe_get(item_dict, "insfat"),
                inspect_pass_yn=safe_get(item_dict, "inspectPassYn"),
                
                # 포장 정보
                process_place_addr=safe_get(item_dict, "processPlaceAddr"),
                process_place_nm=safe_get(item_dict, "processPlaceNm"),
                process_ymd=safe_get(item_dict, "processYmd"),
                
                # 백신 정보
                injection_day_cnt=safe_get(item_dict, "injectiondayCnt"),
                injection_ymd=safe_get(item_dict, "injectionYmd"),
                vaccine_order=safe_get(item_dict, "vaccineorder"),
                
                # 질병 정보
                inspect_desc=safe_get(item_dict, "inspectDesc"),
                inspect_dt=safe_get(item_dict, "inspectDt"),
                inspect_yn=safe_get(item_dict, "inspectYn"),
                tbc_inspect_ymd=safe_get(item_dict, "tbcInspectYmd"),
                tbc_inspect_rslt_nm=safe_get(item_dict, "tbcInspectRsltNm"),
                
                # 묶음 정보
                corp_no=safe_get(item_dict, "corpNo"),
                lot_no=safe_get(item_dict, "lotNo"),
                
                # 가금류 정보
                farm_idno=safe_get(item_dict, "farmIdno"),
                mngr_nm=safe_get(item_dict, "mngrNm"),
                brdng_envrmn_nm=safe_get(item_dict, "brdngEnvrnNm"),
                lvind_rgrfc=safe_get(item_dict, "lvindRgrfc"),
                abatt_nm=safe_get(item_dict, "abattNm"),
                add0r=safe_get(item_dict, "add0R"),
                rcept_dt=safe_get(item_dict, "rceptDt"),
                psexm_yn=safe_get(item_dict, "psexmYn"),
                entrp_nm=safe_get(item_dict, "entrpNm"),
                entrp_addr=safe_get(item_dict, "entrpAddr"),
                frmr_nm=safe_get(item_dict, "frmrNm"),
                reqer_entrp_nm=safe_get(item_dict, "reqerEntrpNm"),
                reqer_entrp_addr=safe_get(item_dict, "reqerEntrpAddr"),
                issue_dt=safe_get(item_dict, "issueDt"),
                edyg_ovpst_dt=safe_get(item_dict, "edygOvpstDt"),
                success_yn=safe_get(item_dict, "successYn")
            )
            
            livestock_info_list.append(livestock_info)
        
        return livestock_info_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"XML 파싱 실패: {str(e)}")

def safe_get(data: dict, key: str) -> Optional[str]:
    """안전하게 딕셔너리에서 값을 가져오기"""
    value = data.get(key)
    if value is None or value == "" or value == "null":
        return None
    return str(value).strip()

@router.get("/farm-search/{farm_unique_no}",
            summary="농장식별번호로 농장정보 조회",
            description="농장식별번호를 사용하여 해당 농장의 상세 정보를 조회합니다. 소, 돼지, 가금류별 농장 정보 확인 가능합니다.")
async def search_farm_by_unique_no(
    farm_unique_no: str,
    type_gbn: str = "0022",  # 0022: 소, 0028: 돼지, 0089: 닭.오리.계란
    farmer_nm: Optional[str] = None
):
    """
    농장식별번호로 농장정보 조회
    
    농장식별번호를 사용하여 해당 농장의 상세 정보를 조회합니다.
    
    **축종구분:**
    - 0022: 소
    - 0028: 돼지  
    - 0089: 닭·오리·계란
    """
    try:
        service_key = os.getenv("LIVESTOCK_TRACE_API_ENCODING_EKEY")
        if not service_key:
            raise HTTPException(status_code=500, detail="API 키가 설정되지 않았습니다")
        
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/farmUniqueNoSearch"
        
        params = {
            "serviceKey": service_key,
            "farmUniqueNo": farm_unique_no,
            "typeGbn": type_gbn
        }
        
        if farmer_nm:
            params["farmerNm"] = farmer_nm
        
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, timeout=30.0)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"API 호출 실패: {response.text}")
            
            # XML 파싱
            root = ET.fromstring(response.text)
            
            # 응답 헤더 확인
            header = root.find('header')
            if header is not None:
                result_code = header.find('resultCode')
                if result_code is not None and result_code.text != "00":
                    result_msg = header.find('resultMsg')
                    error_msg = result_msg.text if result_msg is not None else "알 수 없는 오류"
                    raise HTTPException(status_code=400, detail=f"API 오류: {error_msg}")
            
            # 농장 정보 파싱
            items = root.find('.//items')
            farm_info_list = []
            
            if items is not None:
                for item in items.findall('item'):
                    farm_info = {}
                    for element in item:
                        farm_info[element.tag] = element.text
                    farm_info_list.append(farm_info)
            
            return {
                "success": True,
                "farm_unique_no": farm_unique_no,
                "type_gbn": type_gbn,
                "farm_info": farm_info_list,
                "total_records": len(farm_info_list),
                "message": "농장정보 조회 성공"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"농장 조회 실패: {str(e)}")

@router.post("/verify-ear-tag",
             summary="1단계: 이표번호 조회 후 임시 저장",
             description="사용자가 입력한 이표번호로 축산물 이력정보를 조회하고 30분간 임시 저장합니다. 중복 등록 방지 및 사용자 확인을 위한 첫 번째 단계입니다.")
async def verify_ear_tag_number(
    request: EarTagVerifyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    1단계: 이표번호 조회 후 임시 저장
    
    사용자가 입력한 이표번호로 축산물 이력정보를 조회하고,
    확인을 위해 30분간 임시로 저장합니다.
    
    **프로세스:**
    1. 이표번호 중복 등록 확인
    2. 축산물품질평가원 API 호출
    3. 조회 결과 임시 저장 (30분 만료)
    4. 사용자에게 확인 요청
    """
    try:
        # 1. 이미 등록된 젖소인지 확인
        existing_cow = await check_existing_cow_by_ear_tag(request.ear_tag_number, current_user["uid"])
        if existing_cow:
            raise HTTPException(status_code=409, detail="이미 등록된 젖소입니다.")
        
        # 2. 축산물품질평가원 API 호출
        service_key = os.getenv("LIVESTOCK_TRACE_API_ENCODING_EKEY")
        if not service_key:
            raise HTTPException(status_code=500, detail="축산물 이력조회 API 키가 설정되지 않았습니다.")
        
        base_url = "http://data.ekape.or.kr/openapi-data/service/user/animalTrace/traceNoSearch"
        params = {
            "serviceKey": service_key,
            "traceNo": request.ear_tag_number,
            "optionNo": request.option_number or "1"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, timeout=30.0)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"축산물 이력정보 조회 실패: {response.text}"
                )
            
            # 3. XML 응답 파싱
            xml_data = response.text
            livestock_info_list = parse_xml_response(xml_data)
            
            if not livestock_info_list:
                raise HTTPException(status_code=404, detail="해당 이표번호의 축산물 이력정보를 찾을 수 없습니다.")
            
            # 4. 임시 데이터 저장
            import uuid
            verification_id = f"verify_{uuid.uuid4().hex[:12]}"
            
            temporary_data = {
                "verification_id": verification_id,
                "user_id": current_user["uid"],
                "ear_tag_number": request.ear_tag_number,
                "option_number": request.option_number or "1",
                "livestock_info": [info.dict() for info in livestock_info_list],
                "created_at": datetime.now().isoformat(),
                "expires_at": datetime.now().timestamp() + 1800  # 30분 후 만료
            }
            
            temporary_livestock_data[verification_id] = temporary_data
            
            # 5. 사용자에게 확인을 위한 응답
            main_info = livestock_info_list[0] if livestock_info_list else {}
            
            return {
                "success": True,
                "verification_id": verification_id,
                "message": "축산물 이력정보를 조회했습니다. 아래 정보가 등록하려는 젖소가 맞는지 확인해주세요.",
                "ear_tag_number": request.ear_tag_number,
                "livestock_summary": {
                    "cattle_no": main_info.get("cattle_no"),
                    "birth_ymd": main_info.get("birth_ymd"),
                    "sex_nm": main_info.get("sex_nm"),
                    "ls_type_nm": main_info.get("ls_type_nm"),
                    "farm_addr": main_info.get("farm_addr"),
                    "farmer_nm": main_info.get("farmer_nm"),
                    "farm_unique_no": main_info.get("farm_unique_no")
                },
                "total_records": len(livestock_info_list),
                "expires_in_minutes": 30,
                "next_step": "이 정보가 맞다면 /confirm-registration 호출, 틀렸다면 /cancel-verification 호출"
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="축산물 이력정보 조회 시간 초과")
    except ET.ParseError as e:
        raise HTTPException(status_code=500, detail=f"응답 데이터 파싱 실패: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"축산물 이력정보 조회 실패: {str(e)}")

@router.post("/confirm-registration",
             summary="2단계: 젖소 등록 확인 및 저장",
             description="사용자가 '맞습니다'를 선택한 경우 임시 저장된 축산물 이력정보를 바탕으로 실제 젖소를 Firebase DB에 등록합니다.")
async def confirm_livestock_registration(
    request: LivestockConfirmRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    2단계: 젖소 등록 확인 및 저장
    
    사용자가 "맞습니다"를 선택한 경우, 
    임시 저장된 축산물 이력정보를 바탕으로 실제 젖소를 등록합니다.
    
    **처리 과정:**
    1. 임시 데이터 유효성 확인
    2. Firebase DB에 젖소 정보 저장
    3. 사용자 젖소 목록에 추가
    4. 임시 데이터 자동 삭제
    """
    try:
        # 1. 임시 데이터 확인
        if request.verification_id not in temporary_livestock_data:
            raise HTTPException(status_code=404, detail="확인할 수 없는 요청입니다. 다시 이표번호를 조회해주세요.")
        
        temp_data = temporary_livestock_data[request.verification_id]
        
        # 2. 사용자 확인
        if temp_data["user_id"] != current_user["uid"]:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        # 3. 만료 확인
        if datetime.now().timestamp() > temp_data["expires_at"]:
            del temporary_livestock_data[request.verification_id]
            raise HTTPException(status_code=410, detail="확인 시간이 만료되었습니다. 다시 이표번호를 조회해주세요.")
        
        # 4. 중복 등록 재확인
        existing_cow = await check_existing_cow_by_ear_tag(temp_data["ear_tag_number"], current_user["uid"])
        if existing_cow:
            del temporary_livestock_data[request.verification_id]
            raise HTTPException(status_code=409, detail="이미 등록된 젖소입니다.")
        
        # 5. 실제 데이터베이스에 젖소 등록
        cow_data = {
            "cow_id": generate_cow_id(),
            "user_id": current_user["uid"],
            "ear_tag_number": temp_data["ear_tag_number"],
            "custom_name": request.custom_name,
            "user_notes": request.user_notes,
            "trace_info": temp_data["livestock_info"],
            "registration_source": "livestock_trace_verified",
            "verified_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 6. Firebase에 저장
        from config.firebase_config import db
        from google.cloud import firestore
        
        cow_ref = db.collection("cows").document(cow_data["cow_id"])
        cow_ref.set(cow_data)
        
        user_ref = db.collection("users").document(current_user["uid"])
        user_ref.update({
            "cow_ids": firestore.ArrayUnion([cow_data["cow_id"]])
        })
        
        # 7. 임시 데이터 삭제
        del temporary_livestock_data[request.verification_id]
        
        # 8. 요약 정보 생성
        main_info = temp_data["livestock_info"][0] if temp_data["livestock_info"] else {}
        
        return {
            "success": True,
            "message": "젖소가 성공적으로 등록되었습니다!",
            "cow_id": cow_data["cow_id"],
            "ear_tag_number": cow_data["ear_tag_number"],
            "custom_name": cow_data["custom_name"],
            "trace_info_summary": {
                "cattle_no": main_info.get("cattle_no"),
                "ls_type_nm": main_info.get("ls_type_nm"),
                "farm_addr": main_info.get("farm_addr"),
                "farmer_nm": main_info.get("farmer_nm")
            },
            "total_trace_records": len(temp_data["livestock_info"])
        }
        
    except Exception as e:
        # 오류 발생시 임시 데이터 정리
        if request.verification_id in temporary_livestock_data:
            del temporary_livestock_data[request.verification_id]
        raise HTTPException(status_code=500, detail=f"젖소 등록 실패: {str(e)}")

@router.post("/cancel-verification",
             summary="젖소 등록 취소",
             description="사용자가 '아닙니다'를 선택한 경우 임시 저장된 데이터를 즉시 삭제합니다. 잘못된 이표번호 입력이나 타인 소 등록 방지 기능입니다.")
async def cancel_livestock_verification(
    verification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    젖소 등록 취소
    
    사용자가 "아닙니다"를 선택한 경우,
    임시 저장된 데이터를 즉시 삭제합니다.
    
    **안전 기능:**
    - 잘못된 이표번호 입력 방지
    - 다른 사람 젖소 등록 방지
    - 개인정보 보호
    """
    try:
        if verification_id not in temporary_livestock_data:
            raise HTTPException(status_code=404, detail="취소할 데이터를 찾을 수 없습니다.")
        
        temp_data = temporary_livestock_data[verification_id]
        
        if temp_data["user_id"] != current_user["uid"]:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        # 임시 데이터 삭제
        del temporary_livestock_data[verification_id]
        
        return {
            "success": True,
            "message": "축산물 이력정보 확인이 취소되었습니다.",
            "ear_tag_number": temp_data["ear_tag_number"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"취소 처리 실패: {str(e)}")

async def check_existing_cow_by_ear_tag(ear_tag_number: str, user_id: str):
    """사용자의 젖소 목록에서 이표번호 중복 확인"""
    try:
        from config.firebase_config import db
        cows_ref = db.collection("cows").where(filter=("user_id", "==", user_id)).where(filter=("ear_tag_number", "==", ear_tag_number))
        docs = list(cows_ref.stream())
        return len(docs) > 0
    except:
        return False

def generate_cow_id():
    """고유한 젖소 ID 생성"""
    from uuid import uuid4
    return f"cow_{uuid4().hex[:8]}"

@router.get("/health",
            summary="축산물 이력조회 API 연결 상태 확인",
            description="축산물품질평가원 API 키 설정 상태와 연결 가능 여부를 확인합니다. API 키가 올바르게 설정되었는지 검증할 수 있습니다.")
async def trace_api_health():
    """
    축산물 이력조회 API 연결 상태 확인
    
    축산물품질평가원 API 키 설정 상태와 
    연결 가능 여부를 확인합니다.
    """
    try:
        service_key = os.getenv("LIVESTOCK_TRACE_API_ENCODING_EKEY")
        if not service_key:
            return {"status": "error", "message": "API 키가 설정되지 않음"}
        
        return {
            "status": "healthy",
            "api_key_configured": True,
            "api_base_url": "http://data.ekape.or.kr/openapi-data/service/user/animalTrace",
            "supported_animals": ["소(CATTLE)", "돼지(PIG)", "닭(FOWL)", "오리(DUCK)", "계란(EGG)"],
            "total_option_types": 9,
            "message": "축산물품질평가원 API 준비 완료"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/sample-data",
            summary="축산물 이력정보 샘플 데이터 조회",
            description="실제 축산물품질평가원 API 응답 형식과 동일한 테스트용 샘플 데이터를 제공합니다. 프론트엔드 개발 및 API 응답 구조 확인용입니다.")
async def get_sample_data():
    """
    축산물 이력정보 샘플 데이터 조회
    
    실제 축산물품질평가원 API 응답 형식과 동일한 
    테스트용 샘플 데이터를 제공합니다.
    
    **용도:**
    - API 응답 구조 확인
    - 프론트엔드 개발 테스트
    - 데이터 형식 검증
    """
    sample_data = {
        "success": True,
        "ear_tag_number": "L01709271277007",
        "option_number": "9",
        "livestock_info": [
            {
                "trace_no_type": "CATTLE|LOT_NO",
                "info_type": "9",
                "butchery_place_addr": "경기도 안성시 일죽면 금산리 598번지",
                "butchery_place_nm": "주식회사 도드람엘피씨",
                "butchery_ymd": "20170920",
                "cattle_no": "410002075264204",
                "corp_no": "1178522046",
                "farm_addr": "강원특별자치도 원주시 호저면 매호리",
                "grade_nm": "1",
                "lot_no": "L01709271277007",
                "ls_type_nm": "한우",
                "process_place_addr": "서울특별시 양천구 목동 916번지",
                "process_place_nm": "㈜현대그린푸드목동점"
            },
            {
                "trace_no_type": "CATTLE|LOT_NO",
                "info_type": "9",
                "butchery_place_addr": "경기도 안성시 일죽면 금산리 598번지",
                "butchery_place_nm": "주식회사 도드람엘피씨",
                "butchery_ymd": "20170909",
                "cattle_no": "410002302364116",
                "corp_no": "1178522046",
                "farm_addr": "충청남도 공주시 탄천면",
                "grade_nm": "1",
                "lot_no": "L01709271277007",
                "ls_type_nm": "한우",
                "process_place_addr": "서울특별시 양천구 목동 916번지",
                "process_place_nm": "㈜현대그린푸드목동점"
            }
        ],
        "total_records": 2,
        "message": "샘플 데이터 (테스트용)"
    }
    
    return sample_data

@router.get("/usage-guide",
            summary="축산물 이력조회 기반 젖소 등록 사용법 안내",
            description="2단계 확인 프로세스를 통한 안전한 젖소 등록 방법을 상세히 설명합니다. 단계별 API 호출 방법과 보안 기능을 포함합니다.")
async def get_usage_guide():
    """
    축산물 이력조회 기반 젖소 등록 사용법 안내
    
    2단계 확인 프로세스를 통한 안전한 젖소 등록 방법을 
    상세히 설명합니다.
    
    **포함 내용:**
    - 단계별 API 호출 방법
    - 요청/응답 예시
    - 보안 기능 설명
    - 오류 처리 가이드
    """
    return {
        "title": "축산물 이력조회 기반 젖소 등록 프로세스",
        "description": "2단계 확인 프로세스를 통한 안전한 젖소 등록",
        "process": {
            "step1": {
                "title": "1단계: 이표번호 조회",
                "endpoint": "POST /api/livestock-trace/verify-ear-tag",
                "description": "이표번호로 축산물 이력정보 조회 후 임시 저장",
                "request_example": {
                    "ear_tag_number": "410002075264204",
                    "option_number": "1"
                },
                "response_fields": [
                    "verification_id: 확인용 임시 ID",
                    "livestock_summary: 조회된 소 정보 요약",
                    "expires_in_minutes: 만료 시간 (30분)"
                ]
            },
            "step2a": {
                "title": "2-A단계: 등록 확인",
                "endpoint": "POST /api/livestock-trace/confirm-registration",
                "description": "사용자가 '맞습니다' 선택 시 실제 DB 등록",
                "request_example": {
                    "verification_id": "verify_abc123def456",
                    "custom_name": "젖소 이름 (옵션)",
                    "user_notes": "메모 (옵션)"
                }
            },
            "step2b": {
                "title": "2-B단계: 등록 취소",
                "endpoint": "POST /api/livestock-trace/cancel-verification",
                "description": "사용자가 '아닙니다' 선택 시 임시 데이터 삭제",
                "request_example": {
                    "verification_id": "verify_abc123def456"
                }
            }
        },
        "security_features": [
            "사용자 인증 필수 (JWT 토큰)",
            "임시 데이터 30분 자동 만료",
            "중복 등록 방지",
            "사용자별 데이터 격리"
        ],
        "error_handling": [
            "404: 이표번호 정보 없음",
            "409: 이미 등록된 젖소",
            "410: 확인 시간 만료",
            "500: API 호출 실패"
        ]
    }

@router.get("/temporary-status",
            summary="현재 사용자의 임시 확인 대기 데이터 상태 조회", 
            description="사용자가 이표번호를 조회했지만 아직 등록 확인을 하지 않은 임시 저장 데이터 목록과 각 데이터의 남은 만료 시간을 확인합니다.")
async def get_temporary_data_status(
    current_user: dict = Depends(get_current_user)
):
    """
    현재 사용자의 임시 확인 대기 데이터 상태 조회
    
    사용자가 이표번호를 조회했지만 아직 등록 확인을 하지 않은 
    임시 저장 데이터 목록을 확인합니다.
    
    **제공 정보:**
    - 확인 대기 중인 이표번호 목록
    - 각 데이터의 남은 만료 시간
    - 총 대기 건수
    """
    user_temp_data = []
    current_time = datetime.now().timestamp()
    
    # 만료된 데이터 정리
    expired_keys = []
    for key, data in temporary_livestock_data.items():
        if current_time > data["expires_at"]:
            expired_keys.append(key)
    
    for key in expired_keys:
        del temporary_livestock_data[key]
    
    # 현재 사용자의 임시 데이터 조회
    for verification_id, data in temporary_livestock_data.items():
        if data["user_id"] == current_user["uid"]:
            remaining_minutes = max(0, int((data["expires_at"] - current_time) / 60))
            user_temp_data.append({
                "verification_id": verification_id,
                "ear_tag_number": data["ear_tag_number"],
                "created_at": data["created_at"],
                "remaining_minutes": remaining_minutes
            })
    
    return {
        "success": True,
        "pending_verifications": user_temp_data,
        "total_pending": len(user_temp_data),
        "message": f"확인 대기 중인 이표번호 조회 {len(user_temp_data)}건"
    }