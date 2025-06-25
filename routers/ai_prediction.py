# AI 예측 라우터 routers/ai_prediction.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from schemas.ai_prediction import *
from services.ai_model_service import AIModelService
from routers.auth_firebase import get_current_user
import asyncio

router = APIRouter()

# AI 모델 서비스 인스턴스 (전역 변수로 선언하여 모델 로딩 시간 최소화)
ai_service = None

def get_ai_service():
    """AI 서비스 인스턴스 반환 (싱글톤 패턴)"""
    global ai_service
    if ai_service is None:
        ai_service = AIModelService()
    return ai_service

@router.get("/models/health",
            summary="AI 모델 상태 확인",
            description="현재 로딩된 AI 모델들의 상태를 확인합니다.")
async def check_models_health():
    """AI 모델 상태 확인"""
    try:
        service = get_ai_service()
        model_status = {}
        
        for model_type in PredictionModelType:
            is_loaded = model_type in service.models
            model_status[model_type.value] = {
                "loaded": is_loaded,
                "version": service.model_configs.get(model_type, {}).get("version", "unknown"),
                "last_updated": service.model_configs.get(model_type, {}).get("last_updated", "unknown")
            }
        
        return {
            "status": "healthy",
            "total_models": len(service.models),
            "models": model_status,
            "service_start_time": "2025-01-01T00:00:00"  # 실제로는 서비스 시작 시간
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 모델 상태 확인 중 오류가 발생했습니다: {str(e)}"
        )

# ===== 질병 예측 API =====
@router.post("/predict/disease",
             response_model=DiseasesPredictionResponse,
             summary="젖소 질병 예측",
             description="""
             젖소의 현재 상태 데이터를 기반으로 질병 발생 위험을 예측합니다.
             
             **예측 질병:**
             - 유방염 (Mastitis)
             - 대사성 질환 (Metabolic Disorder) 
             - 럼피스킨병 (Lumpy Skin Disease)
             - 소화기 질환 (Digestive Disorder)
             
             **입력 데이터:**
             - 착유 관련: 착유량, 체세포수, 전도도, 온도, 유성분
             - 사료 관련: 사료 섭취량
             - 개체 정보: 산차수, 착유일수
             
             **판단 기준:**
             - 유방염: 체세포수 > 500,000개/ml, 전도도 > 0.073
             - 체온: 정상 38.5-39.5°C
             - 착유량 급격한 감소시 질병 의심
             """)
async def predict_disease(
    request: DiseasesPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """젖소 질병 예측"""
    try:
        # 젖소 소유권 확인
        await _verify_cow_ownership(request.cow_id, current_user.get("farm_id"))
        
        service = get_ai_service()
        result = await service.predict_disease(request)
        
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"질병 예측 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/predict/breeding-success",
             response_model=BreedingSuccessPredictionResponse,
             summary="번식 성공률 예측",
             description="""
             젖소의 번식 성공 확률과 최적 수정 시기를 예측합니다.
             
             **예측 요소:**
             - 수정 성공 확률 (0-1)
             - 최적 수정 시기
             - 위험 요소 식별
             - 관리 권장사항
             
             **고려 사항:**
             - 분만 후 45-60일 이후 수정 권장
             - 체형점수 2.5-3.5 최적
             - 산차수별 성공률 차이
             - 영양상태 및 스트레스 요인
             """)
async def predict_breeding_success(
    request: BreedingSuccessPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """번식 성공률 예측"""
    try:
        await _verify_cow_ownership(request.cow_id, current_user.get("farm_id"))
        
        service = get_ai_service()
        result = await service.predict_breeding_success(request)
        
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"번식 성공률 예측 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/predict/calving-date", 
             response_model=CalvingDatePredictionResponse,
             summary="분만 예정일 예측",
             description="""
             수정일을 기반으로 정확한 분만 예정일을 예측합니다.
             
             **예측 정보:**
             - 예상 분만일
             - 신뢰 구간 (최소/최대일)
             - 임신 기간 (일수)
             - 분만 준비 권장사항
             
             **일반적인 임신 기간:**
             - 홀스타인: 평균 280일 (275-285일)
             - 한우: 평균 285일 (280-290일)
             - 초산우는 경산우보다 2-3일 길어질 수 있음
             """)
