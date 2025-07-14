# routers/ai_prediction.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from schemas.ai_prediction import (
    MilkYieldPredictionRequest,
    PredictionBatchRequest
)
from services.ai_prediction_service import AIPredictionService
from routers.auth_firebase import get_current_user

router = APIRouter(tags=["AI 예측"])

@router.post("/milk-yield/predict",
             summary="착유량 예측",
             description="""
             젖소의 8개 특성(feature)을 바탕으로 착유량을 예측합니다.
             
             **필요한 입력:**
             - 착유횟수, 전도율, 온도, 유지방비율, 유단백비율
             - 농후사료섭취량, 착유기측정월, 착유기측정요일
             
             **결과:**
             - 예상 착유량 (리터)
             """)
async def predict_milk_yield(
    prediction_request: MilkYieldPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """개별 젖소 착유량 예측"""
    return await AIPredictionService.predict_milk_yield(prediction_request, current_user)

@router.post("/milk-yield/batch-predict",
             summary="다중 젖소 착유량 예측",
             description="여러 젖소의 착유량을 한번에 예측합니다.")
async def predict_milk_yield_batch(
    batch_request: PredictionBatchRequest,
    current_user: dict = Depends(get_current_user)
):
    """다중 젖소 착유량 일괄 예측"""
    return await AIPredictionService.predict_milk_yield_batch(batch_request, current_user)

# ===== 테스트/개발용 엔드포인트 =====

@router.get("/test/sample-predict", summary="샘플 예측 테스트(비인증)", description="AI 서버가 실제 예측 가능한지 샘플 데이터로 테스트합니다.")
async def test_sample_predict():
    class SampleRequest:
        def __init__(self):
            self.cow_id = "test_cow"
            self.milking_frequency = 2
            self.conductivity = 7.7
            self.temperature = 38.5
            self.fat_percentage = 3.8
            self.protein_percentage = 3.2
            self.concentrate_intake = 3.5
            self.milking_month = 6
            self.milking_day_of_week = 1
            self.prediction_date = "2025-01-17"
            self.notes = "sample test"
    sample_request = SampleRequest()
    return await AIPredictionService.predict_milk_yield(sample_request, current_user={})

# @router.get("/test/model-health",
#            summary="모델 상태 확인",
#            description="AI 모델 로드 및 예측 상태를 확인합니다.")
# async def check_model_health():
#     """모델 서빙 상태 확인"""
#     return await AIPredictionService.check_model_health()