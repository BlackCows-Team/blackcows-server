from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
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