async def predict_calving_date(
    request: CalvingDatePredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """분만 예정일 예측"""
    try:
        await _verify_cow_ownership(request.cow_id, current_user.get("farm_id"))
        
        service = get_ai_service()
        
        # 간단한 분만일 계산 (실제로는 AI 모델 사용)
        from datetime import timedelta
        
        cow_info = await service.get_cow_basic_info(request.cow_id)
        
        # 품종별 평균 임신기간
        breed_gestation = {
            "Holstein": 280,
            "Korean Native": 285,
            "Jersey": 279
        }
        
        base_gestation = breed_gestation.get(cow_info.get('breed', ''), 280)
        
        # 산차수 보정
        if request.lactation_number == 1:  # 초산
            base_gestation += 2
        
        # 이전 임신기간 고려
        if request.previous_gestation_period:
            base_gestation = (base_gestation + request.previous_gestation_period) // 2
        
        predicted_calving_date = request.insemination_date + timedelta(days=base_gestation)
        
        # 신뢰구간 계산
        confidence_interval = {
            "earliest": predicted_calving_date - timedelta(days=5),
            "latest": predicted_calving_date + timedelta(days=5)
        }
        
        # 분만 준비 권장사항
        preparation_recommendations = [
            "분만 30일 전: 건유 시작 및 분만방 준비",
            "분만 14일 전: 분만징후 관찰 강화",
            "분만 7일 전: 24시간 모니터링 체계 구축",
            "분만 직전: 수의사 연락처 준비 및 응급상황 대비"
        ]
        
        return CalvingDatePredictionResponse(
            cow_id=request.cow_id,
            cow_name=cow_info['name'],
            ear_tag_number=cow_info['ear_tag_number'],
            predicted_calving_date=predicted_calving_date,
            confidence_interval={
                "earliest": confidence_interval["earliest"],
                "latest": confidence_interval["latest"]
            },
            gestation_period_days=base_gestation,
            preparation_recommendations=preparation_recommendations,
            prediction_date=datetime.now(),
            model_version="v1.0"
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분만 예정일 예측 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/analyze/feed-efficiency",
             response_model=FeedEfficiencyAnalysisResponse,
             summary="사료 효율 분석",
             description="""
             젖소의 사료 섭취 대비 착유 효율을 분석하고 최적화 방안을 제시합니다.
             
             **분석 지표:**
             - 사료 효율 비율 (L우유/kg사료)
             - 효율 등급 (우수/양호/보통/부족)
             - 벤치마크 대비 비교
             - 최적 사료량 예측
             
             **일반적인 효율 기준:**
             - 우수: 1.5L/kg 이상
             - 양호: 1.2-1.5L/kg
             - 보통: 1.0-1.2L/kg
             - 부족: 1.0L/kg 미만
             """)
async def analyze_feed_efficiency(
    request: FeedEfficiencyAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """사료 효율 분석"""
    try:
        await _verify_cow_ownership(request.cow_id, current_user.get("farm_id"))
        
        service = get_ai_service()
        result = await service.predict_feed_efficiency(request)
        
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사료 효율 분석 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/predict/milk-quality",
             response_model=MilkQualityPredictionResponse,
             summary="유성분 품질 예측",
             description="""
             향후 일정 기간의 우유 품질(유성분)을 예측합니다.
             
             **예측 성분:**
             - 유지방 비율 (%)
             - 유단백 비율 (%)
             - 무지고형분 (SNF) (%)
             - 품질 등급
             
             **품질 등급 기준:**
             - 특급: 유지방 3.6% 이상, 유단백 3.2% 이상
             - 1등급: 유지방 3.4% 이상, 유단백 3.0% 이상
             - 2등급: 유지방 3.2% 이상, 유단백 2.8% 이상
             - 3등급: 그 외
             
             **영향 요인:**
             - 사료 구성 및 급여량
             - 착유일수 및 산차수
             - 계절 및 환경 요인
             """)
async def predict_milk_quality(
    request: MilkQualityPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """유성분 품질 예측"""
    try:
        await _verify_cow_ownership(request.cow_id, current_user.get("farm_id"))
        
        service = get_ai_service()
        result = await service.predict_milk_quality(request)
        
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"유성분 품질 예측 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/predict/growth",
             response_model=GrowthPredictionResponse,
             summary="초산우 성장 예측",
             description="""
             초산우 및 육성우의 성장 잠재력과 미래 생산성을 예측합니다.
             
             **예측 정보:**
             - 예상 최고 착유량
             - 예상 성우 체중
             - 성장 잠재력 점수
             - 성장 이정표 예측
             - 관리 권장사항
             
             **성장 단계별 관리 포인트:**
             - 0-6개월: 골격 발달 중점
             - 6-15개월: 번식 준비기
             - 15-24개월: 초산 준비기
             - 24개월+: 성우 전환기
             """)
async def predict_growth(
    request: GrowthPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """초산우 성장 예측"""
    try:
        await _verify_cow_ownership(request.cow_id, current_user.get("farm_id"))
        
        service = get_ai_service()
        result = await service.predict_growth(request)
        
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"성장 예측 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/predict/comprehensive",
             response_model=ComprehensivePredictionResponse,
             summary="종합 예측 분석",
             description="""
             여러 AI 모델을 동시에 실행하여 젖소의 종합적인 상태를 분석합니다.
             
             **포함 가능한 예측:**
             - 질병 예측
             - 번식 성공률 예측
             - 분만 예정일 예측 (임신우만)
             - 사료 효율 분석
             - 유성분 품질 예측
             - 성장 예측 (초산우만)
             
             **장점:**
             - 한 번의 요청으로 다양한 분석 결과
             - 통합된 관리 권장사항
             - 우선순위별 조치 사항
             - 전체적인 경제성 전망
             """)
async def comprehensive_prediction(
    request: ComprehensivePredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """종합 예측 분석"""
    try:
        await _verify_cow_ownership(request.cow_id, current_user.get("farm_id"))
        
        service = get_ai_service()
        result = await service.comprehensive_prediction(request)
        
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"종합 예측 분석 중 오류가 발생했습니다: {str(e)}"
        )

# ===== 배치 처리 API =====
@router.post("/predict/batch/disease",
             summary="농장 전체 질병 예측 (배치)",
             description="""
             농장의 모든 젖소에 대해 질병 예측을 일괄 실행합니다.
             
             **처리 방식:**
             - 백그라운드에서 비동기 처리
             - 진행상황을 별도 API로 확인 가능
             - 완료 후 결과를 데이터베이스에 저장
             
             **활용 시나리오:**
             - 정기 건강 모니터링
             - 질병 발생 위험군 식별
             - 예방 관리 계획 수립
             """)
async def batch_disease_prediction(
    background_tasks: BackgroundTasks,
    use_historical_data: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """농장 전체 질병 예측 배치 처리"""
    try:
        farm_id = current_user.get("farm_id")
        task_id = f"batch_disease_{farm_id}_{int(datetime.now().timestamp())}"
        
        # 백그라운드 작업 시작
        background_tasks.add_task(
            _process_batch_disease_prediction, 
            task_id, 
            farm_id, 
            use_historical_data
        )
        
        return {
            "success": True,
            "message": "농장 전체 질병 예측을 시작했습니다",
            "task_id": task_id,
            "estimated_duration": "5-10분",
            "status_check_url": f"/ai/batch/status/{task_id}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"배치 처리 시작 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/batch/status/{task_id}",
            summary="배치 작업 상태 확인",
            description="실행 중인 배치 작업의 진행상황을 확인합니다.")
async def get_batch_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """배치 작업 상태 확인"""
    # 메모리 또는 Redis에서 작업 상태 조회 (실제 구현시)
    # 여기서는 간단한 예시
    return {
        "task_id": task_id,
        "status": "processing",  # processing, completed, failed
        "progress": 65,  # 0-100
        "processed_cows": 13,
        "total_cows": 20,
        "start_time": "2025-06-25T10:00:00",
        "estimated_completion": "2025-06-25T10:08:00",
        "current_step": "젖소 015번 질병 예측 중..."
    }

# ===== 예측 결과 관리 API =====
@router.get("/predictions/history/{cow_id}",
            summary="젖소별 예측 이력 조회",
            description="특정 젖소의 과거 AI 예측 결과들을 조회합니다.")
async def get_prediction_history(
    cow_id: str,
    model_type: Optional[PredictionModelType] = None,
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """젖소별 예측 이력 조회"""
    try:
        await _verify_cow_ownership(cow_id, current_user.get("farm_id"))
        
        # 실제로는 prediction_history 컬렉션에서 조회
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        
        query = db.collection('ai_prediction_history')\
            .where('cow_id', '==', cow_id)\
            .where('farm_id', '==', current_user.get("farm_id"))
        
        if model_type:
            query = query.where('model_type', '==', model_type.value)
        
        # 최근 N일간의 예측 이력
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        query = query.where('prediction_date', '>=', start_date)
        
        results = query.order_by('prediction_date', direction='DESCENDING').limit(50).get()
        
        history = []
        for result in results:
            data = result.to_dict()
            history.append({
                "id": data["id"],
                "model_type": data["model_type"],
                "prediction_date": data["prediction_date"],
                "summary": data.get("summary", {}),
                "accuracy_score": data.get("accuracy_score"),  # 실제 결과와 비교한 정확도
                "confidence": data.get("confidence")
            })
        
        return {
            "cow_id": cow_id,
            "total_predictions": len(history),
            "period_days": days,
            "predictions": history
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예측 이력 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/analytics/farm-overview",
            summary="농장 전체 AI 분석 개요",
            description="농장 전체의 AI 예측 결과를 요약하여 제공합니다.")
async def get_farm_ai_analytics(
    current_user: dict = Depends(get_current_user)
):
    """농장 전체 AI 분석 개요"""
    try:
        farm_id = current_user.get("farm_id")
        
        # 최근 예측 결과 요약
        analytics = {
            "farm_id": farm_id,
            "analysis_date": datetime.now(),
            "total_cows_analyzed": 25,
            "health_overview": {
                "healthy_cows": 20,
                "attention_needed": 4,
                "high_risk": 1,
                "average_health_score": 85.2
            },
            "breeding_overview": {
                "ready_for_breeding": 8,
                "pregnant_cows": 12,
                "breeding_success_rate": 0.75,
                "average_success_probability": 0.68
            },
            "production_overview": {
                "high_efficiency_cows": 15,
                "average_efficiency_cows": 8,
                "low_efficiency_cows": 2,
                "average_milk_yield": 28.5,
                "average_feed_efficiency": 1.25
            },
            "quality_overview": {
                "premium_grade": 18,
                "grade_1": 6,
                "grade_2": 1,
                "average_fat_percentage": 3.8,
                "average_protein_percentage": 3.3
            },
            "recommendations": [
                "젖소 015번 긴급 건강검진 필요",
                "사료 효율 개선 대상: 003번, 007번",
                "번식 적기 젖소: 009번, 012번, 018번",
                "품질 관리 강화 필요: 전체적으로 양호한 상태"
            ],
            "economic_impact": {
                "potential_cost_savings": 1250000,  # 원
                "productivity_improvement": 8.5,  # %
                "disease_prevention_value": 850000  # 원
            }
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"농장 분석 개요 조회 중 오류가 발생했습니다: {str(e)}"
        )

# ===== 헬퍼 함수들 =====

async def _verify_cow_ownership(cow_id: str, farm_id: str):
    """젖소 소유권 확인"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        
        cow_doc = db.collection('cows').document(cow_id).get()
        
        if not cow_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="젖소를 찾을 수 없습니다"
            )
        
        cow_data = cow_doc.to_dict()
        if cow_data.get("farm_id") != farm_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 젖소에 대한 접근 권한이 없습니다"
            )
        
        if not cow_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 젖소입니다"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"젖소 정보 확인 중 오류가 발생했습니다: {str(e)}"
        )

async def _process_batch_disease_prediction(task_id: str, farm_id: str, use_historical_data: bool):
    """배치 질병 예측 처리 (백그라운드 작업)"""
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        
        # 작업 상태 초기화
        task_status = {
            "task_id": task_id,
            "farm_id": farm_id,
            "status": "processing",
            "progress": 0,
            "start_time": datetime.now(),
            "processed_cows": 0,
            "total_cows": 0,
            "results": []
        }
        
        # 농장의 모든 젖소 조회
        cows_query = db.collection('cows')\
            .where('farm_id', '==', farm_id)\
            .where('is_active', '==', True)\
            .get()
        
        total_cows = len(cows_query)
        task_status["total_cows"] = total_cows
        
        service = get_ai_service()
        
        for i, cow_doc in enumerate(cows_query):
            cow_data = cow_doc.to_dict()
            cow_id = cow_data["id"]
            
            try:
                # 각 젖소별 질병 예측 실행
                # 기본값으로 예측 요청 생성
                disease_request = DiseasesPredictionRequest(
                    cow_id=cow_id,
                    use_historical_data=use_historical_data
                )
                
                prediction_result = await service.predict_disease(disease_request)
                
                # 결과 저장
                task_status["results"].append({
                    "cow_id": cow_id,
                    "cow_name": cow_data.get("name"),
                    "overall_health_score": prediction_result.overall_health_score,
                    "high_risk_diseases": [
                        p.disease_type.value for p in prediction_result.prediction_results 
                        if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
                    ]
                })
                
            except Exception as e:
                print(f"젖소 {cow_id} 예측 실패: {str(e)}")
                task_status["results"].append({
                    "cow_id": cow_id,
                    "cow_name": cow_data.get("name"),
                    "error": str(e)
                })
            
            # 진행률 업데이트
            task_status["processed_cows"] = i + 1
            task_status["progress"] = int((i + 1) / total_cows * 100)
            
            # 실제로는 Redis나 DB에 상태 저장
            print(f"배치 처리 진행률: {task_status['progress']}%")
        
        # 작업 완료
        task_status["status"] = "completed"
        task_status["end_time"] = datetime.now()
        task_status["progress"] = 100
        
        # 결과를 데이터베이스에 저장
        db.collection('batch_prediction_results').document(task_id).set(task_status)
        
    except Exception as e:
        # 작업 실패
        task_status["status"] = "failed"
        task_status["error"] = str(e)
        task_status["end_time"] = datetime.now()
        print(f"배치 처리 실패: {str(e)}")

# ===== 모델 관리 API (관리자용) =====
@router.post("/admin/models/reload",
             summary="AI 모델 재로딩 (관리자)",
             description="모든 AI 모델을 다시 로딩합니다. 모델 업데이트 후 사용합니다.")
async def reload_models(
    current_user: dict = Depends(get_current_user)
):
    """AI 모델 재로딩 (관리자 전용)"""
    # 실제로는 관리자 권한 확인 필요
    try:
        global ai_service
        ai_service = None  # 기존 서비스 해제
        ai_service = AIModelService()  # 새로 로딩
        
        return {
            "success": True,
            "message": "모든 AI 모델이 성공적으로 재로딩되었습니다",
            "loaded_models": list(ai_service.models.keys()),
            "reload_time": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모델 재로딩 중 오류가 발생했습니다: {str(e)}"
        )