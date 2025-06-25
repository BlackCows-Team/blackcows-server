# schemas/ai_prediction.py

from pydantic import BaseModel, validator, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum

# 예측 모델 타입
class PredictionModelType(str, Enum):
    DISEASE_PREDICTION = "disease_prediction"           # 질병 예측
    BREEDING_SUCCESS = "breeding_success"               # 수정 성공률 예측
    CALVING_DATE = "calving_date"                      # 분만 예정일 예측
    FEED_EFFICIENCY = "feed_efficiency"                # 사료 효율 분석
    MILK_QUALITY = "milk_quality"                      # 유성분 품질 예측
    GROWTH_PREDICTION = "growth_prediction"            # 초산우 성장 예측

# 질병 타입
class DiseaseType(str, Enum):
    MASTITIS = "mastitis"                              # 유방염
    METABOLIC_DISORDER = "metabolic_disorder"          # 대사성 질환
    LUMPY_SKIN = "lumpy_skin"                         # 럼피스킨병
    DIGESTIVE_DISORDER = "digestive_disorder"          # 소화기 질환

# 위험도 등급
class RiskLevel(str, Enum):
    LOW = "low"                                        # 낮음
    MEDIUM = "medium"                                  # 보통
    HIGH = "high"                                      # 높음
    CRITICAL = "critical"                              # 위험

# 효율 등급
class EfficiencyGrade(str, Enum):
    EXCELLENT = "excellent"                            # 우수
    GOOD = "good"                                      # 양호
    AVERAGE = "average"                                # 보통
    POOR = "poor"                                      # 부족

# ===== 질병 예측 요청/응답 =====
class DiseasesPredictionRequest(BaseModel):
    cow_id: str = Field(..., description="젖소 ID")
    # 착유 데이터
    milk_yield: Optional[float] = Field(None, description="착유량 (L)")
    somatic_cell_count: Optional[int] = Field(None, description="체세포수")
    conductivity: Optional[float] = Field(None, description="전도도")
    temperature: Optional[float] = Field(None, description="온도 (°C)")
    fat_percentage: Optional[float] = Field(None, description="유지방 비율 (%)")
    protein_percentage: Optional[float] = Field(None, description="유단백 비율 (%)")
    # 사료 데이터
    feed_intake: Optional[float] = Field(None, description="사료 섭취량 (kg)")
    # 개체 정보
    lactation_number: Optional[int] = Field(None, description="산차수")
    days_in_milk: Optional[int] = Field(None, description="착유일수")
    # 기존 데이터 사용 여부
    use_historical_data: bool = Field(True, description="기존 데이터 활용 여부")

class DiseasePredictionResult(BaseModel):
    disease_type: DiseaseType
    probability: float = Field(..., ge=0, le=1, description="발병 확률 (0-1)")
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0, le=1, description="예측 신뢰도")

class DiseasesPredictionResponse(BaseModel):
    cow_id: str
    cow_name: str
    ear_tag_number: str
    prediction_results: List[DiseasePredictionResult]
    overall_health_score: float = Field(..., ge=0, le=100, description="전체 건강 점수")
    recommendations: List[str] = Field(default=[], description="관리 권장사항")
    prediction_date: datetime
    model_version: str

# ===== 번식 성공률 예측 =====
class BreedingSuccessPredictionRequest(BaseModel):
    cow_id: str = Field(..., description="젖소 ID")
    # 번식 이력
    lactation_number: Optional[int] = Field(None, description="산차수")
    days_since_calving: Optional[int] = Field(None, description="분만 후 경과일")
    previous_breeding_attempts: Optional[int] = Field(None, description="이전 수정 횟수")
    body_condition_score: Optional[float] = Field(None, description="체형점수 (1-5)")
    # 현재 상태
    milk_yield: Optional[float] = Field(None, description="현재 착유량")
    feed_intake: Optional[float] = Field(None, description="사료 섭취량")
    use_historical_data: bool = Field(True, description="기존 데이터 활용 여부")

class BreedingSuccessPredictionResponse(BaseModel):
    cow_id: str
    cow_name: str
    ear_tag_number: str
    success_probability: float = Field(..., ge=0, le=1, description="수정 성공 확률")
    optimal_breeding_window: Dict[str, str] = Field(default={}, description="최적 수정 시기")
    risk_factors: List[str] = Field(default=[], description="위험 요소")
    recommendations: List[str] = Field(default=[], description="관리 권장사항")
    prediction_date: datetime
    model_version: str

# ===== 분만 예정일 예측 =====
class CalvingDatePredictionRequest(BaseModel):
    cow_id: str = Field(..., description="젖소 ID")
    insemination_date: date = Field(..., description="수정일")
    lactation_number: Optional[int] = Field(None, description="산차수")
    previous_gestation_period: Optional[int] = Field(None, description="이전 임신 기간")
    breed: Optional[str] = Field(None, description="품종")
    use_historical_data: bool = Field(True, description="기존 데이터 활용 여부")

class CalvingDatePredictionResponse(BaseModel):
    cow_id: str
    cow_name: str
    ear_tag_number: str
    predicted_calving_date: date
    confidence_interval: Dict[str, date] = Field(default={}, description="신뢰구간 (최소/최대일)")
    gestation_period_days: int = Field(..., description="예상 임신 기간")
    preparation_recommendations: List[str] = Field(default=[], description="분만 준비 사항")
    prediction_date: datetime
    model_version: str

