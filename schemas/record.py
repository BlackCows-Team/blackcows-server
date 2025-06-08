from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 기록 유형 열거형
class RecordType(str, Enum):
    BREEDING = "breeding"       # 번식기록
    DISEASE = "disease"         # 질병기록
    STATUS_CHANGE = "status_change"  # 분류변경
    OTHER = "other"            # 기타기록

# 번식 관련 열거형
class BreedingMethod(str, Enum):
    ARTIFICIAL = "artificial"   # 인공수정
    NATURAL = "natural"        # 자연교배

class BreedingResult(str, Enum):
    SUCCESS = "success"        # 성공
    FAILED = "failed"          # 실패
    PENDING = "pending"        # 확인중

# 질병 심각도 열거형
class DiseaseSeverity(str, Enum):
    MILD = "mild"              # 경미
    MODERATE = "moderate"      # 보통
    SEVERE = "severe"          # 심각
    CRITICAL = "critical"      # 위중

# 치료 상태 열거형
class TreatmentStatus(str, Enum):
    ONGOING = "ongoing"        # 치료중
    COMPLETED = "completed"    # 치료완료
    DISCONTINUED = "discontinued"  # 치료중단

# 기록 생성 기본 스키마
class RecordCreateBase(BaseModel):
    cow_id: str                     # 젖소 ID (필수)
    record_type: RecordType         # 기록 유형 (필수)
    record_date: str                # 기록 날짜 YYYY-MM-DD (필수)
    title: str                      # 제목 (필수)
    description: Optional[str] = None # 설명 (선택)
    
    @validator('record_date')
    def validate_record_date(cls, v):
        try:
            from datetime import datetime
            # YYYY-MM-DD 형식 검증
            record_datetime = datetime.strptime(v.strip(), '%Y-%m-%d')
            
            # 미래 날짜는 허용하지만 너무 먼 미래는 제한 (1년 후까지)
            today = datetime.now()
            from datetime import timedelta
            one_year_later = today + timedelta(days=365)
            if record_datetime > one_year_later:
                raise ValueError('기록 날짜는 1년 이후까지만 입력 가능합니다')
            
            # 너무 오래된 날짜 제한 (10년 전까지)
            ten_years_ago = today - timedelta(days=365*10)
            if record_datetime < ten_years_ago:
                raise ValueError('기록 날짜는 10년 이전까지만 입력 가능합니다')
            
            return v.strip()
        except ValueError as e:
            if '기록 날짜' in str(e):
                raise e
            raise ValueError('기록 날짜는 YYYY-MM-DD 형식으로 입력해주세요 (예: 2025-06-09)')
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('제목은 필수입니다')
        if len(v) > 100:
            raise ValueError('제목은 100자 이하여야 합니다')
        return v.strip()

# 번식기록 생성 스키마
class BreedingRecordCreate(RecordCreateBase):
    breeding_method: BreedingMethod             # 교배방법 (필수)
    breeding_date: str                          # 교배일 YYYY-MM-DD (필수)
    bull_info: Optional[str] = None             # 수소 정보 (선택)
    expected_calving_date: Optional[str] = None # 분만예정일 YYYY-MM-DD (선택)
    pregnancy_check_date: Optional[str] = None  # 임신확인일 YYYY-MM-DD (선택)
    breeding_result: BreedingResult = BreedingResult.PENDING  # 번식결과 (기본: 확인중)
    cost: Optional[float] = None                # 비용 (선택)
    veterinarian: Optional[str] = None          # 수의사명 (선택)
    
    @validator('breeding_date', 'expected_calving_date', 'pregnancy_check_date')
    def validate_dates(cls, v):
        if v is not None and len(v.strip()) > 0:
            try:
                from datetime import datetime
                datetime.strptime(v.strip(), '%Y-%m-%d')
                return v.strip()
            except ValueError:
                raise ValueError('날짜는 YYYY-MM-DD 형식으로 입력해주세요')
        return v

