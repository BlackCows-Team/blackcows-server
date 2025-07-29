# routers/ai_prediction.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from schemas.ai_prediction import (
    MilkYieldPredictionRequest,
    MastitisPredictionRequest,
    SCCMastitisPredictionRequest,
    PredictionBatchRequest,
    MastitisBatchRequest,
    SCCMastitisBatchRequest
)
from services.ai_prediction_service import AIPredictionService
from routers.auth_firebase import get_current_user

router = APIRouter(tags=["AI 예측"])

# ===== 착유량 예측 API =====

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


# ===== 유방염 예측 API ===== #

@router.post("/mastitis/predict",
             summary="유방염 예측",
             description="""
             젖소의 5개 특성을 바탕으로 유방염 위험도를 분류합니다.
             
             **필요한 입력:**
             - 착유량, 전도율, 유지방비율, 유단백비율, 산차수
             
             **결과:**
             - 예측 클래스: 정상, 주의, 염증 가능성
             - 신뢰도 점수
             """)
async def predict_mastitis(
    prediction_request: MastitisPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """개별 젖소 유방염 예측"""
    return await AIPredictionService.predict_mastitis(prediction_request, current_user)

@router.post("/mastitis/batch-predict",
             summary="다중 젖소 유방염 예측",
             description="여러 젖소의 유방염 위험도를 한번에 예측합니다.")
async def predict_mastitis_batch(
    batch_request: MastitisBatchRequest,
    current_user: dict = Depends(get_current_user)
):
    """다중 젖소 유방염 일괄 예측"""
    return await AIPredictionService.predict_mastitis_batch(batch_request, current_user)

# ===== 체세포수 기반 유방염 예측 API ===== #

@router.post("/scc-mastitis/predict",
             summary="체세포수 기반 유방염 예측",
             description="""
             젖소의 체세포수를 바탕으로 유방염 위험도를 분류합니다.
             
             **필요한 입력:**
             - 체세포수 (somatic_cell_count)
             
             **결과:**
             - 예측 클래스: 정상, 주의, 위험
             - 신뢰도 점수
             """)
async def predict_scc_mastitis(
    prediction_request: SCCMastitisPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """개별 젖소 체세포수 기반 유방염 예측"""
    return await AIPredictionService.predict_scc_mastitis(prediction_request, current_user)

@router.post("/scc-mastitis/batch-predict",
             summary="다중 젖소 체세포수 기반 유방염 예측",
             description="여러 젖소의 체세포수 기반 유방염 위험도를 한번에 예측합니다.")
async def predict_scc_mastitis_batch(
    batch_request: SCCMastitisBatchRequest,
    current_user: dict = Depends(get_current_user)
):
    """다중 젖소 체세포수 기반 유방염 일괄 예측"""
    return await AIPredictionService.predict_scc_mastitis_batch(batch_request, current_user)

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

@router.post("/test/milk-yield-predict", summary="착유량 예측 테스트(비인증)", description="인증 없이 착유량 예측을 테스트할 수 있습니다.")
async def test_milk_yield_predict(prediction_request: MilkYieldPredictionRequest):
    """테스트용 착유량 예측 (인증 불필요)"""
    return await AIPredictionService.predict_milk_yield(prediction_request, current_user={})

@router.get("/test/sample-mastitis-predict", summary="샘플 유방염 예측 테스트(비인증)", description="AI 서버가 실제 유방염 예측 가능한지 샘플 데이터로 테스트합니다.")
async def test_sample_mastitis_predict():
    """유방염 예측 샘플 테스트"""
    class SampleMastitisRequest:
        def __init__(self):
            self.cow_id = "test_cow"
            self.milk_yield = 25.5
            self.conductivity = 7.7
            self.fat_percentage = 3.8
            self.protein_percentage = 3.2
            self.lactation_number = 2
            self.prediction_date = "2025-01-17"
            self.notes = "sample mastitis test"
    
    sample_request = SampleMastitisRequest()
    return await AIPredictionService.predict_mastitis(sample_request, current_user={})

@router.post("/test/mastitis-predict", summary="유방염 예측 테스트(비인증)", description="인증 없이 유방염 예측을 테스트할 수 있습니다.")
async def test_mastitis_predict(prediction_request: MastitisPredictionRequest):
    """테스트용 유방염 예측 (인증 불필요)"""
    return await AIPredictionService.predict_mastitis(prediction_request, current_user={})

@router.get("/test/sample-scc-mastitis-predict", summary="샘플 체세포수 기반 유방염 예측 테스트(비인증)", description="AI 서버가 실제 체세포수 기반 유방염 예측 가능한지 샘플 데이터로 테스트합니다.")
async def test_sample_scc_mastitis_predict():
    """체세포수 기반 유방염 예측 샘플 테스트"""
    class SampleSCCMastitisRequest:
        def __init__(self):
            self.cow_id = "test_cow"
            self.somatic_cell_count = 145
            self.prediction_date = "2025-01-17"
            self.notes = "sample scc mastitis test"
    
    sample_request = SampleSCCMastitisRequest()
    return await AIPredictionService.predict_scc_mastitis(sample_request, current_user={})

@router.post("/test/scc-mastitis-predict", summary="체세포수 기반 유방염 예측 ", description="인증 없이 체세포수 기반 유방염 예측을 테스트할 수 있습니다.")
async def test_scc_mastitis_predict(prediction_request: SCCMastitisPredictionRequest):
    """테스트용 체세포수 기반 유방염 예측 (인증 불필요)"""
    return await AIPredictionService.predict_scc_mastitis(prediction_request, current_user={})

@router.get("/health",
           summary="AI 서버 상태 확인",
           description="AI 서버 연결 상태 및 모델 상태를 확인합니다.")
async def check_ai_server_health():
    """AI 서버 연결 및 모델 상태 확인"""
    return await AIPredictionService.check_ai_server_health()