# ===== 사료 효율 분석 =====
class FeedEfficiencyAnalysisRequest(BaseModel):
    cow_id: str = Field(..., description="젖소 ID")
    # 사료 데이터
    daily_feed_intake: float = Field(..., description="일일 사료 섭취량 (kg)")
    feed_type: Optional[str] = Field(None, description="사료 종류")
    # 생산 데이터
    daily_milk_yield: float = Field(..., description="일일 착유량 (L)")
    # 개체 정보
    body_weight: Optional[float] = Field(None, description="체중 (kg)")
    lactation_number: Optional[int] = Field(None, description="산차수")
    days_in_milk: Optional[int] = Field(None, description="착유일수")
    # 분석 기간
    analysis_period_days: int = Field(7, description="분석 기간 (일)", ge=1, le=30)

class FeedEfficiencyAnalysisResponse(BaseModel):
    cow_id: str
    cow_name: str
    ear_tag_number: str
    feed_efficiency_ratio: float = Field(..., description="사료 효율 비율 (L우유/kg사료)")
    efficiency_grade: EfficiencyGrade
    benchmark_comparison: Dict[str, float] = Field(default={}, description="벤치마크 대비 비교")
    optimization_suggestions: List[str] = Field(default=[], description="최적화 제안")
    predicted_optimal_intake: float = Field(..., description="최적 사료 섭취량 예측")
    analysis_date: datetime
    model_version: str

# ===== 유성분 품질 예측 =====
class MilkQualityPredictionRequest(BaseModel):
    cow_id: str = Field(..., description="젖소 ID")
    # 현재 상태
    current_feed_intake: float = Field(..., description="현재 사료 섭취량")
    lactation_number: Optional[int] = Field(None, description="산차수")
    days_in_milk: Optional[int] = Field(None, description="착유일수")
    # 환경 요인
    season: Optional[str] = Field(None, description="계절")
    weather_condition: Optional[str] = Field(None, description="날씨 상태")
    # 예측 기간
    prediction_days: int = Field(7, description="예측 기간 (일)", ge=1, le=30)

class MilkQualityPrediction(BaseModel):
    date: date
    fat_percentage: float = Field(..., description="유지방 비율 예측")
    protein_percentage: float = Field(..., description="유단백 비율 예측")
    solid_not_fat: float = Field(..., description="무지고형분 예측")
    quality_grade: str = Field(..., description="품질 등급")

class MilkQualityPredictionResponse(BaseModel):
    cow_id: str
    cow_name: str
    ear_tag_number: str
    quality_predictions: List[MilkQualityPrediction]
    average_quality_score: float = Field(..., ge=0, le=100, description="평균 품질 점수")
    improvement_recommendations: List[str] = Field(default=[], description="품질 개선 제안")
    prediction_date: datetime
    model_version: str

# ===== 초산우 성장 예측 =====
class GrowthPredictionRequest(BaseModel):
    cow_id: str = Field(..., description="젖소 ID")
    # 현재 상태
    current_age_months: int = Field(..., description="현재 월령")
    current_weight: Optional[float] = Field(None, description="현재 체중")
    current_milk_yield: Optional[float] = Field(None, description="현재 착유량")
    # 유전 정보
    mother_peak_yield: Optional[float] = Field(None, description="어미 최고 착유량")
    breed: Optional[str] = Field(None, description="품종")
    # 관리 정보
    nutrition_level: Optional[str] = Field(None, description="영양 수준")

class GrowthPredictionResponse(BaseModel):
    cow_id: str
    cow_name: str
    ear_tag_number: str
    predicted_peak_yield: float = Field(..., description="예상 최고 착유량")
    predicted_mature_weight: float = Field(..., description="예상 성우 체중")
    growth_potential_score: float = Field(..., ge=0, le=100, description="성장 잠재력 점수")
    milestone_predictions: Dict[str, Any] = Field(default={}, description="성장 이정표 예측")
    management_recommendations: List[str] = Field(default=[], description="관리 권장사항")
    prediction_date: datetime
    model_version: str

# ===== 통합 예측 요청 =====
class ComprehensivePredictionRequest(BaseModel):
    cow_id: str = Field(..., description="젖소 ID")
    prediction_types: List[PredictionModelType] = Field(..., description="요청할 예측 타입들")
    # 공통 데이터 (각 예측에서 필요한 것만 사용)
    milk_yield: Optional[float] = None
    feed_intake: Optional[float] = None
    somatic_cell_count: Optional[int] = None
    conductivity: Optional[float] = None
    lactation_number: Optional[int] = None
    days_in_milk: Optional[int] = None
    body_condition_score: Optional[float] = None
    use_historical_data: bool = Field(True, description="기존 데이터 활용 여부")

class ComprehensivePredictionResponse(BaseModel):
    cow_id: str
    cow_name: str
    ear_tag_number: str
    predictions: Dict[str, Any] = Field(default={}, description="각 예측 결과")
    overall_summary: Dict[str, Any] = Field(default={}, description="전체 요약")
    priority_actions: List[str] = Field(default=[], description="우선 조치 사항")
    prediction_date: datetime