# 질병기록 생성 스키마
class DiseaseRecordCreate(RecordCreateBase):
    disease_name: str                           # 질병명 (필수)
    symptoms: Optional[str] = None              # 증상 (선택)
    severity: DiseaseSeverity = DiseaseSeverity.MILD  # 심각도 (기본: 경미)
    treatment_content: Optional[str] = None     # 치료내용 (선택)
    treatment_start_date: Optional[str] = None  # 치료시작일 YYYY-MM-DD (선택)
    treatment_end_date: Optional[str] = None    # 치료종료일 YYYY-MM-DD (선택)
    treatment_status: TreatmentStatus = TreatmentStatus.ONGOING  # 치료상태 (기본: 치료중)
    treatment_cost: Optional[float] = None      # 치료비용 (선택)
    veterinarian: Optional[str] = None          # 수의사명 (선택)
    medication: Optional[str] = None            # 사용약물 (선택)
    
    @validator('disease_name')
    def validate_disease_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('질병명은 필수입니다')
        if len(v) > 100:
            raise ValueError('질병명은 100자 이하여야 합니다')
        return v.strip()
    
    @validator('treatment_start_date', 'treatment_end_date')
    def validate_treatment_dates(cls, v):
        if v is not None and len(v.strip()) > 0:
            try:
                from datetime import datetime
                datetime.strptime(v.strip(), '%Y-%m-%d')
                return v.strip()
            except ValueError:
                raise ValueError('날짜는 YYYY-MM-DD 형식으로 입력해주세요')
        return v

# 분류변경 기록 생성 스키마
class StatusChangeRecordCreate(RecordCreateBase):
    previous_status: str                        # 이전 상태 (필수)
    new_status: str                            # 변경후 상태 (필수)
    change_reason: str                         # 변경 사유 (필수)
    change_date: str                           # 변경일 YYYY-MM-DD (필수)
    responsible_person: Optional[str] = None    # 담당자 (선택)
    
    @validator('previous_status', 'new_status', 'change_reason')
    def validate_required_fields(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('이 필드는 필수입니다')
        if len(v) > 100:
            raise ValueError('입력값은 100자 이하여야 합니다')
        return v.strip()
    
    @validator('change_date')
    def validate_change_date(cls, v):
        try:
            from datetime import datetime
            datetime.strptime(v.strip(), '%Y-%m-%d')
            return v.strip()
        except ValueError:
            raise ValueError('변경일은 YYYY-MM-DD 형식으로 입력해주세요')

# 기타기록 생성 스키마
class OtherRecordCreate(RecordCreateBase):
    category: Optional[str] = None              # 카테고리 (선택)
    details: Optional[Dict[str, Any]] = None    # 추가 세부사항 (선택)
    attachments: Optional[list] = None          # 첨부파일 목록 (선택)
    importance: Optional[str] = "normal"        # 중요도 (normal, high, urgent)

# 기록 응답 스키마
class RecordResponse(BaseModel):
    id: str
    cow_id: str
    cow_name: str                              # 젖소 이름
    cow_ear_tag_number: str                    # 젖소 이표번호
    record_type: RecordType
    record_date: str
    title: str
    description: Optional[str]
    record_data: Dict[str, Any]                # 기록 유형별 상세 데이터
    farm_id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

# 기록 목록 조회용 요약 스키마
class RecordSummary(BaseModel):
    id: str
    cow_id: str
    cow_name: str
    cow_ear_tag_number: str
    record_type: RecordType
    record_date: str
    title: str
    created_at: datetime

# 기록 업데이트 스키마
class RecordUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    record_date: Optional[str] = None
    record_data: Optional[Dict[str, Any]] = None  # 기록 유형별 데이터 업데이트
    
    @validator('record_date')
    def validate_record_date(cls, v):
        if v is not None and len(v.strip()) > 0:
            try:
                from datetime import datetime
                datetime.strptime(v.strip(), '%Y-%m-%d')
                return v.strip()
            except ValueError:
                raise ValueError('기록 날짜는 YYYY-MM-DD 형식으로 입력해주세요')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('제목은 비어있을 수 없습니다')
            if len(v) > 100:
                raise ValueError('제목은 100자 이하여야 합니다')
            return v.strip()
        return v