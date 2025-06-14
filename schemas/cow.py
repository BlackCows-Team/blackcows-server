from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, time
from enum import Enum

# 건강상태 열거형
class HealthStatus(str, Enum):
    EXCELLENT = "excellent"  # 우수
    GOOD = "good"           # 양호
    AVERAGE = "average"     # 보통
    POOR = "poor"          # 불량
    SICK = "sick"          # 질병

# 번식생태 열거형
class BreedingStatus(str, Enum):
    CALF = "calf"                    # 송아지
    HEIFER = "heifer"               # 미경산우
    PREGNANT = "pregnant"           # 임신중
    LACTATING = "lactating"         # 비유중
    DRY = "dry"                     # 건유중
    BREEDING = "breeding"           # 교배대기

# 젖소 등록 요청 스키마
class CowCreate(BaseModel):
    ear_tag_number: str                         # 이표번호 (필수)
    name: str                                   # 이름(별명) (필수)
    birthdate: Optional[str] = None             # 출생일 (선택) - YYYY-MM-DD 형식
    sensor_number: Optional[str] = None         # 센서 번호 (선택)
    health_status: Optional[HealthStatus] = None # 건강상태 (선택)
    breeding_status: Optional[BreedingStatus] = None # 번식생태 (선택)
    breed: Optional[str] = None                 # 품종 (선택)
    notes: Optional[str] = None                 # 비고 (선택)
    
    @validator('ear_tag_number')
    def validate_ear_tag_number(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('이표번호는 필수입니다')
        clean_number = v.strip()
        if len(clean_number) != 12:
            raise ValueError('이표번호는 002를 포함한 12자리여야 합니다')
        if not clean_number.isdigit():
            raise ValueError('이표번호는 숫자만 입력 가능합니다')
        return clean_number
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('젖소 이름은 필수입니다')
        if len(v) > 50:
            raise ValueError('젖소 이름은 50자 이하여야 합니다')
        return v.strip()
    
    @validator('birthdate')
    def validate_birthdate(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                return None  # 빈 문자열은 None으로 처리
            
            try:
                from datetime import datetime
                # YYYY-MM-DD 형식 검증
                birth_date = datetime.strptime(v.strip(), '%Y-%m-%d')
                
                # 미래 날짜 검증
                today = datetime.now()
                if birth_date > today:
                    raise ValueError('출생일은 미래 날짜일 수 없습니다')
                
                # 너무 오래된 날짜 검증
                from datetime import timedelta
                fifty_years_ago = today - timedelta(days=365*20)
                if birth_date < fifty_years_ago:
                    raise ValueError('출생일이 너무 오래되었습니다 (20년 이내)')
                
                return v.strip()
            except ValueError as e:
                if '출생일' in str(e):
                    raise e
                raise ValueError('출생일은 YYYY-MM-DD 형식으로 입력해주세요 (예: 2022-03-15)')
        return v
    
    @validator('sensor_number')
    def validate_sensor_number(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                return None  # 빈 문자열은 None으로 처리
            clean_sensor = v.strip()
            if len(clean_sensor) != 13:
                raise ValueError('센서 번호는 정확히 13자리여야 합니다')
            if not clean_sensor.isdigit():
                raise ValueError('센서 번호는 숫자만 입력 가능합니다')
            return clean_sensor
        return v

# 젖소 응답 스키마
class CowResponse(BaseModel):
    id: str
    ear_tag_number: str
    name: str
    birthdate: Optional[str]
    sensor_number: Optional[str]
    health_status: Optional[HealthStatus]
    breeding_status: Optional[BreedingStatus]
    breed: Optional[str]
    notes: Optional[str]
    is_favorite: bool = False            # 즐겨찾기 여부
    farm_id: str                         # 소속 농장 ID
    owner_id: str                        # 소유자 ID
    created_at: datetime
    updated_at: datetime
    is_active: bool

# 젖소 업데이트 스키마
class CowUpdate(BaseModel):
    name: Optional[str] = None
    sensor_number: Optional[str] = None
    health_status: Optional[HealthStatus] = None
    breeding_status: Optional[BreedingStatus] = None
    birthdate: Optional[str] = None
    breed: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('젖소 이름은 비어있을 수 없습니다')
            if len(v) > 50:
                raise ValueError('젖소 이름은 50자 이하여야 합니다')
            return v.strip()
        return v
    
    @validator('birthdate')
    def validate_birthdate_update(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                return None  # 빈 문자열은 None으로 처리
            
            try:
                from datetime import datetime
                # YYYY-MM-DD 형식 검증
                birth_date = datetime.strptime(v.strip(), '%Y-%m-%d')
                
                # 미래 날짜 검증
                today = datetime.now()
                if birth_date > today:
                    raise ValueError('출생일은 미래 날짜일 수 없습니다')
                
                # 너무 오래된 날짜 검증
                from datetime import timedelta
                fifty_years_ago = today - timedelta(days=365*20)
                if birth_date < fifty_years_ago:
                    raise ValueError('출생일이 너무 오래되었습니다 (20년 이내)')
                
                return v.strip()
            except ValueError as e:
                if '출생일' in str(e):
                    raise e
                raise ValueError('출생일은 YYYY-MM-DD 형식으로 입력해주세요 (예: 2022-03-15)')
        return v
    
    @validator('sensor_number')
    def validate_sensor_number(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                return None  # 빈 문자열은 None으로 처리
            clean_sensor = v.strip()
            if len(clean_sensor) != 13:
                raise ValueError('센서 번호는 정확히 13자리여야 합니다')
            if not clean_sensor.isdigit():
                raise ValueError('센서 번호는 숫자만 입력 가능합니다')
            return clean_sensor
        return v

# 기존 호환성을 위한 기본 Cow 클래스
class Cow(BaseModel):
    id: str
    number: str  # 이표번호 (기존 호환성)
    birthdate: Optional[str]
    breed: Optional[str]

# 성격 열거형
class Temperament(str, Enum):
    GENTLE = "gentle"        # 온순
    ACTIVE = "active"        # 활발
    NERVOUS = "nervous"      # 예민
    AGGRESSIVE = "aggressive" # 공격적
    CALM = "calm"           # 차분

# 착유 행동 열거형
class MilkingBehavior(str, Enum):
    COOPERATIVE = "cooperative"     # 협조적
    UNCOOPERATIVE = "uncooperative" # 비협조적
    NORMAL = "normal"              # 보통
    RESTLESS = "restless"          # 불안

# 젖소 상세 정보 업데이트 스키마 (수정하기에서 사용)
class CowDetailUpdate(BaseModel):
    # 기본 정보 수정
    name: Optional[str] = None
    birthdate: Optional[str] = None
    sensor_number: Optional[str] = None
    health_status: Optional[HealthStatus] = None
    breeding_status: Optional[BreedingStatus] = None
    breed: Optional[str] = None
    notes: Optional[str] = None
    
    # 신체 정보
    body_weight: Optional[float] = None           # 체중(kg)
    body_height: Optional[float] = None           # 체고(cm)
    body_length: Optional[float] = None           # 체장(cm)
    chest_girth: Optional[float] = None           # 흉위(cm)
    body_condition_score: Optional[float] = None  # 체형점수(1-5)
    
    # 생산 정보
    lactation_number: Optional[int] = None        # 산차수
    milk_yield_record: Optional[float] = None     # 최고 착유량 기록(L)
    lifetime_milk_yield: Optional[float] = None   # 누적 착유량(L)
    average_daily_yield: Optional[float] = None   # 평균 일일 착유량(L)
    
    # 번식 정보
    first_calving_date: Optional[str] = None      # 초산일 (YYYY-MM-DD)
    last_calving_date: Optional[str] = None       # 최종 분만일 (YYYY-MM-DD)
    total_calves: Optional[int] = None            # 총 분만 횟수
    breeding_efficiency: Optional[float] = None   # 번식 효율(%)
    
    # 건강 정보
    vaccination_status: Optional[str] = None      # 백신 접종 상태
    last_health_check: Optional[str] = None       # 최근 건강검진일 (YYYY-MM-DD)
    chronic_conditions: Optional[List[str]] = None # 만성 질환 목록
    allergy_info: Optional[str] = None            # 알레르기 정보
    
    # 관리 정보
    purchase_date: Optional[str] = None           # 구입일 (YYYY-MM-DD)
    purchase_price: Optional[float] = None        # 구입 가격(원)
    current_value: Optional[float] = None         # 현재 가치(원)
    insurance_policy: Optional[str] = None        # 보험 정보
    special_management: Optional[str] = None      # 특별 관리 사항
    
    # 혈통 정보
    mother_id: Optional[str] = None               # 어미 젖소 ID
    father_info: Optional[str] = None             # 아비 정보
    genetic_info: Optional[str] = None            # 유전 정보
    
    # 사료 정보
    feed_type: Optional[str] = None               # 주 사료 종류
    daily_feed_amount: Optional[float] = None     # 일일 사료량(kg)
    supplement_info: Optional[str] = None         # 보조 사료 정보
    
    # 위치 정보
    barn_section: Optional[str] = None            # 축사 구역
    stall_number: Optional[str] = None            # 스톨 번호
    
    # 행동 특성
    temperament: Optional[Temperament] = None     # 성격
    milking_behavior: Optional[MilkingBehavior] = None # 착유 행동 특성
    retirement_plan: Optional[str] = None         # 도태 계획
    
    # Validator들
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('젖소 이름은 비어있을 수 없습니다')
            if len(v) > 50:
                raise ValueError('젖소 이름은 50자 이하여야 합니다')
            return v.strip()
        return v
    
    @validator('birthdate', 'first_calving_date', 'last_calving_date', 'purchase_date', 'last_health_check')
    def validate_dates(cls, v):
        if v is not None and len(v.strip()) > 0:
            try:
                from datetime import datetime
                datetime.strptime(v.strip(), '%Y-%m-%d')
                return v.strip()
            except ValueError:
                raise ValueError('날짜는 YYYY-MM-DD 형식으로 입력해주세요')
        return v
    
    @validator('body_weight')
    def validate_body_weight(cls, v):
        if v is not None:
            if v <= 0 or v > 1000:
                raise ValueError('체중은 0보다 크고 1000kg 이하여야 합니다')
        return v
    
    @validator('body_condition_score')
    def validate_body_condition_score(cls, v):
        if v is not None:
            if v < 1 or v > 5:
                raise ValueError('체형점수는 1-5 사이여야 합니다')
        return v
    
    @validator('lactation_number', 'total_calves')
    def validate_positive_integers(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError('음수는 입력할 수 없습니다')
        return v
    
    @validator('breeding_efficiency')
    def validate_breeding_efficiency(cls, v):
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError('번식 효율은 0-100% 사이여야 합니다')
        return v

# 젖소 응답 스키마 수정 (상세 정보 포함)
class CowDetailResponse(BaseModel):
    # 기본 정보
    id: str
    ear_tag_number: str
    name: str
    birthdate: Optional[str]
    sensor_number: Optional[str]
    health_status: Optional[HealthStatus]
    breeding_status: Optional[BreedingStatus]
    breed: Optional[str]
    notes: Optional[str]
    is_favorite: bool = False
    farm_id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    # 상세 정보 (모든 필드 포함)
    has_detailed_info: bool = False
    detail_updated_at: Optional[datetime] = None
    
    # 신체 정보
    body_weight: Optional[float] = None
    body_height: Optional[float] = None
    body_length: Optional[float] = None
    chest_girth: Optional[float] = None
    body_condition_score: Optional[float] = None
    
    # 생산 정보
    lactation_number: Optional[int] = None
    milk_yield_record: Optional[float] = None
    lifetime_milk_yield: Optional[float] = None
    average_daily_yield: Optional[float] = None
    
    # 번식 정보
    first_calving_date: Optional[str] = None
    last_calving_date: Optional[str] = None
    total_calves: Optional[int] = None
    breeding_efficiency: Optional[float] = None
    
    # 건강 정보
    vaccination_status: Optional[str] = None
    last_health_check: Optional[str] = None
    chronic_conditions: Optional[List[str]] = None
    allergy_info: Optional[str] = None
    
    # 관리 정보
    purchase_date: Optional[str] = None
    purchase_price: Optional[float] = None
    current_value: Optional[float] = None
    insurance_policy: Optional[str] = None
    special_management: Optional[str] = None
    
    # 혈통 정보
    mother_id: Optional[str] = None
    father_info: Optional[str] = None
    genetic_info: Optional[str] = None
    
    # 사료 정보
    feed_type: Optional[str] = None
    daily_feed_amount: Optional[float] = None
    supplement_info: Optional[str] = None
    
    # 위치 정보
    barn_section: Optional[str] = None
    stall_number: Optional[str] = None
    
    # 행동 특성
    temperament: Optional[Temperament] = None
    milking_behavior: Optional[MilkingBehavior] = None
    retirement_plan: Optional[str] = None

# 기존 CowResponse에 has_detailed_info 필드 추가

CowResponse.model_rebuild()  # Pydantic 모델 재빌드