from pydantic import BaseModel, validator, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, time
from enum import Enum


class DetailedRecordType(str, Enum):
    # 기존 기록 유형
    BREEDING = "breeding"
    DISEASE = "disease"
    STATUS_CHANGE = "status_change"
    OTHER = "other"
    
    # 새로운 상세 기록 유형
    MILKING = "milking"              # 착유 기록
    FEED = "feed"                    # 사료 급여
    HEALTH_CHECK = "health_check"    # 건강 검진
    WEIGHT = "weight"                # 체중 측정
    VACCINATION = "vaccination"      # 백신 접종
    TREATMENT = "treatment"          # 치료 기록
    ESTRUS = "estrus"               # 발정 기록
    PREGNANCY_CHECK = "pregnancy_check"  # 임신 감정
    CALVING = "calving"             # 분만 기록
    INSEMINATION = "insemination"   # 인공수정
    ABORTION = "abortion"           # 유산 기록
    DRY_OFF = "dry_off"            # 건유 전환
    CULLING = "culling"            # 도태 기록

# 착유 기록 스키마
class MilkingRecordCreate(BaseModel):
    cow_id: str = Field(..., description="젖소 ID(필수)")
    record_date: str = Field(..., description="착유 날짜 (필수)")  # YYYY-MM-DD
    milk_yield: float = Field(..., description="착유량 (필수) - 리터(L) 단위", gt=0)
    
    milking_start_time: Optional[str] = Field(None, description="착유 시작 시간 - HH:MM:SS 형식")
    milking_end_time: Optional[str] = Field(None, description="착유 종료 시간 - HH:MM:SS 형식")
    milking_session: Optional[int] = Field(None, description="착유 횟수 (1회차, 2회차 등)")
    conductivity: Optional[float] = Field(None, description="전도율") # 전도율
    somatic_cell_count: Optional[int] = Field(None, description="체세포수")
    blood_flow_detected: Optional[bool] = Field(None, description="혈액 흐름 감지 여부")
    color_value: Optional[str] = Field(None, description="색상값")
    temperature: Optional[float] = Field(None, description="온도(°C)")
    fat_percentage: Optional[float] = Field(None, description="유지방 비율(%)")
    protein_percentage: Optional[float] = Field(None, description="유단백 비율(%)")
    air_flow_value: Optional[float] = Field(None, description="공기 흐름값")
    lactation_number: Optional[int] = Field(None, description="산차수")
    rumination_time: Optional[int] = Field(None, description="반추 시간(분)")
    collection_code: Optional[str] = Field(None, description="수집 구분 코드")
    collection_count: Optional[int] = Field(None, description="수집 건수")
    notes: Optional[str] = Field(None, description="비고")

    # 유효성 검사
    @validator('record_date')
    def validate_record_date(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('착유 날짜는 필수입니다')
        
        try:
            from datetime import datetime
            # YYYY-MM-DD 형식 검증
            record_datetime = datetime.strptime(v.strip(), '%Y-%m-%d')
            
            # 미래 날짜는 허용하지만 너무 먼 미래는 제한 (1년 후까지)
            today = datetime.now()
            from datetime import timedelta
            one_year_later = today + timedelta(days=365)
            if record_datetime > one_year_later:
                raise ValueError('착유 날짜는 1년 이후까지만 입력 가능합니다')
            
            # 너무 오래된 날짜 제한 (5년 전까지)
            five_years_ago = today - timedelta(days=365*5)
            if record_datetime < five_years_ago:
                raise ValueError('착유 날짜는 5년 이전까지만 입력 가능합니다')
            
            return v.strip()
        except ValueError as e:
            if '착유 날짜' in str(e):
                raise e
            raise ValueError('착유 날짜는 YYYY-MM-DD 형식으로 입력해주세요 (예: 2025-06-16)')
    
    @validator('milk_yield')
    def validate_milk_yield(cls, v):
        if v is None:
            raise ValueError('착유량은 필수입니다')
        if v <= 0:
            raise ValueError('착유량은 0보다 커야 합니다')
        return v
    
    @validator('milking_start_time', 'milking_end_time')
    def validate_time_format(cls, v):
        if v is not None and len(v.strip()) > 0:
            try:
                from datetime import datetime
                datetime.strptime(v.strip(), '%H:%M:%S')
                return v.strip()
            except ValueError:
                try:
                    # HH:MM 형식도 허용
                    datetime.strptime(v.strip(), '%H:%M')
                    return v.strip() + ':00'
                except ValueError:
                    raise ValueError('시간은 HH:MM:SS 또는 HH:MM 형식으로 입력해주세요')
        return v
    
    @validator('milking_session')
    def validate_milking_session(cls, v):
        if v is not None:
            if v < 1:  
                raise ValueError('착유 횟수는 1회 이상 입력해야 합니다')
        return v
    
    @validator('fat_percentage', 'protein_percentage')
    def validate_percentage(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('비율은 0% 이상 입력해야 합니다')
        return v
    
    @validator('somatic_cell_count')
    def validate_somatic_cell_count(cls, v):
        if v is not None:
            if v < 0 or v > 10000000:  # 체세포수 범위
                raise ValueError('체세포수는 0-10,000,000 사이여야 합니다')
        return v
    

# 발정 기록 스키마
class EstrusRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    estrus_start_time: Optional[str] = None    # 발정 시작 시간
    estrus_intensity: Optional[str] = None     # 발정 강도 (약/중/강)
    estrus_duration: Optional[int] = None      # 발정 지속시간(시간)
    behavior_signs: Optional[List[str]] = None # 발정 징후 리스트
    visual_signs: Optional[List[str]] = None   # 육안 관찰 사항
    detected_by: Optional[str] = None          # 발견자
    detection_method: Optional[str] = None     # 발견 방법 (육안/센서/기타)
    next_expected_estrus: Optional[str] = None # 다음 발정 예상일
    breeding_planned: Optional[bool] = None    # 교배 계획 여부
    notes: Optional[str] = None

# 인공수정 기록 스키마  
class InseminationRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    insemination_time: Optional[str] = None    # 수정 시간
    bull_id: Optional[str] = None              # 종축 ID
    bull_breed: Optional[str] = None           # 종축 품종
    semen_batch: Optional[str] = None          # 정액 로트번호
    semen_quality: Optional[str] = None        # 정액 품질등급
    technician_name: Optional[str] = None      # 수정사 이름
    insemination_method: Optional[str] = None  # 수정 방법
    cervix_condition: Optional[str] = None     # 자궁경관 상태
    success_probability: Optional[float] = None # 성공 예상률(%)
    cost: Optional[float] = None               # 비용
    pregnancy_check_scheduled: Optional[str] = None # 임신감정 예정일
    notes: Optional[str] = None

# 임신감정 기록 스키마
class PregnancyCheckRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    check_method: Optional[str] = None         # 감정 방법 (직장검사/초음파/혈액검사)
    check_result: Optional[str] = None         # 감정 결과 (임신/비임신/의심)
    pregnancy_stage: Optional[int] = None      # 임신 단계(일)
    fetus_condition: Optional[str] = None      # 태아 상태
    expected_calving_date: Optional[str] = None # 분만예정일
    veterinarian: Optional[str] = None         # 수의사명
    check_cost: Optional[float] = None         # 감정비용
    next_check_date: Optional[str] = None      # 다음 감정일
    additional_care: Optional[str] = None      # 추가 관리사항
    notes: Optional[str] = None

# 분만 기록 스키마
class CalvingRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    calving_start_time: Optional[str] = None   # 분만 시작시간
    calving_end_time: Optional[str] = None     # 분만 완료시간
    calving_difficulty: Optional[str] = None   # 분만 난이도 (정상/약간어려움/어려움/제왕절개)
    calf_count: Optional[int] = None           # 송아지 수
    calf_gender: Optional[List[str]] = None    # 송아지 성별 리스트
    calf_weight: Optional[List[float]] = None  # 송아지 체중 리스트
    calf_health: Optional[List[str]] = None    # 송아지 건강상태 리스트
    placenta_expelled: Optional[bool] = None   # 태반 배출 여부
    placenta_expulsion_time: Optional[str] = None # 태반 배출 시간
    complications: Optional[List[str]] = None  # 합병증 리스트
    assistance_required: Optional[bool] = None # 도움 필요 여부
    veterinarian_called: Optional[bool] = None # 수의사 호출 여부
    dam_condition: Optional[str] = None        # 어미소 상태
    lactation_start: Optional[str] = None      # 비유 시작일
    notes: Optional[str] = None

# 유산 기록 스키마
class AbortionRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    abortion_time: Optional[str] = None        # 유산 시간
    pregnancy_stage: Optional[int] = None      # 임신 단계(일)
    abortion_cause: Optional[str] = None       # 유산 원인
    fetus_condition: Optional[str] = None      # 태아 상태
    placenta_condition: Optional[str] = None   # 태반 상태
    dam_condition: Optional[str] = None        # 어미소 상태
    veterinarian_examined: Optional[bool] = None # 수의사 진찰 여부
    treatment_required: Optional[bool] = None  # 치료 필요 여부
    treatment_details: Optional[str] = None    # 치료 내용
    recovery_period: Optional[int] = None      # 회복 기간(일)
    breeding_restriction: Optional[int] = None # 교배 제한 기간(일)
    cost: Optional[float] = None               # 치료비용
    notes: Optional[str] = None

# 사료급여 기록 스키마
class FeedRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    feed_time: Optional[str] = None            # 급여 시간
    feed_type: Optional[str] = None            # 사료 종류
    feed_amount: Optional[float] = None        # 급여량(kg)
    feed_quality: Optional[str] = None         # 사료 품질
    supplement_type: Optional[str] = None      # 첨가제 종류
    supplement_amount: Optional[float] = None  # 첨가제 양
    water_consumption: Optional[float] = None  # 음수량(L)
    appetite_condition: Optional[str] = None   # 식욕 상태
    feed_efficiency: Optional[float] = None    # 사료효율
    cost_per_feed: Optional[float] = None      # 사료비용
    fed_by: Optional[str] = None               # 급여자
    notes: Optional[str] = None

# 건강검진 기록 스키마
class HealthCheckRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    check_time: Optional[str] = None           # 검진 시간
    body_temperature: Optional[float] = None   # 체온(°C)
    heart_rate: Optional[int] = None           # 심박수(회/분)
    respiratory_rate: Optional[int] = None     # 호흡수(회/분)
    body_condition_score: Optional[float] = None # 체형점수(1-5)
    udder_condition: Optional[str] = None      # 유방 상태
    hoof_condition: Optional[str] = None       # 발굽 상태
    coat_condition: Optional[str] = None       # 털 상태
    eye_condition: Optional[str] = None        # 눈 상태
    nose_condition: Optional[str] = None       # 코 상태
    appetite: Optional[str] = None             # 식욕 상태
    activity_level: Optional[str] = None       # 활동성
    abnormal_symptoms: Optional[List[str]] = None # 이상 증상
    examiner: Optional[str] = None             # 검진자
    next_check_date: Optional[str] = None      # 다음 검진일
    notes: Optional[str] = None

# 백신접종 기록 스키마
class VaccinationRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    vaccination_time: Optional[str] = None     # 접종 시간
    vaccine_name: Optional[str] = None         # 백신명
    vaccine_type: Optional[str] = None         # 백신 종류
    vaccine_batch: Optional[str] = None        # 백신 로트번호
    dosage: Optional[float] = None             # 접종량(ml)
    injection_site: Optional[str] = None       # 접종 부위
    injection_method: Optional[str] = None     # 접종 방법
    administrator: Optional[str] = None        # 접종자
    vaccine_manufacturer: Optional[str] = None # 제조사
    expiry_date: Optional[str] = None          # 유효기간
    adverse_reaction: Optional[bool] = None    # 부작용 여부
    reaction_details: Optional[str] = None     # 부작용 세부사항
    next_vaccination_due: Optional[str] = None # 다음 접종 예정일
    cost: Optional[float] = None               # 비용
    notes: Optional[str] = None

# 체중측정 기록 스키마
class WeightRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    measurement_time: Optional[str] = None     # 측정 시간
    weight: Optional[float] = None             # 체중(kg)
    measurement_method: Optional[str] = None   # 측정 방법 (전자저울/체척자/목측)
    body_condition_score: Optional[float] = None # 체형점수
    height_withers: Optional[float] = None     # 기갑고(cm)
    body_length: Optional[float] = None        # 체장(cm)
    chest_girth: Optional[float] = None        # 흉위(cm)
    growth_rate: Optional[float] = None        # 증체율(kg/일)
    target_weight: Optional[float] = None      # 목표체중(kg)
    weight_category: Optional[str] = None      # 체중 등급
    measurer: Optional[str] = None             # 측정자
    notes: Optional[str] = None

# 치료 기록 스키마
class TreatmentRecordCreate(BaseModel):
    cow_id: str
    record_date: str
    treatment_time: Optional[str] = None       # 치료 시간
    treatment_type: Optional[str] = None       # 치료 종류
    symptoms: Optional[List[str]] = None       # 증상 리스트
    diagnosis: Optional[str] = None            # 진단명
    medication_used: Optional[List[str]] = None # 사용약물 리스트
    dosage_info: Optional[Dict[str, str]] = None # 용법용량 정보
    treatment_method: Optional[str] = None     # 치료 방법
    treatment_duration: Optional[int] = None   # 치료 기간(일)
    veterinarian: Optional[str] = None         # 수의사명
    treatment_response: Optional[str] = None   # 치료 반응
    side_effects: Optional[str] = None         # 부작용
    follow_up_required: Optional[bool] = None  # 추후 관찰 필요
    follow_up_date: Optional[str] = None       # 추후 관찰일
    treatment_cost: Optional[float] = None     # 치료비용
    withdrawal_period: Optional[int] = None    # 휴약기간(일)
    notes: Optional[str] = None

# 통합 상세 기록 응답 스키마
class DetailedRecordResponse(BaseModel):
    id: str
    cow_id: str
    cow_name: str
    cow_ear_tag_number: str
    record_type: DetailedRecordType
    record_date: str
    title: str
    description: Optional[str]
    record_data: Dict[str, Any]
    farm_id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

# 기록 요약 스키마 (목록 조회용)
class DetailedRecordSummary(BaseModel):
    id: str
    cow_id: str
    cow_name: str
    cow_ear_tag_number: str
    record_type: DetailedRecordType
    record_date: str
    title: str
    key_values: Dict[str, Any]  # 주요 수치 정보 (착유량, 체중 등)
    created_at: datetime