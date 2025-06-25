# AI 모델 서비스 services/ai_model_service.py

import os
import torch
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from config.firebase_config import get_firestore_client
from schemas.ai_prediction import *

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelService:
    """AI 모델 서비스 - 모든 예측 모델을 관리"""
    
    def __init__(self):
        self.models = {}
        self.preprocessors = {}
        self.model_configs = {}
        self.db = get_firestore_client()
        self._load_all_models()
    
    def _load_all_models(self):
        """모든 AI 모델 로딩"""
        model_base_path = Path("models")
        
        model_files = {
            PredictionModelType.DISEASE_PREDICTION: "disease_prediction_model.pt",
            PredictionModelType.BREEDING_SUCCESS: "breeding_success_model.pt", 
            PredictionModelType.CALVING_DATE: "calving_date_model.pt",
            PredictionModelType.FEED_EFFICIENCY: "feed_efficiency_model.pt",
            PredictionModelType.MILK_QUALITY: "milk_quality_model.pt",
            PredictionModelType.GROWTH_PREDICTION: "growth_prediction_model.pt"
        }
        
        for model_type, model_file in model_files.items():
            model_path = model_base_path / model_file
            try:
                if model_path.exists():
                    # PyTorch 모델 로딩
                    if model_file.endswith('.pt'):
                        model = torch.jit.load(str(model_path))
                        model.eval()
                    # Pickle 모델 로딩 (sklearn 등)
                    elif model_file.endswith('.pkl'):
                        with open(model_path, 'rb') as f:
                            model = pickle.load(f)
                    
                    self.models[model_type] = model
                    logger.info(f"모델 로딩 성공: {model_type.value}")
                    
                    # 전처리기 로딩
                    preprocessor_path = model_base_path / f"{model_type.value}_preprocessor.pkl"
                    if preprocessor_path.exists():
                        with open(preprocessor_path, 'rb') as f:
                            self.preprocessors[model_type] = pickle.load(f)
                    
                    # 모델 설정 로딩
                    config_path = model_base_path / f"{model_type.value}_config.json"
                    if config_path.exists():
                        import json
                        with open(config_path, 'r', encoding='utf-8') as f:
                            self.model_configs[model_type] = json.load(f)
                            
                else:
                    logger.warning(f"모델 파일을 찾을 수 없습니다: {model_path}")
                    # 임시 더미 모델 (개발용)
                    self.models[model_type] = self._create_dummy_model(model_type)
                    
            except Exception as e:
                logger.error(f"모델 로딩 실패: {model_type.value}, 에러: {str(e)}")
                # 더미 모델로 대체
                self.models[model_type] = self._create_dummy_model(model_type)
    
    def _create_dummy_model(self, model_type: PredictionModelType):
        """개발용 더미 모델 생성"""
        class DummyModel:
            def __init__(self, model_type):
                self.model_type = model_type
                
            def predict(self, X):
                # 더미 예측값 반환
                if self.model_type == PredictionModelType.DISEASE_PREDICTION:
                    return np.random.random((len(X), 4))  # 4개 질병 확률
                elif self.model_type == PredictionModelType.BREEDING_SUCCESS:
                    return np.random.random(len(X))  # 성공 확률
                elif self.model_type == PredictionModelType.CALVING_DATE:
                    return np.random.randint(270, 290, len(X))  # 임신 기간
                elif self.model_type == PredictionModelType.FEED_EFFICIENCY:
                    return np.random.random(len(X)) * 2  # 효율 비율
                elif self.model_type == PredictionModelType.MILK_QUALITY:
                    return np.random.random((len(X), 3))  # 지방, 단백질, 고형분
                elif self.model_type == PredictionModelType.GROWTH_PREDICTION:
                    return np.random.random((len(X), 2))  # 최고착유량, 성우체중
                return np.random.random(len(X))
        
        return DummyModel(model_type)
    
    async def get_cow_historical_data(self, cow_id: str, days: int = 30) -> pd.DataFrame:
        """젖소의 과거 데이터 조회"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 상세 기록에서 착유, 사료, 건강검진 데이터 조회
            records_query = self.db.collection('cow_detailed_records')\
                .where('cow_id', '==', cow_id)\
                .where('is_active', '==', True)\
                .where('record_date', '>=', start_date.strftime('%Y-%m-%d'))\
                .order_by('record_date')\
                .get()
            
            data_list = []
            for record in records_query:
                record_data = record.to_dict()
                if record_data.get('record_type') in ['milking', 'feed', 'health_check']:
                    flat_data = {
                        'date': record_data['record_date'],
                        'record_type': record_data['record_type'],
                        **record_data.get('record_data', {})
                    }
                    data_list.append(flat_data)
            
            if data_list:
                df = pd.DataFrame(data_list)
                # 날짜별로 집계
                df_pivot = df.pivot_table(
                    index='date', 
                    columns='record_type', 
                    values=['milk_yield', 'feed_amount', 'body_temperature', 
                           'somatic_cell_count', 'conductivity', 'fat_percentage', 
                           'protein_percentage'],
                    aggfunc='mean'
                ).fillna(method='ffill')
                
                return df_pivot
            else:
                # 빈 데이터프레임 반환
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"과거 데이터 조회 실패: {str(e)}")
            return pd.DataFrame()
    
    async def get_cow_basic_info(self, cow_id: str) -> Dict:
        """젖소 기본 정보 조회"""
        try:
            cow_doc = self.db.collection('cows').document(cow_id).get()
            if cow_doc.exists:
                cow_data = cow_doc.to_dict()
                
                # 월령 계산
                age_months = 0
                if cow_data.get('birthdate'):
                    birth_date = datetime.strptime(cow_data['birthdate'], '%Y-%m-%d')
                    today = datetime.now()
                    age_months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
                
                return {
                    'cow_id': cow_id,
                    'name': cow_data.get('name', ''),
                    'ear_tag_number': cow_data.get('ear_tag_number', ''),
                    'breed': cow_data.get('breed', ''),
                    'age_months': age_months,
                    'health_status': cow_data.get('health_status'),
                    'breeding_status': cow_data.get('breeding_status'),
                    'farm_id': cow_data.get('farm_id')
                }
            else:
                raise ValueError(f"젖소 정보를 찾을 수 없습니다: {cow_id}")
                
        except Exception as e:
            logger.error(f"젖소 기본 정보 조회 실패: {str(e)}")
            raise
    
    def _prepare_features(self, cow_info: Dict, request_data: Dict, historical_data: pd.DataFrame, 
                         model_type: PredictionModelType) -> np.ndarray:
        """모델별 특성 데이터 준비"""
        features = []
        
        # 공통 특성
        features.extend([
            cow_info.get('age_months', 0),
            request_data.get('lactation_number', 1),
            request_data.get('days_in_milk', 0)
        ])
        
        # 모델별 특성 추가
        if model_type == PredictionModelType.DISEASE_PREDICTION:
            features.extend([
                request_data.get('milk_yield', 0),
                request_data.get('somatic_cell_count', 0),
                request_data.get('conductivity', 0),
                request_data.get('temperature', 38.5),
                request_data.get('fat_percentage', 0),
                request_data.get('protein_percentage', 0),
                request_data.get('feed_intake', 0)
            ])
            
        elif model_type == PredictionModelType.BREEDING_SUCCESS:
            features.extend([
                request_data.get('days_since_calving', 0),
                request_data.get('previous_breeding_attempts', 0),
                request_data.get('body_condition_score', 3.0),
                request_data.get('milk_yield', 0),
                request_data.get('feed_intake', 0)
            ])
            
        elif model_type == PredictionModelType.FEED_EFFICIENCY:
            features.extend([
                request_data.get('daily_feed_intake', 0),
                request_data.get('daily_milk_yield', 0),
                request_data.get('body_weight', 500)
            ])
            
        # 과거 데이터 통계 특성 추가
        if not historical_data.empty and len(historical_data) > 0:
            if 'milk_yield' in historical_data.columns:
                features.extend([
                    historical_data['milk_yield'].mean(),
                    historical_data['milk_yield'].std()
                ])
            else:
                features.extend([0, 0])
        else:
            features.extend([0, 0])
        
        # NaN 값 처리
        features = [0 if pd.isna(f) else f for f in features]
        
        return np.array(features).reshape(1, -1)
    
    async def predict_disease(self, request: DiseasesPredictionRequest) -> DiseasesPredictionResponse:
        """질병 예측"""
        try:
            cow_info = await self.get_cow_basic_info(request.cow_id)
            historical_data = await self.get_cow_historical_data(request.cow_id) if request.use_historical_data else pd.DataFrame()
            
            # 특성 데이터 준비
            features = self._prepare_features(
                cow_info, 
                request.dict(), 
                historical_data, 
                PredictionModelType.DISEASE_PREDICTION
            )
            
            # 모델 예측
            model = self.models[PredictionModelType.DISEASE_PREDICTION]
            predictions = model.predict(features)[0]  # 첫 번째 행 결과
            
            # 질병별 결과 생성
            disease_types = [DiseaseType.MASTITIS, DiseaseType.METABOLIC_DISORDER, 
                           DiseaseType.LUMPY_SKIN, DiseaseType.DIGESTIVE_DISORDER]
            
            prediction_results = []
            for i, disease_type in enumerate(disease_types):
                probability = float(predictions[i]) if len(predictions) > i else 0.5
                
                # 위험도 계산
                if probability >= 0.8:
                    risk_level = RiskLevel.CRITICAL
                elif probability >= 0.6:
                    risk_level = RiskLevel.HIGH
                elif probability >= 0.4:
                    risk_level = RiskLevel.MEDIUM
                else:
                    risk_level = RiskLevel.LOW
                
                prediction_results.append(DiseasePredictionResult(
                    disease_type=disease_type,
                    probability=probability,
                    risk_level=risk_level,
                    confidence=min(0.95, max(0.6, probability))
                ))
            
            # 전체 건강 점수 계산
            overall_health_score = max(0, 100 - sum(p.probability * 25 for p in prediction_results))
            
            # 권장사항 생성
            recommendations = self._generate_health_recommendations(prediction_results, request)
            
            return DiseasesPredictionResponse(
                cow_id=request.cow_id,
                cow_name=cow_info['name'],
                ear_tag_number=cow_info['ear_tag_number'],
                prediction_results=prediction_results,
                overall_health_score=overall_health_score,
                recommendations=recommendations,
                prediction_date=datetime.now(),
                model_version="v1.0"
            )
            
        except Exception as e:
            logger.error(f"질병 예측 실패: {str(e)}")
            raise
    
    async def predict_breeding_success(self, request: BreedingSuccessPredictionRequest) -> BreedingSuccessPredictionResponse:
        """번식 성공률 예측"""
        try:
            cow_info = await self.get_cow_basic_info(request.cow_id)
            historical_data = await self.get_cow_historical_data(request.cow_id) if request.use_historical_data else pd.DataFrame()
            
            features = self._prepare_features(
                cow_info, 
                request.dict(), 
                historical_data, 
                PredictionModelType.BREEDING_SUCCESS
            )
            
            model = self.models[PredictionModelType.BREEDING_SUCCESS]
            success_probability = float(model.predict(features)[0])
            
            # 최적 수정 시기 계산
            optimal_window = self._calculate_optimal_breeding_window(request)
            
            # 위험 요소 식별
            risk_factors = self._identify_breeding_risk_factors(request, success_probability)
            
            # 권장사항 생성
            recommendations = self._generate_breeding_recommendations(success_probability, risk_factors)
            
            return BreedingSuccessPredictionResponse(
                cow_id=request.cow_id,
                cow_name=cow_info['name'],
                ear_tag_number=cow_info['ear_tag_number'],
                success_probability=success_probability,
                optimal_breeding_window=optimal_window,
                risk_factors=risk_factors,
                recommendations=recommendations,
                prediction_date=datetime.now(),
                model_version="v1.0"
            )
            
        except Exception as e:
            logger.error(f"번식 성공률 예측 실패: {str(e)}")
            raise
    
    async def predict_feed_efficiency(self, request: FeedEfficiencyAnalysisRequest) -> FeedEfficiencyAnalysisResponse:
        """사료 효율 분석"""
        try:
            cow_info = await self.get_cow_basic_info(request.cow_id)
            historical_data = await self.get_cow_historical_data(request.cow_id, request.analysis_period_days)
            
            # 실제 효율 계산
            actual_efficiency = request.daily_milk_yield / request.daily_feed_intake
            
            # 모델 예측으로 최적 효율 계산
            features = self._prepare_features(
                cow_info, 
                request.dict(), 
                historical_data, 
                PredictionModelType.FEED_EFFICIENCY
            )
            
            model = self.models[PredictionModelType.FEED_EFFICIENCY]
            predicted_optimal_efficiency = float(model.predict(features)[0])
            
            # 효율 등급 결정
            efficiency_ratio = actual_efficiency / predicted_optimal_efficiency if predicted_optimal_efficiency > 0 else 0.5
            
            if efficiency_ratio >= 0.9:
                efficiency_grade = EfficiencyGrade.EXCELLENT
            elif efficiency_ratio >= 0.75:
                efficiency_grade = EfficiencyGrade.GOOD
            elif efficiency_ratio >= 0.6:
                efficiency_grade = EfficiencyGrade.AVERAGE
            else:
                efficiency_grade = EfficiencyGrade.POOR
            
            # 벤치마크 비교
            benchmark_comparison = {
                "farm_average": 1.2,  # 농장 평균
                "breed_average": 1.3,  # 품종 평균
                "current_efficiency": actual_efficiency
            }
            
            # 최적 사료량 예측
            predicted_optimal_intake = request.daily_milk_yield / predicted_optimal_efficiency
            
            # 최적화 제안
            optimization_suggestions = self._generate_feed_optimization_suggestions(
                efficiency_grade, actual_efficiency, predicted_optimal_efficiency
            )
            
            return FeedEfficiencyAnalysisResponse(
                cow_id=request.cow_id,
                cow_name=cow_info['name'],
                ear_tag_number=cow_info['ear_tag_number'],
                feed_efficiency_ratio=actual_efficiency,
                efficiency_grade=efficiency_grade,
                benchmark_comparison=benchmark_comparison,
                optimization_suggestions=optimization_suggestions,
                predicted_optimal_intake=predicted_optimal_intake,
                analysis_date=datetime.now(),
                model_version="v1.0"
            )
            
        except Exception as e:
            logger.error(f"사료 효율 분석 실패: {str(e)}")
            raise
    
    async def predict_milk_quality(self, request: MilkQualityPredictionRequest) -> MilkQualityPredictionResponse:
        """유성분 품질 예측"""
        try:
            cow_info = await self.get_cow_basic_info(request.cow_id)
            historical_data = await self.get_cow_historical_data(request.cow_id)
            
            features = self._prepare_features(
                cow_info, 
                request.dict(), 
                historical_data, 
                PredictionModelType.MILK_QUALITY
            )
            
            model = self.models[PredictionModelType.MILK_QUALITY]
            quality_predictions_raw = model.predict(features)[0]  # [fat%, protein%, snf%]
            
            # 일별 예측 생성
            quality_predictions = []
            base_date = datetime.now().date()
            
            for day in range(request.prediction_days):
                prediction_date = base_date + timedelta(days=day)
                
                # 일별 변동 시뮬레이션 (실제로는 더 복잡한 시계열 모델 사용)
                daily_variation = np.random.normal(0, 0.1, 3)
                
                fat_pct = max(2.0, min(6.0, quality_predictions_raw[0] + daily_variation[0]))
                protein_pct = max(2.5, min(4.5, quality_predictions_raw[1] + daily_variation[1]))
                snf = max(8.0, min(10.0, quality_predictions_raw[2] + daily_variation[2]))
                
                # 품질 등급 계산
                quality_score = (fat_pct * 0.4 + protein_pct * 0.4 + snf * 0.2) / 10 * 100
                if quality_score >= 85:
                    quality_grade = "특급"
                elif quality_score >= 75:
                    quality_grade = "1등급"
                elif quality_score >= 65:
                    quality_grade = "2등급"
                else:
                    quality_grade = "3등급"
                
                quality_predictions.append(MilkQualityPrediction(
                    date=prediction_date,
                    fat_percentage=round(fat_pct, 2),
                    protein_percentage=round(protein_pct, 2),
                    solid_not_fat=round(snf, 2),
                    quality_grade=quality_grade
                ))
            
            # 평균 품질 점수
            avg_quality_score = sum(
                (p.fat_percentage * 0.4 + p.protein_percentage * 0.4 + p.solid_not_fat * 0.2) / 10 * 100
                for p in quality_predictions
            ) / len(quality_predictions)
            
            # 개선 권장사항
            improvement_recommendations = self._generate_quality_improvement_recommendations(
                quality_predictions, request
            )
            
            return MilkQualityPredictionResponse(
                cow_id=request.cow_id,
                cow_name=cow_info['name'],
                ear_tag_number=cow_info['ear_tag_number'],
                quality_predictions=quality_predictions,
                average_quality_score=round(avg_quality_score, 1),
                improvement_recommendations=improvement_recommendations,
                prediction_date=datetime.now(),
                model_version="v1.0"
            )
            
        except Exception as e:
            logger.error(f"유성분 품질 예측 실패: {str(e)}")
            raise
    
    async def predict_growth(self, request: GrowthPredictionRequest) -> GrowthPredictionResponse:
        """초산우 성장 예측"""
        try:
            cow_info = await self.get_cow_basic_info(request.cow_id)
            historical_data = await self.get_cow_historical_data(request.cow_id)
            
            features = self._prepare_features(
                cow_info, 
                request.dict(), 
                historical_data, 
                PredictionModelType.GROWTH_PREDICTION
            )
            
            model = self.models[PredictionModelType.GROWTH_PREDICTION]
            growth_predictions = model.predict(features)[0]  # [peak_yield, mature_weight]
            
            predicted_peak_yield = float(growth_predictions[0])
            predicted_mature_weight = float(growth_predictions[1])
            
            # 성장 잠재력 점수 계산
            breed_avg_yield = 25.0  # 품종별 평균 (실제로는 DB에서 조회)
            growth_potential_score = min(100, (predicted_peak_yield / breed_avg_yield) * 100)
            
            # 성장 이정표 예측
            milestone_predictions = {
                "first_breeding_age": f"{request.current_age_months + 6}개월",
                "first_calving_age": f"{request.current_age_months + 15}개월",
                "peak_lactation_age": f"{request.current_age_months + 24}개월",
                "economic_life_years": "6-8년"
            }
            
            # 관리 권장사항
            management_recommendations = self._generate_growth_management_recommendations(
                request, predicted_peak_yield, growth_potential_score
            )
            
            return GrowthPredictionResponse(
                cow_id=request.cow_id,
                cow_name=cow_info['name'],
                ear_tag_number=cow_info['ear_tag_number'],
                predicted_peak_yield=round(predicted_peak_yield, 1),
                predicted_mature_weight=round(predicted_mature_weight, 1),
                growth_potential_score=round(growth_potential_score, 1),
                milestone_predictions=milestone_predictions,
                management_recommendations=management_recommendations,
                prediction_date=datetime.now(),
                model_version="v1.0"
            )
            
        except Exception as e:
            logger.error(f"성장 예측 실패: {str(e)}")
            raise
    
    async def comprehensive_prediction(self, request: ComprehensivePredictionRequest) -> ComprehensivePredictionResponse:
        """종합 예측 분석"""
        try:
            cow_info = await self.get_cow_basic_info(request.cow_id)
            predictions = {}
            priority_actions = []
            
            # 요청된 예측 타입별로 실행
            for prediction_type in request.prediction_types:
                try:
                    if prediction_type == PredictionModelType.DISEASE_PREDICTION:
                        disease_req = DiseasesPredictionRequest(
                            cow_id=request.cow_id,
                            milk_yield=request.milk_yield,
                            somatic_cell_count=request.somatic_cell_count,
                            conductivity=request.conductivity,
                            lactation_number=request.lactation_number,
                            days_in_milk=request.days_in_milk,
                            feed_intake=request.feed_intake,
                            use_historical_data=request.use_historical_data
                        )
                        result = await self.predict_disease(disease_req)
                        predictions["disease_prediction"] = result.dict()
                        
                        # 높은 위험도 질병이 있으면 우선 조치
                        high_risk_diseases = [p for p in result.prediction_results if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
                        if high_risk_diseases:
                            priority_actions.extend([f"긴급: {d.disease_type.value} 질병 위험 검진 필요" for d in high_risk_diseases])
                    
                    elif prediction_type == PredictionModelType.BREEDING_SUCCESS:
                        breeding_req = BreedingSuccessPredictionRequest(
                            cow_id=request.cow_id,
                            lactation_number=request.lactation_number,
                            body_condition_score=request.body_condition_score,
                            milk_yield=request.milk_yield,
                            feed_intake=request.feed_intake,
                            use_historical_data=request.use_historical_data
                        )
                        result = await self.predict_breeding_success(breeding_req)
                        predictions["breeding_success"] = result.dict()
                        
                        if result.success_probability < 0.6:
                            priority_actions.append("번식 성공률 낮음 - 체형점수 및 영양상태 점검 필요")
                    
                    # 다른 예측 타입들도 비슷하게 처리...
                    
                except Exception as e:
                    logger.error(f"예측 실패 - {prediction_type.value}: {str(e)}")
                    predictions[prediction_type.value] = {"error": str(e)}
            
            # 전체 요약 생성
            overall_summary = self._generate_overall_summary(predictions, cow_info)
            
            return ComprehensivePredictionResponse(
                cow_id=request.cow_id,
                cow_name=cow_info['name'],
                ear_tag_number=cow_info['ear_tag_number'],
                predictions=predictions,
                overall_summary=overall_summary,
                priority_actions=priority_actions,
                prediction_date=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"종합 예측 실패: {str(e)}")
            raise
    
    # === 헬퍼 메서드들 ===
    
    def _generate_health_recommendations(self, prediction_results: List[DiseasePredictionResult], 
                                       request: DiseasesPredictionRequest) -> List[str]:
        """건강 권장사항 생성"""
        recommendations = []
        
        for result in prediction_results:
            if result.risk_level == RiskLevel.CRITICAL:
                if result.disease_type == DiseaseType.MASTITIS:
                    recommendations.append("즉시 수의사 진료 - 유방염 의심")
                    if hasattr(request, 'somatic_cell_count') and request.somatic_cell_count and request.somatic_cell_count > 500000:
                        recommendations.append("체세포수 매우 높음 - 유방 마사지 및 위생 관리 강화")
            elif result.risk_level == RiskLevel.HIGH:
                if result.disease_type == DiseaseType.MASTITIS:
                    recommendations.append("유방염 예방 관리 - 착유기 위생 점검")
                elif result.disease_type == DiseaseType.METABOLIC_DISORDER:
                    recommendations.append("대사성 질환 위험 - 사료 배합 재검토 필요")
        
        if not recommendations:
            recommendations.append("현재 건강상태 양호 - 정기 검진 지속")
        
        return recommendations
    
    def _calculate_optimal_breeding_window(self, request: BreedingSuccessPredictionRequest) -> Dict[str, str]:
        """최적 수정 시기 계산"""
        if request.days_since_calving:
            optimal_start = max(45, request.days_since_calving + 7)
            optimal_end = optimal_start + 14
            
            return {
                "start_date": (datetime.now() + timedelta(days=optimal_start - request.days_since_calving)).strftime('%Y-%m-%d'),
                "end_date": (datetime.now() + timedelta(days=optimal_end - request.days_since_calving)).strftime('%Y-%m-%d'),
                "days_from_calving": f"{optimal_start}-{optimal_end}일"
            }
        
        return {
            "recommendation": "분만 후 60-80일 이후 수정 권장"
        }
    
    def _identify_breeding_risk_factors(self, request: BreedingSuccessPredictionRequest, 
                                      success_probability: float) -> List[str]:
        """번식 위험 요소 식별"""
        risk_factors = []
        
        if request.body_condition_score and request.body_condition_score < 2.5:
            risk_factors.append("체형점수 낮음 (영양 부족)")
        
        if request.days_since_calving and request.days_since_calving < 45:
            risk_factors.append("분만 후 경과일 부족")
        
        if request.previous_breeding_attempts and request.previous_breeding_attempts > 3:
            risk_factors.append("반복 수정 이력")
        
        if request.milk_yield and request.milk_yield > 35:
            risk_factors.append("고능력우 - 에너지 밸런스 관리 필요")
        
        return risk_factors
    
    def _generate_breeding_recommendations(self, success_probability: float, 
                                         risk_factors: List[str]) -> List[str]:
        """번식 권장사항 생성"""
        recommendations = []
        
        if success_probability >= 0.8:
            recommendations.append("수정 적기 - 발정 관찰 강화")
        elif success_probability >= 0.6:
            recommendations.append("수정 가능 - 체형점수 관리 필요")
        else:
            recommendations.append("수정 연기 권장 - 영양 및 건강상태 개선 우선")
        
        if "체형점수 낮음" in risk_factors:
            recommendations.append("고에너지 사료 급여 증가")
        
        if "분만 후 경과일 부족" in risk_factors:
            recommendations.append("자궁 회복 기간 충분히 확보")
        
        return recommendations
    
    def _generate_feed_optimization_suggestions(self, efficiency_grade: EfficiencyGrade, 
                                              actual_efficiency: float, 
                                              predicted_optimal: float) -> List[str]:
        """사료 최적화 제안"""
        suggestions = []
        
        if efficiency_grade == EfficiencyGrade.POOR:
            suggestions.extend([
                "사료 품질 점검 필요",
                "소화율 높은 사료로 교체 검토",
                "급여 횟수 증가 (3-4회/일)"
            ])
        elif efficiency_grade == EfficiencyGrade.AVERAGE:
            suggestions.extend([
                "사료 배합비 최적화",
                "급여 시간 일정하게 유지"
            ])
        else:
            suggestions.append("현재 사료 관리 상태 우수")
        
        efficiency_gap = predicted_optimal - actual_efficiency
        if efficiency_gap > 0.2:
            suggestions.append(f"효율 개선 여지 {efficiency_gap:.1f}L/kg - 전문가 상담 권장")
        
        return suggestions
    
    def _generate_quality_improvement_recommendations(self, predictions: List[MilkQualityPrediction], 
                                                    request: MilkQualityPredictionRequest) -> List[str]:
        """품질 개선 권장사항"""
        recommendations = []
        
        avg_fat = sum(p.fat_percentage for p in predictions) / len(predictions)
        avg_protein = sum(p.protein_percentage for p in predictions) / len(predictions)
        
        if avg_fat < 3.5:
            recommendations.append("유지방 개선 - 섬유질 사료 증가")
        
        if avg_protein < 3.2:
            recommendations.append("유단백 개선 - 단백질 사료 보강")
        
        if any(p.quality_grade in ["2등급", "3등급"] for p in predictions):
            recommendations.extend([
                "사료 품질 점검",
                "급여량 재조정",
                "스트레스 요인 제거"
            ])
        
        return recommendations
    
    def _generate_growth_management_recommendations(self, request: GrowthPredictionRequest, 
                                                  predicted_peak_yield: float, 
                                                  growth_potential_score: float) -> List[str]:
        """성장 관리 권장사항"""
        recommendations = []
        
        if growth_potential_score >= 80:
            recommendations.extend([
                "우수한 성장 잠재력 - 집중 관리 투자 권장",
                "고품질 육성용 사료 급여",
                "정기 체중 측정 및 성장 모니터링"
            ])
        elif growth_potential_score >= 60:
            recommendations.extend([
                "평균 이상 잠재력 - 안정적 관리",
                "균형잡힌 영양 공급"
            ])
        else:
            recommendations.extend([
                "성장 잠재력 개선 필요",
                "영양사 상담 권장",
                "건강검진 강화"
            ])
        
        if request.current_age_months < 15:
            recommendations.append("초기 성장기 - 골격 발달 중점 관리")
        elif request.current_age_months < 24:
            recommendations.append("번식 준비기 - 체형점수 관리")
        
        return recommendations
    
    def _generate_overall_summary(self, predictions: Dict, cow_info: Dict) -> Dict[str, Any]:
        """전체 요약 생성"""
        summary = {
            "cow_overview": {
                "name": cow_info['name'],
                "age_months": cow_info['age_months'],
                "breed": cow_info['breed']
            },
            "health_status": "점검 필요",
            "management_priority": "중간",
            "economic_outlook": "양호"
        }
        
        # 질병 예측이 있는 경우
        if "disease_prediction" in predictions:
            disease_data = predictions["disease_prediction"]
            if disease_data.get("overall_health_score", 0) < 70:
                summary["health_status"] = "주의 필요"
                summary["management_priority"] = "높음"
        
        # 번식 예측이 있는 경우
        if "breeding_success" in predictions:
            breeding_data = predictions["breeding_success"]
            if breeding_data.get("success_probability", 0) < 0.6:
                summary["management_priority"] = "높음"
        
        return summary