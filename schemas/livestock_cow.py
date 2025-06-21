# schemas/livestock_cow.py

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime

class CowRegisterFromLivestockTrace(BaseModel):
    """축산물이력제 정보 기반 젖소 등록 요청 스키마"""
    ear_tag_number: str                          # 이표번호 (필수)
    user_provided_name: str                      # 사용자가 지어준 젖소 이름 (필수)
    use_livestock_trace_data: bool = True        # 축산물이력제 데이터 사용 여부
    sensor_number: Optional[str] = None          # 센서 번호 (선택)
    additional_notes: Optional[str] = None       # 추가 메모 (선택)
    
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
    
    @validator('user_provided_name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('젖소 이름은 필수입니다')
        if len(v) > 15:
            raise ValueError('젖소 이름은 15자 이하여야 합니다')
        return v.strip()

class RegistrationStatusResponse(BaseModel):
    """젖소 등록 상태 응답 스키마"""
    status: str                                  # 등록 상태
    ear_tag_number: str                          # 이표번호
    message: str                                 # 상태 메시지
    livestock_trace_data: Optional[Dict[str, Any]] = None    # 축산물이력제 데이터
    existing_cow_info: Optional[Dict[str, Any]] = None       # 이미 등록된 젖소 정보
    
class LivestockTraceRegistrationResponse(BaseModel):
    """축산물이력제 기반 젖소 등록 응답 스키마"""
    success: bool
    message: str
    cow_id: Optional[str] = None
    cow_info: Optional[Dict[str, Any]] = None
    livestock_trace_data: Optional[Dict[str, Any]] = None