# routers/detailed_record.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from schemas.detailed_record import (
    MilkingRecordCreate, EstrusRecordCreate, InseminationRecordCreate,
    PregnancyCheckRecordCreate, CalvingRecordCreate, FeedRecordCreate,
    HealthCheckRecordCreate, VaccinationRecordCreate, WeightRecordCreate,
    TreatmentRecordCreate, DetailedRecordResponse, DetailedRecordSummary, 
    DetailedRecordType, DetailedRecordUpdate
)
from services.detailed_record_service import DetailedRecordService
from routers.auth_firebase import get_current_user

router = APIRouter()

# ===== 착유 기록 =====
@router.post("/milking", 
             response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED,
             summary="착유 기록 생성",
             description="""
             착유 기록을 생성합니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 착유 날짜 (YYYY-MM-DD 형식)
             - milk_yield: 착유량 (리터 단위, 0보다 큰 값)
             
             **선택적 필드:**
             - milking_start_time: 착유 시작 시간
             - milking_end_time: 착유 종료 시간
             - milking_session: 착유 횟수 (1회차, 2회차 등)
             - fat_percentage: 유지방 비율
             - protein_percentage: 유단백 비율
             - somatic_cell_count: 체세포수
             - temperature: 온도
             - conductivity: 전도율
             - 기타 모든 측정 필드들...
             """,
             responses={
                 201: {"description": "착유 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_milking_record(
    record_data: MilkingRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """착유 기록 생성"""
    return DetailedRecordService.create_milking_record(record_data, current_user)

@router.get("/cow/{cow_id}/milking", 
           response_model=List[DetailedRecordSummary],
           summary="젖소별 착유 기록 조회",
           description="특정 젖소의 착유 기록만 필터링하여 조회")
def get_cow_milking_records(
    cow_id: str,
    limit: int = Query(50, description="조회할 기록 수 제한", ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """젖소별 착유 기록 조회"""
    farm_id = current_user.get("farm_id")
    return DetailedRecordService.get_detailed_records_by_cow(
        cow_id, farm_id, DetailedRecordType.MILKING, limit
    )

# 최근 착유 기록 조회 (농장 전체)
@router.get("/milking/recent", 
           response_model=List[DetailedRecordSummary],
           summary="최근 착유 기록 조회",
           description="농장 전체의 최근 착유 기록을 조회")
def get_recent_milking_records(
    limit: int = Query(20, description="조회할 기록 수", ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """최근 착유 기록 조회 (농장 전체)"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 최근 착유 기록만 조회
        records_query = (db.collection('cow_detailed_records')
                        .where('farm_id', '==', farm_id)
                        .where('record_type', '==', DetailedRecordType.MILKING.value)
                        .where('is_active', '==', True)
                        .order_by('record_date', direction='DESCENDING')
                        .limit(limit)
                        .get())
        
        records = []
        for record_doc in records_query:
            record_data = record_doc.to_dict()
            
            # 젖소 정보 조회
            try:
                cow_info = DetailedRecordService._get_cow_info(record_data["cow_id"], farm_id)
                
                # 착유량 정보 추출
                key_values = {}
                if record_data.get("record_data", {}).get("milk_yield"):
                    key_values["milk_yield"] = f"{record_data['record_data']['milk_yield']}L"
                if record_data.get("record_data", {}).get("milking_session"):
                    key_values["session"] = f"{record_data['record_data']['milking_session']}회차"
                if record_data.get("record_data", {}).get("fat_percentage"):
                    key_values["fat"] = f"{record_data['record_data']['fat_percentage']}%"
                
                records.append(DetailedRecordSummary(
                    id=record_data["id"],
                    cow_id=record_data["cow_id"],
                    cow_name=cow_info["name"],
                    cow_ear_tag_number=cow_info["ear_tag_number"],
                    record_type=DetailedRecordType.MILKING,
                    record_date=record_data["record_date"],
                    title=record_data["title"],
                    key_values=key_values,
                    created_at=record_data["created_at"]
                ))
            except:
                # 젖소가 삭제된 경우 등 예외 처리
                continue
        
        return records
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"최근 착유 기록 조회 중 오류가 발생했습니다: {str(e)}"
        )
    
# ===== 발정 기록 =====
@router.post("/estrus", 
             response_model=DetailedRecordResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="발정 기록 생성",
             description="""
             젖소의 발정 상태를 기록합니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 발정 관찰 날짜 (YYYY-MM-DD 형식)
             
             **선택적 필드:**
             - estrus_start_time: 발정 시작 시간 (HH:MM:SS 형식)
             - estrus_intensity: 발정 강도 (약/중/강)
             - estrus_duration: 발정 지속시간 (시간 단위)
             - behavior_signs: 발정 징후 목록 (승가허용, 불안, 울음 등)
             - visual_signs: 육안 관찰 사항 (점액분비, 외음부종 등)
             - detected_by: 발견자 이름
             - detection_method: 발견 방법 (육안관찰/센서감지/기타)
             - next_expected_estrus: 다음 발정 예상일 (YYYY-MM-DD 형식)
             - breeding_planned: 교배 계획 여부 (true/false)
             - notes: 특이사항 및 추가 메모
             """,
             responses={
                 201: {"description": "발정 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_estrus_record(
    record_data: EstrusRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """발정 기록 생성"""
    return DetailedRecordService.create_estrus_record(record_data, current_user)

# ===== 인공수정 기록 =====
@router.post("/insemination", 
             response_model=DetailedRecordResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="인공수정 기록 생성",
             description="""
             젖소의 인공수정 작업을 기록합니다. 정액 정보, 수정시간, 기술자 정보 등을 포함할 수 있습니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 인공수정 실시 날짜 (YYYY-MM-DD 형식)
             
             **선택적 필드:**
             - insemination_time: 수정 시간 (HH:MM:SS 형식)
             - bull_id: 종축(황소) ID
             - bull_breed: 종축 품종 (홀스타인, 한우 등)
             - semen_batch: 정액 로트번호
             - semen_quality: 정액 품질등급 (A급, B급 등)
             - technician_name: 수정사 이름
             - insemination_method: 수정 방법 (직장수정, 질수정 등)
             - cervix_condition: 자궁경관 상태 (양호, 불량 등)
             - success_probability: 성공 예상률 (백분율, 0-100)
             - cost: 수정 비용 (원 단위)
             - pregnancy_check_scheduled: 임신감정 예정일 (YYYY-MM-DD 형식)
             - notes: 특이사항 및 추가 메모
             """,
             responses={
                 201: {"description": "인공수정 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_insemination_record(
    record_data: InseminationRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """인공수정 기록 생성"""
    return DetailedRecordService.create_insemination_record(record_data, current_user)

# ===== 임신감정 기록 =====
@router.post("/pregnancy-check", 
             response_model=DetailedRecordResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="임신감정 기록 생성",
             description="""
             젖소의 임신 여부를 확인한 결과를 기록합니다. 초음파 검사 결과, 예상 분만일 등을 포함할 수 있습니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 임신감정 실시 날짜 (YYYY-MM-DD 형식)
             
             **선택적 필드:**
             - check_method: 감정 방법 (직장검사/초음파검사/혈액검사)
             - check_result: 감정 결과 (임신/비임신/의심)
             - pregnancy_stage: 임신 단계 (일 단위, 수정 후 경과일)
             - fetus_condition: 태아 상태 (정상/이상/확인불가)
             - expected_calving_date: 분만예정일 (YYYY-MM-DD 형식)
             - veterinarian: 검사 수의사명
             - check_cost: 감정비용 (원 단위)
             - next_check_date: 다음 감정일 (YYYY-MM-DD 형식)
             - additional_care: 추가 관리사항 (영양관리, 운동제한 등)
             - notes: 특이사항 및 추가 메모
             """,
             responses={
                 201: {"description": "임신감정 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_pregnancy_check_record(
    record_data: PregnancyCheckRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """임신감정 기록 생성"""
    return DetailedRecordService.create_pregnancy_check_record(record_data, current_user)

# ===== 분만 기록 =====
@router.post("/calving", 
             response_model=DetailedRecordResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="분만 기록 생성",
             description="""
             젖소의 분만 상황을 기록합니다. 분만 일시, 송아지 정보, 분만 과정의 특이사항 등을 포함할 수 있습니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 분만 날짜 (YYYY-MM-DD 형식)
             
             **선택적 필드:**
             - calving_start_time: 분만 시작시간 (HH:MM:SS 형식)
             - calving_end_time: 분만 완료시간 (HH:MM:SS 형식)
             - calving_difficulty: 분만 난이도 (정상/약간어려움/어려움/제왕절개)
             - calf_count: 송아지 수 (1, 2 등)
             - calf_gender: 송아지 성별 목록 (["수컷", "암컷"] 등)
             - calf_weight: 송아지 체중 목록 (kg 단위, [35.5, 40.2] 등)
             - calf_health: 송아지 건강상태 목록 (["정상", "허약"] 등)
             - placenta_expelled: 태반 배출 여부 (true/false)
             - placenta_expulsion_time: 태반 배출 시간 (HH:MM:SS 형식)
             - complications: 합병증 목록 (["난산", "태반정체"] 등)
             - assistance_required: 도움 필요 여부 (true/false)
             - veterinarian_called: 수의사 호출 여부 (true/false)
             - dam_condition: 어미소 상태 (정상/허약/위험)
             - lactation_start: 비유 시작일 (YYYY-MM-DD 형식)
             - notes: 특이사항 및 추가 메모
             """,
             responses={
                 201: {"description": "분만 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_calving_record(
    record_data: CalvingRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """분만 기록 생성"""
    return DetailedRecordService.create_calving_record(record_data, current_user)

# ===== 사료급여 기록 =====
@router.post("/feed", 
             response_model=DetailedRecordResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="사료급여 기록 생성",
             description="""
             젖소의 사료급여 현황을 기록합니다. 사료 종류, 급여량, 급여 시간 등을 포함할 수 있습니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 사료급여 날짜 (YYYY-MM-DD 형식)
             
             **선택적 필드:**
             - feed_time: 급여 시간 (HH:MM:SS 형식)
             - feed_type: 사료 종류 (조사료, 농후사료, 혼합사료 등)
             - feed_amount: 급여량 (kg 단위)
             - feed_quality: 사료 품질 (1등급, 2등급, 특급 등)
             - supplement_type: 첨가제 종류 (비타민, 미네랄, 효소 등)
             - supplement_amount: 첨가제 양 (kg 또는 g 단위)
             - water_consumption: 음수량 (리터 단위)
             - appetite_condition: 식욕 상태 (정상/저하/증가)
             - feed_efficiency: 사료효율 (증체량/사료섭취량)
             - cost_per_feed: 사료비용 (원 단위)
             - fed_by: 급여자 이름
             - notes: 특이사항 및 추가 메모
             """,
             responses={
                 201: {"description": "사료급여 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_feed_record(
    record_data: FeedRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """사료급여 기록 생성"""
    return DetailedRecordService.create_feed_record(record_data, current_user)

# ===== 건강검진 기록 =====
@router.post("/health-check", 
             response_model=DetailedRecordResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="건강검진 기록 생성",
             description="""
             젖소의 건강검진 결과를 기록합니다. 체온, 맥박, 호흡수, 일반건강상태 등을 포함할 수 있습니다. 
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 건강검진 날짜 (YYYY-MM-DD 형식)
             
             **선택적 필드:**
             - check_time: 검진 시간 (HH:MM:SS 형식)
             - body_temperature: 체온 (섭씨 온도, 38.5 등)
             - heart_rate: 심박수 (회/분, 60-80 정상범위)
             - respiratory_rate: 호흡수 (회/분, 15-30 정상범위)
             - body_condition_score: 체형점수 (1-5점 척도)
             - udder_condition: 유방 상태 (정상/부종/염증/상처)
             - hoof_condition: 발굽 상태 (정상/균열/썩음/절뚝거림)
             - coat_condition: 털 상태 (윤기있음/거침/탈모)
             - eye_condition: 눈 상태 (맑음/충혈/분비물)
             - nose_condition: 코 상태 (촉촉함/건조/분비물)
             - appetite: 식욕 상태 (정상/저하/증가/없음)
             - activity_level: 활동성 (활발/보통/둔함/무기력)
             - abnormal_symptoms: 이상 증상 목록 (["기침", "설사"] 등)
             - examiner: 검진자 이름
             - next_check_date: 다음 검진일 (YYYY-MM-DD 형식)
             - notes: 특이사항 및 추가 메모
             """,
             responses={
                 201: {"description": "건강검진 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_health_check_record(
    record_data: HealthCheckRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """건강검진 기록 생성"""
    return DetailedRecordService.create_health_check_record(record_data, current_user)

# ===== 백신접종 기록 =====
@router.post("/vaccination", 
             response_model=DetailedRecordResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="백신접종 기록 생성",
             description="""
             젖소의 백신접종 내역을 기록합니다. 백신 종류, 접종일, 다음접종예정일 등을 포함할 수 있습니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 백신접종 날짜 (YYYY-MM-DD 형식)
             
             **선택적 필드:**
             - vaccination_time: 접종 시간 (HH:MM:SS 형식)
             - vaccine_name: 백신명 (구제역백신, 소유행열백신 등)
             - vaccine_type: 백신 종류 (생백신/사백신/혼합백신)
             - vaccine_batch: 백신 로트번호
             - dosage: 접종량 (ml 단위, 2.0 등)
             - injection_site: 접종 부위 (목, 어깨, 엉덩이 등)
             - injection_method: 접종 방법 (근육주사/피하주사)
             - administrator: 접종자 이름
             - vaccine_manufacturer: 백신 제조사명
             - expiry_date: 백신 유효기간 (YYYY-MM-DD 형식)
             - adverse_reaction: 부작용 발생 여부 (true/false)
             - reaction_details: 부작용 세부사항 (발열, 식욕부진 등)
             - next_vaccination_due: 다음 접종 예정일 (YYYY-MM-DD 형식)
             - cost: 백신 비용 (원 단위)
             - notes: 특이사항 및 추가 메모
             """,
             responses={
                 201: {"description": "백신접종 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_vaccination_record(
    record_data: VaccinationRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """백신접종 기록 생성"""
    return DetailedRecordService.create_vaccination_record(record_data, current_user)

# ===== 체중측정 기록 =====
@router.post("/weight", 
             response_model=DetailedRecordResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="체중측정 기록 생성",
             description="""
             젖소의 체중 측정 결과를 기록합니다. 측정 체중, 측정 방법, 체형점수 등을 포함할 수 있습니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 체중측정 날짜 (YYYY-MM-DD 형식)
             
             **선택적 필드:**
             - measurement_time: 측정 시간 (HH:MM:SS 형식)
             - weight: 체중 (kg 단위, 550.5 등)
             - measurement_method: 측정 방법 (전자저울/체척자/목측)
             - body_condition_score: 체형점수 (1-5점 척도)
             - height_withers: 기갑고 (cm 단위, 어깨 높이)
             - body_length: 체장 (cm 단위, 몸통 길이)
             - chest_girth: 흉위 (cm 단위, 가슴둘레)
             - growth_rate: 증체율 (kg/일 단위)
             - target_weight: 목표체중 (kg 단위)
             - weight_category: 체중 등급 (저체중/정상/과체중)
             - measurer: 측정자 이름
             - notes: 특이사항 및 추가 메모
             """,
             responses={
                 201: {"description": "체중측정 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_weight_record(
    record_data: WeightRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """체중측정 기록 생성"""
    return DetailedRecordService.create_weight_record(record_data, current_user)

# ===== 치료 기록 =====
@router.post("/treatment", 
             response_model=DetailedRecordResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="치료 기록 생성",
             description="""
             젖소의 질병 치료 과정을 기록합니다. 진단명, 처방약, 치료과정, 회복상태 등을 포함할 수 있습니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 치료 날짜 (YYYY-MM-DD 형식)
             
             **선택적 필드:**
             - treatment_time: 치료 시간 (HH:MM:SS 형식)
             - treatment_type: 치료 종류 (약물치료/수술/물리치료 등)
             - symptoms: 증상 목록 (["발열", "설사", "기침"] 등)
             - diagnosis: 진단명 (유방염, 소화불량, 호흡기질환 등)
             - medication_used: 사용약물 목록 (["항생제", "해열제"] 등)
             - dosage_info: 용법용량 정보 ({"항생제": "1일 2회, 5ml"} 등)
             - treatment_method: 치료 방법 (근육주사/정맥주사/경구투여)
             - treatment_duration: 치료 기간 (일 단위)
             - veterinarian: 담당 수의사명
             - treatment_response: 치료 반응 (호전/악화/변화없음)
             - side_effects: 부작용 내용
             - follow_up_required: 추후 관찰 필요 여부 (true/false)
             - follow_up_date: 추후 관찰일 (YYYY-MM-DD 형식)
             - treatment_cost: 치료비용 (원 단위)
             - withdrawal_period: 휴약기간 (일 단위, 우유 폐기 기간)
             - notes: 특이사항 및 추가 메모
             """,
             responses={
                 201: {"description": "치료 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })
def create_treatment_record(
    record_data: TreatmentRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """치료 기록 생성"""
    return DetailedRecordService.create_treatment_record(record_data, current_user)

# ===== 기록 조회 API =====
@router.get("/cow/{cow_id}", 
            response_model=List[DetailedRecordSummary],
            summary="젖소별 상세 기록 목록 조회",
            description="""
            특정 젖소의 모든 상세 기록을 조회합니다. 기록 유형별로 필터링할 수 있습니다.
            
            **기록 유형별 필터링 옵션:**
            
            **기본 관리 기록**
            - `milking`: **착유 기록** - 착유량, 유성분, 착유시간 등
            - `feed`: **사료급여 기록** - 사료종류, 급여량, 급여시간 등
            - `weight`: **체중측정 기록** - 체중, 체형점수, 성장률 등
            
            **건강 관리 기록**
            - `health_check`: **건강검진 기록** - 체온, 맥박, 호흡수, 일반건강상태 등
            - `vaccination`: **백신접종 기록** - 백신명, 접종일, 다음접종예정일 등
            - `treatment`: **치료 기록** - 진단명, 처방약, 치료과정 등
            - `disease`: **질병 기록** - 질병발생, 증상, 치료이력 등
            
            **번식 관리 기록**
            - `estrus`: **발정 기록** - 발정증상, 발정강도, 발정주기 등
            - `insemination`: **인공수정 기록** - 수정일, 정액정보, 수정사 등
            - `pregnancy_check`: **임신감정 기록** - 임신여부, 임신단계, 분만예정일 등
            - `calving`: **분만 기록** - 분만일시, 송아지정보, 분만과정 등
            - `breeding`: **번식 관련 기타 기록**
            
            **특수 관리 기록**
            - `abortion`: **유산 기록** - 유산일, 유산원인, 후속조치 등
            - `dry_off`: **건유 전환 기록** - 건유시작일, 건유기간 등
            - `culling`: **도태 기록** - 도태일, 도태사유, 처리방법 등
            - `status_change`: **상태 변경 기록** - 젖소 상태 변화 이력
            - `other`: **기타 기록** - 위 분류에 속하지 않는 특별한 기록
            
            **사용 예시:**
            - 전체 기록 조회: record_type 파라미터 없이 호출
            - 착유 기록만 조회: `?record_type=milking`
            - 건강 기록만 조회: `?record_type=health_check`
            - 번식 기록만 조회: `?record_type=breeding`
            """)
def get_cow_detailed_records(
    cow_id: str,
    record_type: Optional[DetailedRecordType] = Query(
        None, 
        description="""
        **기록 유형 필터 (선택사항)**
        
        - `milking`: 착유 기록 (착유량, 유성분 등)
        - `feed`: 사료급여 기록 (사료종류, 급여량 등) 
        - `weight`: 체중측정 기록 (체중, 체형점수 등)
        - `health_check`: 건강검진 기록 (체온, 맥박, 일반건강상태 등)
        - `vaccination`: 백신접종 기록 (백신명, 접종일 등)
        - `treatment`: 치료 기록 (진단명, 처방약, 치료과정 등)
        - `estrus`: 발정 기록 (발정증상, 발정주기 등)
        - `insemination`: 인공수정 기록 (수정일, 정액정보 등)
        - `pregnancy_check`: 임신감정 기록 (임신여부, 분만예정일 등)
        - `calving`: 분만 기록 (분만일시, 송아지정보 등)
        - `abortion`: 유산 기록 (유산일, 유산원인 등)
        - `dry_off`: 건유 전환 기록 (건유시작일, 건유기간 등)
        - `culling`: 도태 기록 (도태일, 도태사유 등)
        - `breeding`: 번식 관련 기타 기록
        - `disease`: 질병 기록 (질병발생, 증상, 치료이력 등)
        - `status_change`: 상태 변경 기록 (젖소 상태 변화)
        - `other`: 기타 기록 (특별한 기록사항)
        
        **미입력시 모든 기록 타입을 조회합니다.**
        """
    ),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 상세 기록 목록 조회"""
    farm_id = current_user.get("farm_id")
    return DetailedRecordService.get_detailed_records_by_cow(cow_id, farm_id, record_type)

@router.get("/{record_id}", 
            response_model=DetailedRecordResponse,
            summary="상세 기록 단건 조회",
            description="특정 기록의 상세 정보를 조회합니다. 모든 기록 데이터와 메타데이터를 포함합니다.")
def get_detailed_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """상세 기록 단건 조회"""
    farm_id = current_user.get("farm_id")
    return DetailedRecordService.get_detailed_record_by_id(record_id, farm_id)

@router.delete("/{record_id}",
               summary="상세 기록 삭제",
               description="특정 기록을 완전히 삭제합니다. 삭제된 기록은 복구할 수 없습니다.")
def delete_detailed_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """상세 기록 삭제"""
    return DetailedRecordService.delete_detailed_record(record_id, current_user)

# ===== 통계 및 분석 API =====
@router.get("/cow/{cow_id}/milking/statistics",
            summary="착유 통계 조회",
            description="특정 젖소의 착유 통계를 조회합니다. 일별 착유량, 평균값, 유성분 분석 등을 포함합니다.")
def get_milking_statistics(
    cow_id: str,
    days: int = Query(30, description="조회 기간(일)", ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """착유 통계 조회"""
    try:
        from config.firebase_config import get_firestore_client
        from datetime import datetime, timedelta
        
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 착유 기록 조회
        milking_records = (db.collection('cow_detailed_records')
                          .where(filter=('cow_id', '==', cow_id))
                          .where(filter=('farm_id', '==', farm_id))
                          .where(filter=('record_type', '==', DetailedRecordType.MILKING.value))
                          .where(filter=('is_active', '==', True))
                          .where(filter=('record_date', '>=', start_date.strftime('%Y-%m-%d')))
                          .where(filter=('record_date', '<=', end_date.strftime('%Y-%m-%d')))
                          .get())
        
        total_yield = 0
        total_sessions = 0
        avg_fat = 0
        avg_protein = 0
        fat_count = 0
        protein_count = 0
        daily_yields = {}
        
        for record in milking_records:
            data = record.to_dict()
            record_data = data.get('record_data', {})
            
            # 착유량 합계
            milk_yield = record_data.get('milk_yield', 0)
            total_yield += milk_yield
            total_sessions += 1
            
            # 일별 착유량 집계
            record_date = data.get('record_date')
            if record_date:
                if record_date not in daily_yields:
                    daily_yields[record_date] = 0
                daily_yields[record_date] += milk_yield
            
            # 유지방/유단백 평균 계산
            if record_data.get('fat_percentage'):
                avg_fat += record_data['fat_percentage']
                fat_count += 1
            if record_data.get('protein_percentage'):
                avg_protein += record_data['protein_percentage']
                protein_count += 1
        
        # 평균 계산
        daily_average = total_yield / days if days > 0 else 0
        session_average = total_yield / total_sessions if total_sessions > 0 else 0
        fat_average = avg_fat / fat_count if fat_count > 0 else 0
        protein_average = avg_protein / protein_count if protein_count > 0 else 0
        
        return {
            "cow_id": cow_id,
            "period_days": days,
            "total_milk_yield": round(total_yield, 2),
            "total_sessions": total_sessions,
            "daily_average": round(daily_average, 2),
            "session_average": round(session_average, 2),
            "fat_percentage_avg": round(fat_average, 2),
            "protein_percentage_avg": round(protein_average, 2),
            "daily_yields": daily_yields
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"착유 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/cow/{cow_id}/weight/trend",
            summary="체중 변화 추이 조회",
            description="특정 젖소의 체중 변화 추이를 분석합니다. 기간별 체중 증감을 그래프로 확인할 수 있습니다.")
def get_weight_trend(
    cow_id: str,
    months: int = Query(6, description="조회 기간(월)", ge=1, le=24),
    current_user: dict = Depends(get_current_user)
):
    """체중 변화 추이"""
    try:
        from config.firebase_config import get_firestore_client
        from datetime import datetime, timedelta
        
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # 체중 기록 조회
        weight_records = (db.collection('cow_detailed_records')
                         .where(filter=('cow_id', '==', cow_id))
                         .where(filter=('farm_id', '==', farm_id))
                         .where(filter=('record_type', '==', DetailedRecordType.WEIGHT.value))
                         .where(filter=('is_active', '==', True))
                         .where(filter=('record_date', '>=', start_date.strftime('%Y-%m-%d')))
                         .order_by('record_date')
                         .get())
        
        weights = []
        for record in weight_records:
            data = record.to_dict()
            record_data = data.get('record_data', {})
            
            if record_data.get('weight'):
                weights.append({
                    "date": data.get('record_date'),
                    "weight": record_data['weight'],
                    "notes": record_data.get('notes', '')
                })
        
        # 체중 변화 계산
        weight_change = 0
        if len(weights) >= 2:
            weight_change = weights[-1]['weight'] - weights[0]['weight']
        
        return {
            "cow_id": cow_id,
            "period_months": months,
            "weight_records": weights,
            "total_weight_change": round(weight_change, 2),
            "trend": "증가" if weight_change > 0 else "감소" if weight_change < 0 else "유지"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"체중 추이 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/cow/{cow_id}/reproduction/timeline",
            summary="번식 타임라인 조회",
            description="특정 젖소의 번식 관련 기록들을 시간순으로 조회합니다. 발정, 수정, 임신감정, 분만 등의 이력을 확인할 수 있습니다.")
def get_reproduction_timeline(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """번식 타임라인 조회"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 번식 관련 기록들 조회
        reproduction_types = [
            DetailedRecordType.ESTRUS.value,
            DetailedRecordType.INSEMINATION.value,
            DetailedRecordType.PREGNANCY_CHECK.value,
            DetailedRecordType.CALVING.value
        ]
        
        timeline = []
        for record_type in reproduction_types:
            records = (db.collection('cow_detailed_records')
                      .where(filter=('cow_id', '==', cow_id))
                      .where(filter=('farm_id', '==', farm_id))
                      .where(filter=('record_type', '==', record_type))
                      .where(filter=('is_active', '==', True))
                      .order_by('record_date', direction='DESCENDING')
                      .limit(10)
                      .get())
            
            for record in records:
                data = record.to_dict()
                timeline.append({
                    "id": data["id"],
                    "record_type": DetailedRecordType(record_type),
                    "record_date": data["record_date"],
                    "title": data["title"],
                    "summary": data.get("description", ""),
                    "created_at": data["created_at"]
                })
        
        # 날짜순 정렬 (최신순)
        timeline.sort(key=lambda x: x["record_date"], reverse=True)
        
        return {
            "cow_id": cow_id,
            "timeline": timeline[:20]  # 최대 20개만 반환
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"번식 타임라인 조회 중 오류가 발생했습니다: {str(e)}"
        )

# ===== 젖소별 모든 기록 요약 =====
@router.get("/cow/{cow_id}/summary",
            summary="젖소별 기록 요약 조회",
            description="특정 젖소의 모든 기록 현황을 요약하여 조회합니다. 기록 유형별 개수, 최근 활동 등을 확인할 수 있습니다.")
def get_cow_records_summary(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """젖소별 기록 요약"""
    try:
        from config.firebase_config import get_firestore_client
        from datetime import datetime, timedelta
        
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # 각 기록 유형별 총 개수
        total_counts = {}
        for record_type in DetailedRecordType:
            count = len((db.collection('cow_detailed_records')
                        .where(filter=('cow_id', '==', cow_id))
                        .where(filter=('farm_id', '==', farm_id))
                        .where(filter=('record_type', '==', record_type.value))
                        .where(filter=('is_active', '==', True))
                        .get()))
            total_counts[record_type.value] = count
        
        # 최근 30일 기록 개수
        recent_count = len((db.collection('cow_detailed_records')
                           .where(filter=('cow_id', '==', cow_id))
                           .where(filter=('farm_id', '==', farm_id))
                           .where(filter=('record_type', '==', record_type.value))
                           .where(filter=('is_active', '==', True))
                           .where(filter=('record_date', '>=', thirty_days_ago))
                           .get()))
        
        # 전체 기록 개수
        total_records = len((db.collection('cow_detailed_records')
                           .where(filter=('cow_id', '==', cow_id))
                           .where(filter=('farm_id', '==', farm_id))
                           .where(filter=('is_active', '==', True))
                           .get()))
        
        return {
            "cow_id": cow_id,
            "total_records": total_records,
            "recent_records_30days": recent_count,
            "record_type_counts": total_counts
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"젖소 기록 요약 조회 중 오류가 발생했습니다: {str(e)}"
        )

# ===== 플러터 프론트엔드용 기록 조회 엔드포인트들 =====

@router.get("/cow/{cow_id}/health-records", 
            response_model=List[DetailedRecordSummary],
            summary="젖소별 건강 기록 조회",
            description="특정 젖소의 모든 건강 관련 기록을 조회합니다. 건강검진, 백신접종, 치료 기록을 포함합니다.")
def get_cow_health_records(
    cow_id: str,
    limit: int = Query(100, description="조회할 기록 수 제한", ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 모든 건강 관련 기록 조회 (건강검진, 백신접종, 치료)"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 건강 관련 기록 타입들
        health_types = [
            DetailedRecordType.HEALTH_CHECK.value,
            DetailedRecordType.VACCINATION.value,
            DetailedRecordType.TREATMENT.value
        ]
        
        all_records = []
        for record_type in health_types:
            records = (db.collection('cow_detailed_records')
                      .where(filter=('cow_id', '==', cow_id))
                      .where(filter=('farm_id', '==', farm_id))
                      .where(filter=('record_type', '==', record_type))
                      .where(filter=('is_active', '==', True))
                      .order_by('record_date', direction='DESCENDING')
                      .limit(limit)
                      .get())
            
            for record in records:
                data = record.to_dict()
                all_records.append(DetailedRecordSummary(
                    id=data["id"],
                    cow_id=data["cow_id"],
                    record_type=data["record_type"],
                    record_date=data["record_date"],
                    title=data["title"],
                    description=data.get("description", ""),
                    created_at=data["created_at"],
                    updated_at=data["updated_at"]
                ))
        
        # 날짜순 정렬 (최신순)
        all_records.sort(key=lambda x: x.record_date, reverse=True)
        
        return all_records[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"건강 기록 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/cow/{cow_id}/milking-records", 
            response_model=List[DetailedRecordSummary],
            summary="젖소별 착유 기록 조회",
            description="특정 젖소의 모든 착유 기록을 조회합니다. 착유량, 착유 시간, 유성분 정보 등을 포함합니다.")
def get_cow_all_milking_records(
    cow_id: str,
    limit: int = Query(100, description="조회할 기록 수 제한", ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 모든 착유 기록 조회"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        records = (db.collection('cow_detailed_records')
                  .where(filter=('cow_id', '==', cow_id))
                  .where(filter=('farm_id', '==', farm_id))
                  .where(filter=('record_type', '==', DetailedRecordType.MILKING.value))
                  .where(filter=('is_active', '==', True))
                  .order_by('record_date', direction='DESCENDING')
                  .limit(limit)
                  .get())
        
        result = []
        for record in records:
            data = record.to_dict()
            result.append(DetailedRecordSummary(
                id=data["id"],
                cow_id=data["cow_id"],
                record_type=data["record_type"],
                record_date=data["record_date"],
                title=data["title"],
                description=data.get("description", ""),
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"착유 기록 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/cow/{cow_id}/breeding-records", 
            response_model=List[DetailedRecordSummary],
            summary="젖소별 번식 기록 조회",
            description="특정 젖소의 모든 번식 관련 기록을 조회합니다. 발정, 인공수정, 임신감정, 분만 기록을 포함합니다.")
def get_cow_breeding_records(
    cow_id: str,
    limit: int = Query(100, description="조회할 기록 수 제한", ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 모든 번식 관련 기록 조회 (발정, 인공수정, 임신감정, 분만)"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 번식 관련 기록 타입들
        breeding_types = [
            DetailedRecordType.ESTRUS.value,
            DetailedRecordType.INSEMINATION.value,
            DetailedRecordType.PREGNANCY_CHECK.value,
            DetailedRecordType.CALVING.value
        ]
        
        all_records = []
        for record_type in breeding_types:
            records = (db.collection('cow_detailed_records')
                      .where(filter=('cow_id', '==', cow_id))
                      .where(filter=('farm_id', '==', farm_id))
                      .where(filter=('record_type', '==', record_type))
                      .where(filter=('is_active', '==', True))
                      .order_by('record_date', direction='DESCENDING')
                      .limit(limit)
                      .get())
            
            for record in records:
                data = record.to_dict()
                all_records.append(DetailedRecordSummary(
                    id=data["id"],
                    cow_id=data["cow_id"],
                    record_type=data["record_type"],
                    record_date=data["record_date"],
                    title=data["title"],
                    description=data.get("description", ""),
                    created_at=data["created_at"],
                    updated_at=data["updated_at"]
                ))
        
        # 날짜순 정렬 (최신순)
        all_records.sort(key=lambda x: x.record_date, reverse=True)
        
        return all_records[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"번식 기록 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/cow/{cow_id}/feed-records", 
            response_model=List[DetailedRecordSummary],
            summary="젖소별 사료급여 기록 조회",
            description="특정 젖소의 모든 사료급여 기록을 조회합니다. 사료 종류, 급여량, 급여 시간 등을 포함합니다.")
def get_cow_feed_records(
    cow_id: str,
    limit: int = Query(100, description="조회할 기록 수 제한", ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 모든 사료급여 기록 조회"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        records = (db.collection('cow_detailed_records')
                  .where(filter=('cow_id', '==', cow_id))
                  .where(filter=('farm_id', '==', farm_id))
                  .where(filter=('record_type', '==', DetailedRecordType.FEED.value))
                  .where(filter=('is_active', '==', True))
                  .order_by('record_date', direction='DESCENDING')
                  .limit(limit)
                  .get())
        
        result = []
        for record in records:
            data = record.to_dict()
            result.append(DetailedRecordSummary(
                id=data["id"],
                cow_id=data["cow_id"],
                record_type=data["record_type"],
                record_date=data["record_date"],
                title=data["title"],
                description=data.get("description", ""),
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사료급여 기록 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/cow/{cow_id}/weight-records", 
            response_model=List[DetailedRecordSummary],
            summary="젖소별 체중측정 기록 조회",
            description="특정 젖소의 모든 체중측정 기록을 조회합니다. 측정 체중, 측정 날짜, 체형점수 등을 포함합니다.")
def get_cow_weight_records(
    cow_id: str,
    limit: int = Query(100, description="조회할 기록 수 제한", ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 모든 체중측정 기록 조회"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        records = (db.collection('cow_detailed_records')
                  .where(filter=('cow_id', '==', cow_id))
                  .where(filter=('farm_id', '==', farm_id))
                  .where(filter=('record_type', '==', DetailedRecordType.WEIGHT.value))
                  .where(filter=('is_active', '==', True))
                  .order_by('record_date', direction='DESCENDING')
                  .limit(limit)
                  .get())
        
        result = []
        for record in records:
            data = record.to_dict()
            result.append(DetailedRecordSummary(
                id=data["id"],
                cow_id=data["cow_id"],
                record_type=data["record_type"],
                record_date=data["record_date"],
                title=data["title"],
                description=data.get("description", ""),
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"체중측정 기록 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/cow/{cow_id}/all-records", 
            response_model=List[DetailedRecordSummary],
            summary="젖소별 전체 기록 조회",
            description="""
            특정 젖소의 모든 상세 기록을 조회합니다. 기록 유형별 필터링이 가능하며, 전체 또는 특정 타입만 조회할 수 있습니다.
            
            **기록 유형별 필터링 옵션:**
            
            **기본 관리**
            - `milking`: 착유 기록 (착유량, 유성분 등)
            - `feed`: 사료급여 기록 (사료종류, 급여량 등) 
            - `weight`: 체중측정 기록 (체중, 체형점수 등)
            
            **건강 관리**
            - `health_check`: 건강검진 기록 (체온, 맥박, 일반건강상태 등)
            - `vaccination`: 백신접종 기록 (백신명, 접종일 등)
            - `treatment`: 치료 기록 (진단명, 처방약, 치료과정 등)
            - `disease`: 질병 기록 (질병발생, 증상 등)
            
            **번식 관리**
            - `estrus`: 발정 기록 (발정증상, 발정주기 등)
            - `insemination`: 인공수정 기록 (수정일, 정액정보 등)
            - `pregnancy_check`: 임신감정 기록 (임신여부, 분만예정일 등)
            - `calving`: 분만 기록 (분만일시, 송아지정보 등)
            - `breeding`: 번식 관련 기타 기록
            
            **특수 관리**
            - `abortion`: 유산 기록 (유산원인, 후속조치 등)
            - `dry_off`: 건유 전환 기록 (건유시작일, 건유기간 등)
            - `culling`: 도태 기록 (도태사유, 처리방법 등)
            - `status_change`: 상태 변경 기록 (젖소 상태 변화)
            - `other`: 기타 기록 (특별한 기록사항)
            
            **미입력시 모든 기록 타입을 조회합니다.**
            """)
def get_cow_all_records(
    cow_id: str,
    limit: int = Query(100, description="조회할 기록 수 제한 (최대 200개)", ge=1, le=200),
    record_type: Optional[DetailedRecordType] = Query(
        None, 
        description="""
        **기록 유형 필터 (선택사항)**
        
        **기본 관리**
        - `milking`: 착유 기록 (착유량, 유성분 등)
        - `feed`: 사료급여 기록 (사료종류, 급여량 등) 
        - `weight`: 체중측정 기록 (체중, 체형점수 등)
        
        **건강 관리**
        - `health_check`: 건강검진 기록 (체온, 맥박, 일반건강상태 등)
        - `vaccination`: 백신접종 기록 (백신명, 접종일 등)
        - `treatment`: 치료 기록 (진단명, 처방약, 치료과정 등)
        - `disease`: 질병 기록 (질병발생, 증상 등)
        
        **번식 관리**
        - `estrus`: 발정 기록 (발정증상, 발정주기 등)
        - `insemination`: 인공수정 기록 (수정일, 정액정보 등)
        - `pregnancy_check`: 임신감정 기록 (임신여부, 분만예정일 등)
        - `calving`: 분만 기록 (분만일시, 송아지정보 등)
        - `breeding`: 번식 관련 기타 기록
        
        **특수 관리**
        - `abortion`: 유산 기록 (유산원인, 후속조치 등)
        - `dry_off`: 건유 전환 기록 (건유시작일, 건유기간 등)
        - `culling`: 도태 기록 (도태사유, 처리방법 등)
        - `status_change`: 상태 변경 기록 (젖소 상태 변화)
        - `other`: 기타 기록 (특별한 기록사항)
        
        **미입력시 모든 기록 타입을 조회합니다.**
        """
    ),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 모든 상세 기록 조회 (전체 또는 특정 타입 필터링)"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 기본 쿼리
        query = (db.collection('cow_detailed_records')
                .where(filter=('cow_id', '==', cow_id))
                .where(filter=('farm_id', '==', farm_id))
                .where(filter=('is_active', '==', True)))
        
        # 기록 타입 필터링
        if record_type:
            query = query.where(filter=('record_type', '==', record_type.value))
        
        records = (query.order_by('record_date', direction='DESCENDING')
                  .limit(limit)
                  .get())
        
        result = []
        for record in records:
            data = record.to_dict()
            result.append(DetailedRecordSummary(
                id=data["id"],
                cow_id=data["cow_id"],
                record_type=data["record_type"],
                record_date=data["record_date"],
                title=data["title"],
                description=data.get("description", ""),
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기록 조회 중 오류가 발생했습니다: {str(e)}"
        )