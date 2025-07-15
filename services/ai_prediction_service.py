# services/ai_prediction_service.py

import httpx
import uuid
import time
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException, status
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class AIPredictionService:
    
    MODEL_VERSION = "v2.0.0"
    
    # AI 서버 URL (Cloudflare Tunnel 고정 도메인)
    AI_SERVER_URL = "https://feof-implement-finnish-finally.trycloudflare.com"
    
    # HTTP 클라이언트 설정
    timeout = httpx.Timeout(30.0)  # 30초 타임아웃
    
    @classmethod
    async def _make_ai_request(cls, endpoint: str, payload: dict) -> dict:
        """AI 서버로 HTTP 요청"""
        try:
            async with httpx.AsyncClient(timeout=cls.timeout) as client:
                response = await client.post(
                    f"{cls.AI_SERVER_URL}{endpoint}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail={
                            "error_code": "AI_MODEL_UNAVAILABLE",
                            "error_message": "AI 모델을 사용할 수 없습니다",
                            "reason": "AI 서버의 모델이 로드되지 않았습니다",
                            "suggestion": "잠시 후 다시 시도하거나 관리자에게 문의하세요"
                        }
                    )
                else:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"detail": "Unknown error"}
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_data
                    )
                    
        except httpx.TimeoutException:
            logger.error("AI 서버 요청 타임아웃")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "error_code": "AI_SERVER_TIMEOUT",
                    "error_message": "AI 서버 응답 시간이 초과되었습니다",
                    "suggestion": "잠시 후 다시 시도해주세요"
                }
            )
        except httpx.ConnectError:
            logger.error("AI 서버 연결 실패")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error_code": "AI_SERVER_UNAVAILABLE",
                    "error_message": "AI 서버에 연결할 수 없습니다",
                    "suggestion": "잠시 후 다시 시도하거나 관리자에게 문의하세요"
                }
            )
        except Exception as e:
            logger.error(f"AI 서버 요청 중 예상치 못한 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "AI_REQUEST_FAILED",
                    "error_message": "AI 예측 요청 처리 중 오류가 발생했습니다",
                    "reason": str(e)
                }
            )
    
    @classmethod
    async def predict_milk_yield(cls, request, current_user: Dict) -> Dict[str, Any]:
        """착유량 예측 - AI 서버로 요청 전달"""
        start_time = time.time()
        
        logger.info(f"사용자 {current_user.get('user_id')}의 AI 예측 요청 시작")
        
        try:
            # AI 서버로 보낼 페이로드 구성
            payload = {
                "cow_id": getattr(request, 'cow_id', None),
                "milking_frequency": request.milking_frequency,
                "conductivity": request.conductivity,
                "temperature": request.temperature,
                "fat_percentage": request.fat_percentage,
                "protein_percentage": request.protein_percentage,
                "concentrate_intake": request.concentrate_intake,
                "milking_month": request.milking_month,
                "milking_day_of_week": request.milking_day_of_week,
                "prediction_date": getattr(request, 'prediction_date', None),
                "notes": getattr(request, 'notes', None)
            }
            
            # AI 서버로 예측 요청
            ai_response = await cls._make_ai_request("/ai/milk-yield/predict", payload)
            
            # AWS EC2 서버에서 추가 메타데이터 보강
            enhanced_response = {
                **ai_response,
                "user_id": current_user.get("user_id"),
                "farm_id": current_user.get("farm_id"),
                "requested_at": datetime.utcnow().isoformat(),
                "server_processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            logger.info(f"AI 예측 완료 - 결과: {ai_response.get('predicted_milk_yield')}L")
            return enhanced_response
            
        except HTTPException:
            # AI 서버에서 발생한 HTTP 예외는 그대로 전달
            raise
        except Exception as e:
            logger.error(f"예측 처리 중 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "PREDICTION_PROCESSING_FAILED",
                    "error_message": "예측 처리 중 오류가 발생했습니다",
                    "reason": str(e)
                }
            )
    
    # 유방염 예측
    @classmethod
    async def predict_mastitis(cls, request, current_user: Dict) -> Dict[str, Any]:
        """유방염 예측 - AI 서버로 요청 전달"""
        start_time = time.time()
        
        logger.info(f"사용자 {current_user.get('user_id')}의 유방염 예측 요청 시작")
        
        try:
            # AI 서버로 보낼 페이로드 구성
            payload = {
                "cow_id": getattr(request, 'cow_id', None),
                "milk_yield": request.milk_yield,
                "conductivity": request.conductivity,
                "fat_percentage": request.fat_percentage,
                "protein_percentage": request.protein_percentage,
                "lactation_number": request.lactation_number,
                "prediction_date": getattr(request, 'prediction_date', None),
                "notes": getattr(request, 'notes', None)
            }
            
            # AI 서버로 예측 요청
            ai_response = await cls._make_ai_request("/ai/mastitis/predict", payload)
            
            # AWS EC2 서버에서 추가 메타데이터 보강
            enhanced_response = {
                **ai_response,
                "user_id": current_user.get("user_id"),
                "farm_id": current_user.get("farm_id"),
                "requested_at": datetime.utcnow().isoformat(),
                "server_processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            logger.info(f"유방염 예측 완료 - 결과: {ai_response.get('prediction_class')}")
            return enhanced_response
            
        except HTTPException:
            # AI 서버에서 발생한 HTTP 예외는 그대로 전달
            raise
        except Exception as e:
            logger.error(f"유방염 예측 처리 중 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "MASTITIS_PREDICTION_PROCESSING_FAILED",
                    "error_message": "유방염 예측 처리 중 오류가 발생했습니다",
                    "reason": str(e)
                }
            )

    #체세포수 기반 유방염 예측
    @classmethod
    async def predict_scc_mastitis(cls, request, current_user: Dict) -> Dict[str, Any]:
        """체세포수 기반 유방염 예측 - AI 서버로 요청 전달"""
        start_time = time.time()
        
        logger.info(f"사용자 {current_user.get('user_id')}의 체세포수 기반 유방염 예측 요청 시작")
        
        try:
            # AI 서버로 보낼 페이로드 구성 (체세포수만 전송)
            payload = {
                "cow_id": getattr(request, 'cow_id', None),
                "somatic_cell_count": request.somatic_cell_count,
                "prediction_date": getattr(request, 'prediction_date', None),
                "notes": getattr(request, 'notes', None)
            }
            
            # AI 서버로 예측 요청 (정확한 엔드포인트로 수정)
            ai_response = await cls._make_ai_request("/ai/mastitis/predict-by-scc", payload)
            
            # AWS EC2 서버에서 추가 메타데이터 보강
            enhanced_response = {
                **ai_response,
                "user_id": current_user.get("user_id"),
                "farm_id": current_user.get("farm_id"),
                "requested_at": datetime.utcnow().isoformat(),
                "server_processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            logger.info(f"체세포수 기반 유방염 예측 완료 - 결과: {ai_response.get('prediction_class')}")
            return enhanced_response
            
        except HTTPException:
            # AI 서버에서 발생한 HTTP 예외는 그대로 전달
            raise
        except Exception as e:
            logger.error(f"체세포수 기반 유방염 예측 처리 중 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "SCC_MASTITIS_PREDICTION_PROCESSING_FAILED",
                    "error_message": "체세포수 기반 유방염 예측 처리 중 오류가 발생했습니다",
                    "reason": str(e)
                }
            )
    
    @classmethod
    async def predict_milk_yield_batch(cls, batch_request, current_user: Dict) -> Dict[str, Any]:
        """다중 젖소 착유량 일괄 예측 - AI 서버로 요청 전달"""
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"사용자 {current_user.get('user_id')}의 배치 AI 예측 요청 시작 - 크기: {len(batch_request.predictions)}")
        
        try:
            # AI 서버로 보낼 페이로드 구성
            payload = {
                "predictions": [
                    {
                        "cow_id": getattr(pred, 'cow_id', None),
                        "milking_frequency": pred.milking_frequency,
                        "conductivity": pred.conductivity,
                        "temperature": pred.temperature,
                        "fat_percentage": pred.fat_percentage,
                        "protein_percentage": pred.protein_percentage,
                        "concentrate_intake": pred.concentrate_intake,
                        "milking_month": pred.milking_month,
                        "milking_day_of_week": pred.milking_day_of_week,
                        "prediction_date": getattr(pred, 'prediction_date', None),
                        "notes": getattr(pred, 'notes', None)
                    }
                    for pred in batch_request.predictions
                ],
                "batch_name": getattr(batch_request, 'batch_name', None)
            }
            
            # AI 서버로 배치 예측 요청
            ai_response = await cls._make_ai_request("/ai/milk-yield/batch-predict", payload)
            
            # AWS EC2 서버에서 추가 메타데이터 보강
            enhanced_response = {
                **ai_response,
                "aws_batch_id": batch_id,
                "user_id": current_user.get("user_id"),
                "farm_id": current_user.get("farm_id"),
                "requested_at": datetime.utcnow().isoformat(),
                "server_processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            logger.info(f"배치 AI 예측 완료 - 성공: {ai_response.get('successful_predictions')}")
            return enhanced_response
                
        except HTTPException:
            # AI 서버에서 발생한 HTTP 예외는 그대로 전달
            raise
        except Exception as e:
            logger.error(f"배치 예측 처리 중 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "BATCH_PREDICTION_PROCESSING_FAILED",
                    "error_message": "배치 예측 처리 중 오류가 발생했습니다",
                    "batch_id": batch_id,
                    "reason": str(e)
                }
            )

    # 유방염 배치 예측
    @classmethod
    async def predict_mastitis_batch(cls, batch_request, current_user: Dict) -> Dict[str, Any]:
        """다중 젖소 유방염 일괄 예측 - AI 서버로 요청 전달"""
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"사용자 {current_user.get('user_id')}의 배치 유방염 예측 요청 시작 - 크기: {len(batch_request.predictions)}")
        
        try:
            # AI 서버로 보낼 페이로드 구성
            payload = {
                "predictions": [
                    {
                        "cow_id": getattr(pred, 'cow_id', None),
                        "milk_yield": pred.milk_yield,
                        "conductivity": pred.conductivity,
                        "fat_percentage": pred.fat_percentage,
                        "protein_percentage": pred.protein_percentage,
                        "lactation_number": pred.lactation_number,
                        "prediction_date": getattr(pred, 'prediction_date', None),
                        "notes": getattr(pred, 'notes', None)
                    }
                    for pred in batch_request.predictions
                ],
                "batch_name": getattr(batch_request, 'batch_name', None)
            }
            
            # AI 서버로 배치 예측 요청
            ai_response = await cls._make_ai_request("/ai/mastitis/batch-predict", payload)
            
            # AWS EC2 서버에서 추가 메타데이터 보강
            enhanced_response = {
                **ai_response,
                "aws_batch_id": batch_id,
                "user_id": current_user.get("user_id"),
                "farm_id": current_user.get("farm_id"),
                "requested_at": datetime.utcnow().isoformat(),
                "server_processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            logger.info(f"배치 유방염 예측 완료 - 성공: {ai_response.get('successful_predictions')}")
            return enhanced_response
                
        except HTTPException:
            # AI 서버에서 발생한 HTTP 예외는 그대로 전달
            raise
        except Exception as e:
            logger.error(f"배치 유방염 예측 처리 중 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "BATCH_MASTITIS_PREDICTION_PROCESSING_FAILED",
                    "error_message": "배치 유방염 예측 처리 중 오류가 발생했습니다",
                    "batch_id": batch_id,
                    "reason": str(e)
                }
            )

    # 체세포수 기반 유방염 배치 예측
    @classmethod
    async def predict_scc_mastitis_batch(cls, batch_request, current_user: Dict) -> Dict[str, Any]:
        """다중 젖소 체세포수 기반 유방염 일괄 예측 - AI 서버로 요청 전달"""
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"사용자 {current_user.get('user_id')}의 배치 체세포수 기반 유방염 예측 요청 시작 - 크기: {len(batch_request.predictions)}")
        
        try:
            # AI 서버로 보낼 페이로드 구성 (체세포수만 전송)
            payload = {
                "predictions": [
                    {
                        "cow_id": getattr(pred, 'cow_id', None),
                        "somatic_cell_count": pred.somatic_cell_count,
                        "prediction_date": getattr(pred, 'prediction_date', None),
                        "notes": getattr(pred, 'notes', None)
                    }
                    for pred in batch_request.predictions
                ],
                "batch_name": getattr(batch_request, 'batch_name', None)
            }
            
            # AI 서버로 배치 예측 요청 (정확한 엔드포인트로 수정)
            ai_response = await cls._make_ai_request("/ai/mastitis/batch-predict-by-scc", payload)
            
            # AWS EC2 서버에서 추가 메타데이터 보강
            enhanced_response = {
                **ai_response,
                "aws_batch_id": batch_id,
                "user_id": current_user.get("user_id"),
                "farm_id": current_user.get("farm_id"),
                "requested_at": datetime.utcnow().isoformat(),
                "server_processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            logger.info(f"배치 체세포수 기반 유방염 예측 완료 - 성공: {ai_response.get('successful_predictions')}")
            return enhanced_response
                
        except HTTPException:
            # AI 서버에서 발생한 HTTP 예외는 그대로 전달
            raise
        except Exception as e:
            logger.error(f"배치 체세포수 기반 유방염 예측 처리 중 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error_code": "BATCH_SCC_MASTITIS_PREDICTION_PROCESSING_FAILED",
                    "error_message": "배치 체세포수 기반 유방염 예측 처리 중 오류가 발생했습니다",
                    "batch_id": batch_id,
                    "reason": str(e)
                }
            )

    @classmethod
    async def check_ai_server_health(cls) -> Dict[str, Any]:
        """AI 서버 상태 확인"""
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.get(f"{cls.AI_SERVER_URL}/ai/model-health")
                
                if response.status_code == 200:
                    ai_health = response.json()
                    return {
                        "aws_server_status": "healthy",
                        "ai_server_connection": "connected",
                        "ai_server_url": cls.AI_SERVER_URL,
                        "ai_server_health": ai_health,
                        "timestamp": datetime.utcnow().isoformat(),
                        "service_ready": ai_health.get("status") == "healthy"
                    }
                else:
                    return {
                        "aws_server_status": "healthy",
                        "ai_server_connection": "degraded",
                        "ai_server_url": cls.AI_SERVER_URL,
                        "error": f"AI 서버 응답 코드: {response.status_code}",
                        "timestamp": datetime.utcnow().isoformat(),
                        "service_ready": False
                    }
                    
        except Exception as e:
            return {
                "aws_server_status": "healthy", 
                "ai_server_connection": "failed",
                "ai_server_url": cls.AI_SERVER_URL,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "service_ready": False,
                "recommendation": "AI 서버가 실행 중인지 확인하고 URL이 올바른지 확인하세요"
            }

# 서버 시작시 호출할 초기화 함수 (AI 서버 연결 확인용)
def initialize_models():
    """서버 시작시 AI 서버 연결 확인"""
    try:
        logger.info("🔗 AI 서버 연결 확인 중...")
        logger.info(f"AI 서버 URL: {AIPredictionService.AI_SERVER_URL}")
        # 실제 연결 확인은 첫 요청 시에 수행
        logger.info("✅ AI 예측 서비스 초기화 완료 (연결은 첫 요청 시 확인)")
        return True
    except Exception as e:
        logger.warning(f"⚠️ AI 서비스 초기화 중 경고: {e}")
        logger.info("📱 다른 기능들은 정상 작동합니다")
        return False