# schemas/ai_prediction.py

from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 예측 요청 스키마
class MilkYieldPredictionRequest(BaseModel):
    cow_id: Optional[str] = Field(None, description="젖소 ID (선택사항)")
    
    # 필수 예측 변수들 (모델 학습에 사용된 8개 특성)
    milking_frequency: int = Field(..., description="착유횟수 (1-4회)", ge=1, le=4)
    conductivity: float = Field(..., description="전도율", ge=0)
    temperature: float = Field(..., description="온도 (°C)", ge=-10, le=50)
    fat_percentage: float = Field(..., description="유지방비율 (%)", ge=0, le=10)
    protein_percentage: float = Field(..., description="유단백비율 (%)", ge=0, le=10)
    concentrate_intake: float = Field(..., description="농후사료섭취량 (kg)", ge=0)
    milking_month: int = Field(..., description="착유기측정월 (1-12)", ge=1, le=12)
    milking_day_of_week: int = Field(..., description="착유기측정요일 (0:월요일~6:일요일)", ge=0, le=6)
    
    # 추가 메타데이터
    prediction_date: Optional[str] = Field(None, description="예측 기준일 (YYYY-MM-DD)")
    notes: Optional[str] = Field(None, description="예측 관련 메모")
    
    @validator('prediction_date')
    def validate_prediction_date(cls, v):
        if v is not None and len(v.strip()) > 0:
            try:
                datetime.strptime(v.strip(), '%Y-%m-%d')
                return v.strip()
            except ValueError:
                raise ValueError('예측 기준일은 YYYY-MM-DD 형식으로 입력해주세요')
        return v

# 유방염 예측 요청 스키마
class MastitisPredictionRequest(BaseModel):
    cow_id: Optional[str] = Field(None, description="젖소 ID (선택사항)")
    
    # 필수 예측 변수들 (유방염 예측에 사용되는 5개 특성)
    milk_yield: float = Field(..., description="착유량 (리터)", ge=0)
    conductivity: float = Field(..., description="전도율", ge=0)
    fat_percentage: float = Field(..., description="유지방비율 (%)", ge=0, le=10)
    protein_percentage: float = Field(..., description="유단백비율 (%)", ge=0, le=10)
    lactation_number: int = Field(..., description="산차수", ge=1)
    
    # 추가 메타데이터
    prediction_date: Optional[str] = Field(None, description="예측 기준일 (YYYY-MM-DD)")
    notes: Optional[str] = Field(None, description="예측 관련 메모")
    
    @validator('prediction_date')
    def validate_prediction_date(cls, v):
        if v is not None and len(v.strip()) > 0:
            try:
                datetime.strptime(v.strip(), '%Y-%m-%d')
                return v.strip()
            except ValueError:
                raise ValueError('예측 기준일은 YYYY-MM-DD 형식으로 입력해주세요')
        return v

# 배치 예측 요청 스키마
class PredictionBatchRequest(BaseModel):
    predictions: List[MilkYieldPredictionRequest] = Field(..., description="예측 요청 목록")
    batch_name: Optional[str] = Field(None, description="배치 이름")

# 유방염 배치 예측 요청 스키마
class MastitisBatchRequest(BaseModel):
    predictions: List[MastitisPredictionRequest] = Field(..., description="유방염 예측 요청 목록")
    batch_name: Optional[str] = Field(None, description="배치 이름")

# 에러 응답 스키마
class PredictionErrorResponse(BaseModel):
    error_code: str = Field(..., description="에러 코드")
    error_message: str = Field(..., description="에러 메시지")
    error_details: Optional[Dict[str, Any]] = Field(None, description="에러 상세 정보")
    suggestion: Optional[str] = Field(None, description="해결 방법 제안")