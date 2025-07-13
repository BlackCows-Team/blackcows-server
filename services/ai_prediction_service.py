# services/ai_prediction_service.py

import joblib
import numpy as np
import uuid
import time
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException, status
from pathlib import Path
import logging
from datetime import timezone, timedelta

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))
class AIPredictionService:
    
    MODEL_VERSION = "v1.0.0"
    
    # 로컬 모델 경로
    BASE_DIR = Path(__file__).parent.parent
    MODELS_DIR = BASE_DIR / "models"
    MODEL_PATH = MODELS_DIR / "1_random_forest.pkl"
    SCALER_PATH = MODELS_DIR / "1_scaler.pkl"
    
    # 캐시된 모델 (메모리에 한 번만 로드)
    _cached_model = None
    _cached_scaler = None
    _cache_loaded = False
    
    @classmethod
    def _load_models(cls):
        """로컬에서 모델 로드 (실패해도 서버는 계속 실행)"""
        if cls._cache_loaded:
            return cls._cached_model, cls._cached_scaler
        
        try:
            logger.info("🔧 모델 로드 중...")
            
            if not cls.MODEL_PATH.exists():
                raise FileNotFoundError(f"모델 파일 없음: {cls.MODEL_PATH}")
                cls._cache_loaded = True  # 재시도 방지
                return None, None
            if not cls.SCALER_PATH.exists():
                raise FileNotFoundError(f"스케일러 파일 없음: {cls.SCALER_PATH}")
                cls._cache_loaded = True  # 재시도 방지
                return None, None
            
            start_time = time.time()
            cls._cached_scaler = joblib.load(cls.SCALER_PATH)
            cls._cached_model = joblib.load(cls.MODEL_PATH)
            cls._cache_loaded = True
            
            load_time = time.time() - start_time
            logger.info(f"✅ 모델 로드 완료: {load_time:.2f}초")
            
            return cls._cached_model, cls._cached_scaler
            
        except Exception as e:
            logger.error(f"❌ 모델 로드 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI 모델 로드 실패: {str(e)}"
            )
    
    @classmethod
    def _prepare_features(cls, request) -> np.ndarray:
        """8개 특성을 numpy 배열로 변환"""
        features = np.array([
            request.milking_frequency,    # 착유횟수
            request.conductivity,         # 전도율  
            request.temperature,          # 온도
            request.fat_percentage,       # 유지방비율
            request.protein_percentage,   # 유단백비율
            request.concentrate_intake,   # 농후사료섭취량
            request.milking_month,        # 착유기측정월
            request.milking_day_of_week   # 착유기측정요일
        ]).reshape(1, -1)
        
        return features
    
    @classmethod
    async def predict_milk_yield(cls, request, current_user: Dict) -> Dict[str, Any]:
        """착유량 예측 (확신도 제거) (모델 없으면 에러 응답)"""
        start_time = time.time()
        
        try:
            # 모델 로드
            model, scaler = cls._load_models()
            
            # 모델이 로드되지 않은 경우
            if model is None or scaler is None:
                logger.warning("AI 모델이 로드되지 않음 - 서비스 불가")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error_code": "MODEL_NOT_AVAILABLE",
                        "error_message": "AI 모델을 사용할 수 없습니다",
                        "reason": "모델 파일이 없거나 로드에 실패했습니다",
                        "suggestion": "잠시 후 다시 시도하거나 관리자에게 문의하세요",
                        "available_features": ["기본 기록 관리", "소 관리", "할일 관리"],
                        "unavailable_features": ["AI 착유량 예측"]
                    }
                )
            
            # 특성 준비
            features = cls._prepare_features(request)
            
            # 스케일링 및 예측
            scaled_features = scaler.transform(features)
            prediction = model.predict(scaled_features)[0]
            
            # 처리 시간
            processing_time = (time.time() - start_time) * 1000
            
            # 응답 생성 (확신도 제거)
            response = {
                "prediction_id": str(uuid.uuid4()),
                "cow_id": getattr(request, 'cow_id', None),
                "predicted_milk_yield": round(float(prediction), 2),
                "ai_accuracy": 82,  # 고정값 (R² 기준)
                "input_features": {
                    "착유횟수": request.milking_frequency,
                    "전도율": request.conductivity,
                    "온도": request.temperature,
                    "유지방비율": request.fat_percentage,
                    "유단백비율": request.protein_percentage,
                    "농후사료섭취량": request.concentrate_intake,
                    "착유기측정월": request.milking_month,
                    "착유기측정요일": request.milking_day_of_week
                },
                "model_version": cls.MODEL_VERSION,
                "prediction_time": datetime.utcnow(),
                "processing_time_ms": round(processing_time, 2)
            }
            
            logger.info(f"예측 완료: {prediction:.2f}L ({processing_time:.1f}ms)")
            return response
            
        except Exception as e:
            logger.error(f"예측 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "PREDICTION_FAILED",
                    "error_message": "예측 처리 중 오류가 발생했습니다",
                    "reason": str(e),
                    "suggestion": "입력값을 확인하고 다시 시도하세요"
                }
            )
    
    @classmethod
    async def predict_milk_yield_batch(cls, batch_request, current_user: Dict) -> Dict[str, Any]:
        """다중 젖소 착유량 일괄 예측"""
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            predictions = []
            successful = 0
            failed = 0
            
            for request in batch_request.predictions:
                try:
                    prediction = await cls.predict_milk_yield(request, current_user)
                    predictions.append(prediction)
                    successful += 1
                except Exception as e:
                    logger.error(f"배치 예측 중 개별 실패: {str(e)}")
                    failed += 1
            
            total_time = time.time() - start_time
            
            return {
                "batch_id": batch_id,
                "total_predictions": len(batch_request.predictions),
                "successful_predictions": successful,
                "failed_predictions": failed,
                "predictions": predictions,
                "batch_created_at": datetime.utcnow(),
                "total_processing_time_ms": round(total_time * 1000, 2)
            }
                
        except Exception as e:
            logger.error(f"배치 예측 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "BATCH_PREDICTION_FAILED", 
                    "error_message": "배치 예측 처리 중 오류가 발생했습니다",
                    "batch_id": batch_id,
                    "reason": str(e)
                }
            )
    
    @classmethod
    async def check_model_health(cls) -> Dict[str, Any]:
        """모델 상태 확인"""
        try:
            start_time = time.time()
            
            # 파일 존재 확인
            model_exists = cls.MODEL_PATH.exists()
            scaler_exists = cls.SCALER_PATH.exists()
            
            # 모델 로드 및 테스트
            model_load_success = False
            prediction_test_success = False
            
            try:
                model, scaler = cls._load_models()
                if model is not None and scaler is not None:
                    model_load_success = True
                
                    # 테스트 예측
                    test_features = np.array([[2, 7.5, 38.5, 3.8, 3.2, 3.5, 6, 1]])
                    test_scaled = scaler.transform(test_features)
                    test_prediction = model.predict(test_scaled)[0]
                    prediction_test_success = True
                
            except Exception as e:
                logger.error(f"모델 테스트 실패: {e}")
            
            response_time = (time.time() - start_time) * 1000
            
                        # 상태 결정
            if model_exists and scaler_exists and model_load_success and prediction_test_success:
                status = "healthy"
                message = "AI 예측 서비스가 정상 작동 중입니다"
            elif model_exists and scaler_exists:
                status = "degraded" 
                message = "모델 파일은 존재하지만 로드 또는 테스트에 실패했습니다"
            else:
                status = "unavailable"
                message = "AI 예측 서비스를 사용할 수 없습니다"
            
            return {
                "status": status,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "response_time_ms": round(response_time, 2),
                "checks": {
                    "model_file_exists": model_exists,
                    "scaler_file_exists": scaler_exists,
                    "model_load_success": model_load_success,
                    "prediction_test_success": prediction_test_success,
                    "cache_loaded": cls._cache_loaded
                },
                "model_info": {
                    "version": cls.MODEL_VERSION,
                    "cached": cls._cache_loaded,
                    "available": model_load_success
                },
                "recommendations": {
                    "healthy": "모든 기능을 정상적으로 사용할 수 있습니다",
                    "degraded": "AI 예측 기능에 문제가 있습니다. 관리자에게 문의하세요",
                    "unavailable": "AI 예측 기능을 사용할 수 없습니다. 다른 기능은 정상 작동합니다"
                }.get(status, "상태를 확인할 수 없습니다")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": "모델 상태 확인 중 오류가 발생했습니다",
                "timestamp": datetime.now(KST).isoformat(),
                "error": str(e),
                "recommendations": "서버 관리자에게 문의하세요"
            }
    @classmethod
    async def test_prediction_with_sample(cls) -> Dict[str, Any]:
        """샘플 테스트"""
        try:
            # 샘플 데이터 클래스
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
            
            sample_request = SampleRequest()
            test_user = {"id": "test", "farm_id": "test"}
            
            result = await cls.predict_milk_yield(sample_request, test_user)
            
            return {
                "test_status": "success",
                "sample_input": {
                    "착유횟수": 2,
                    "전도율": 7.7,
                    "온도": 38.5,
                    "유지방비율": 3.8,
                    "유단백비율": 3.2,
                    "농후사료섭취량": 3.5,
                    "착유기측정월": 6,
                    "착유기측정요일": 1
                },
                "predicted_milk_yield": result["predicted_milk_yield"],
                "ai_accuracy": result["ai_accuracy"],
                "processing_time_ms": result["processing_time_ms"],
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_status": "failed",
                "error": str(e),
                "test_timestamp": datetime.utcnow().isoformat()
            }

# 애플리케이션 시작시 모델 로드
def initialize_models():
    """서버 시작시 모델 초기화"""
    try:
        AIPredictionService._load_models()
        logger.info("🎉 AI 서비스 초기화 완료")
        return True
    except Exception as e:
        logger.warning(f"⚠️ AI 서비스 초기화 실패: {e}")
        logger.info("📱 다른 기능들은 정상 작동합니다")
        return False