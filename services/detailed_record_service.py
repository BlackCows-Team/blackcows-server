# services/detailed_record_service.py

from datetime import datetime
from typing import List, Dict, Optional
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
from schemas.detailed_record import *
import uuid

class DetailedRecordService:
    
    @staticmethod
    def create_milking_record(record_data: MilkingRecordCreate, user: Dict) -> DetailedRecordResponse:
        """착유 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 젖소 존재 확인
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            milking_data = {
                "milking_start_time": record_data.milking_start_time,
                "milking_end_time": record_data.milking_end_time,
                "milk_yield": record_data.milk_yield,
                "milking_session": record_data.milking_session,
                "conductivity": record_data.conductivity,
                "somatic_cell_count": record_data.somatic_cell_count,
                "blood_flow_detected": record_data.blood_flow_detected,
                "color_value": record_data.color_value,
                "temperature": record_data.temperature,
                "fat_percentage": record_data.fat_percentage,
                "protein_percentage": record_data.protein_percentage,
                "air_flow_value": record_data.air_flow_value,
                "lactation_number": record_data.lactation_number,
                "rumination_time": record_data.rumination_time,
                "collection_code": record_data.collection_code,
                "collection_count": record_data.collection_count,
                "notes": record_data.notes
            }
            
            # 제목 자동 생성
            title = f"착유 기록"
            if record_data.milk_yield:
                title += f" ({record_data.milk_yield}L)"
            if record_data.milking_session:
                title += f" - {record_data.milking_session}회차"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.MILKING.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": milking_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.MILKING,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=milking_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"착유 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_estrus_record(record_data: EstrusRecordCreate, user: Dict) -> DetailedRecordResponse:
        """발정 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            estrus_data = {
                "estrus_start_time": record_data.estrus_start_time,
                "estrus_intensity": record_data.estrus_intensity,
                "estrus_duration": record_data.estrus_duration,
                "behavior_signs": record_data.behavior_signs or [],
                "visual_signs": record_data.visual_signs or [],
                "detected_by": record_data.detected_by,
                "detection_method": record_data.detection_method,
                "next_expected_estrus": record_data.next_expected_estrus,
                "breeding_planned": record_data.breeding_planned,
                "notes": record_data.notes
            }
            
            title = f"발정 발견"
            if record_data.estrus_intensity:
                title += f" ({record_data.estrus_intensity})"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.ESTRUS.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": estrus_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.ESTRUS,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=estrus_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"발정 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_insemination_record(record_data: InseminationRecordCreate, user: Dict) -> DetailedRecordResponse:
        """인공수정 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            insemination_data = {
                "insemination_time": record_data.insemination_time,
                "bull_id": record_data.bull_id,
                "bull_breed": record_data.bull_breed,
                "semen_batch": record_data.semen_batch,
                "semen_quality": record_data.semen_quality,
                "technician_name": record_data.technician_name,
                "insemination_method": record_data.insemination_method,
                "cervix_condition": record_data.cervix_condition,
                "success_probability": record_data.success_probability,
                "cost": record_data.cost,
                "pregnancy_check_scheduled": record_data.pregnancy_check_scheduled,
                "notes": record_data.notes
            }
            
            title = f"인공수정 실시"
            if record_data.bull_breed:
                title += f" ({record_data.bull_breed})"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.INSEMINATION.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": insemination_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.INSEMINATION,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=insemination_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"인공수정 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_pregnancy_check_record(record_data: PregnancyCheckRecordCreate, user: Dict) -> DetailedRecordResponse:
        """임신감정 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            pregnancy_data = {
                "check_method": record_data.check_method,
                "check_result": record_data.check_result,
                "pregnancy_stage": record_data.pregnancy_stage,
                "fetus_condition": record_data.fetus_condition,
                "expected_calving_date": record_data.expected_calving_date,
                "veterinarian": record_data.veterinarian,
                "check_cost": record_data.check_cost,
                "next_check_date": record_data.next_check_date,
                "additional_care": record_data.additional_care,
                "notes": record_data.notes
            }
            
            title = f"임신감정"
            if record_data.check_result:
                title += f" - {record_data.check_result}"
            if record_data.pregnancy_stage:
                title += f" ({record_data.pregnancy_stage}일)"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.PREGNANCY_CHECK.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": pregnancy_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.PREGNANCY_CHECK,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=pregnancy_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"임신감정 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod 
    def create_calving_record(record_data: CalvingRecordCreate, user: Dict) -> DetailedRecordResponse:
        """분만 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            calving_data = {
                "calving_start_time": record_data.calving_start_time,
                "calving_end_time": record_data.calving_end_time,
                "calving_difficulty": record_data.calving_difficulty,
                "calf_count": record_data.calf_count,
                "calf_gender": record_data.calf_gender or [],
                "calf_weight": record_data.calf_weight or [],
                "calf_health": record_data.calf_health or [],
                "placenta_expelled": record_data.placenta_expelled,
                "placenta_expulsion_time": record_data.placenta_expulsion_time,
                "complications": record_data.complications or [],
                "assistance_required": record_data.assistance_required,
                "veterinarian_called": record_data.veterinarian_called,
                "dam_condition": record_data.dam_condition,
                "lactation_start": record_data.lactation_start,
                "notes": record_data.notes
            }
            
            title = f"분만 완료"
            if record_data.calf_count:
                title += f" (송아지 {record_data.calf_count}마리)"
            if record_data.calving_difficulty:
                title += f" - {record_data.calving_difficulty}"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.CALVING.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": calving_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.CALVING,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=calving_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"분만 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_feed_record(record_data: FeedRecordCreate, user: Dict) -> DetailedRecordResponse:
        """사료급여 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            feed_data = {
                "feed_time": record_data.feed_time,
                "feed_type": record_data.feed_type,
                "feed_amount": record_data.feed_amount,
                "feed_quality": record_data.feed_quality,
                "supplement_type": record_data.supplement_type,
                "supplement_amount": record_data.supplement_amount,
                "water_consumption": record_data.water_consumption,
                "appetite_condition": record_data.appetite_condition,
                "feed_efficiency": record_data.feed_efficiency,
                "cost_per_feed": record_data.cost_per_feed,
                "fed_by": record_data.fed_by,
                "notes": record_data.notes
            }
            
            title = f"사료급여"
            if record_data.feed_type:
                title += f" ({record_data.feed_type})"
            if record_data.feed_amount:
                title += f" {record_data.feed_amount}kg"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.FEED.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": feed_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.FEED,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=feed_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"사료급여 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_health_check_record(record_data: HealthCheckRecordCreate, user: Dict) -> DetailedRecordResponse:
        """건강검진 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            health_data = {
                "check_time": record_data.check_time,
                "body_temperature": record_data.body_temperature,
                "heart_rate": record_data.heart_rate,
                "respiratory_rate": record_data.respiratory_rate,
                "body_condition_score": record_data.body_condition_score,
                "udder_condition": record_data.udder_condition,
                "hoof_condition": record_data.hoof_condition,
                "coat_condition": record_data.coat_condition,
                "eye_condition": record_data.eye_condition,
                "nose_condition": record_data.nose_condition,
                "appetite": record_data.appetite,
                "activity_level": record_data.activity_level,
                "abnormal_symptoms": record_data.abnormal_symptoms or [],
                "examiner": record_data.examiner,
                "next_check_date": record_data.next_check_date,
                "notes": record_data.notes
            }
            
            title = f"건강검진"
            if record_data.body_condition_score:
                title += f" (체형점수: {record_data.body_condition_score})"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.HEALTH_CHECK.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": health_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.HEALTH_CHECK,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=health_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"건강검진 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_vaccination_record(record_data: VaccinationRecordCreate, user: Dict) -> DetailedRecordResponse:
        """백신접종 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            vaccination_data = {
                "vaccination_time": record_data.vaccination_time,
                "vaccine_name": record_data.vaccine_name,
                "vaccine_type": record_data.vaccine_type,
                "vaccine_batch": record_data.vaccine_batch,
                "dosage": record_data.dosage,
                "injection_site": record_data.injection_site,
                "injection_method": record_data.injection_method,
                "administrator": record_data.administrator,
                "vaccine_manufacturer": record_data.vaccine_manufacturer,
                "expiry_date": record_data.expiry_date,
                "adverse_reaction": record_data.adverse_reaction,
                "reaction_details": record_data.reaction_details,
                "next_vaccination_due": record_data.next_vaccination_due,
                "cost": record_data.cost,
                "notes": record_data.notes
            }
            
            title = f"백신접종"
            if record_data.vaccine_name:
                title += f" ({record_data.vaccine_name})"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.VACCINATION.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": vaccination_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.VACCINATION,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=vaccination_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"백신접종 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_weight_record(record_data: WeightRecordCreate, user: Dict) -> DetailedRecordResponse:
        """체중측정 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            weight_data = {
                "measurement_time": record_data.measurement_time,
                "weight": record_data.weight,
                "measurement_method": record_data.measurement_method,
                "body_condition_score": record_data.body_condition_score,
                "height_withers": record_data.height_withers,
                "body_length": record_data.body_length,
                "chest_girth": record_data.chest_girth,
                "growth_rate": record_data.growth_rate,
                "target_weight": record_data.target_weight,
                "weight_category": record_data.weight_category,
                "measurer": record_data.measurer,
                "notes": record_data.notes
            }
            
            title = f"체중측정"
            if record_data.weight:
                title += f" ({record_data.weight}kg)"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.WEIGHT.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": weight_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.WEIGHT,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=weight_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"체중측정 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def create_treatment_record(record_data: TreatmentRecordCreate, user: Dict) -> DetailedRecordResponse:
        """치료 기록 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            treatment_data = {
                "treatment_time": record_data.treatment_time,
                "treatment_type": record_data.treatment_type,
                "symptoms": record_data.symptoms or [],
                "diagnosis": record_data.diagnosis,
                "medication_used": record_data.medication_used or [],
                "dosage_info": record_data.dosage_info or {},
                "treatment_method": record_data.treatment_method,
                "treatment_duration": record_data.treatment_duration,
                "veterinarian": record_data.veterinarian,
                "treatment_response": record_data.treatment_response,
                "side_effects": record_data.side_effects,
                "follow_up_required": record_data.follow_up_required,
                "follow_up_date": record_data.follow_up_date,
                "treatment_cost": record_data.treatment_cost,
                "withdrawal_period": record_data.withdrawal_period,
                "notes": record_data.notes
            }
            
            title = f"치료"
            if record_data.diagnosis:
                title += f" ({record_data.diagnosis})"
            elif record_data.treatment_type:
                title += f" ({record_data.treatment_type})"
            
            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.TREATMENT.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": record_data.notes,
                "record_data": treatment_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.TREATMENT,
                record_date=record_data.record_date,
                title=title,
                description=record_data.notes,
                record_data=treatment_data,
                farm_id=farm_id,
                owner_id=user.get("id"),
                created_at=current_time,
                updated_at=current_time,
                is_active=True
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"치료 기록 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_detailed_records_by_cow(cow_id: str, farm_id: str, record_type: Optional[DetailedRecordType] = None) -> List[DetailedRecordSummary]:
        """특정 젖소의 상세 기록 목록 조회"""
        try:
            db = get_firestore_client()
            cow_info = DetailedRecordService._get_cow_info(cow_id, farm_id)
            
            query = db.collection('cow_detailed_records')\
                .where('cow_id', '==', cow_id)\
                .where('farm_id', '==', farm_id)\
                .where('is_active', '==', True)
            
            if record_type:
                query = query.where('record_type', '==', record_type.value)
            
            records_query = query.order_by('record_date', direction='DESCENDING').get()
            
            records = []
            for record_doc in records_query:
                record_data = record_doc.to_dict()
                
                # 기록 유형별 주요 수치 추출
                key_values = DetailedRecordService._extract_key_values(
                    record_data["record_type"], 
                    record_data["record_data"]
                )
                
                records.append(DetailedRecordSummary(
                    id=record_data["id"],
                    cow_id=record_data["cow_id"],
                    cow_name=cow_info["name"],
                    cow_ear_tag_number=cow_info["ear_tag_number"],
                    record_type=DetailedRecordType(record_data["record_type"]),
                    record_date=record_data["record_date"],
                    title=record_data["title"],
                    key_values=key_values,
                    created_at=record_data["created_at"]
                ))
            
            return records
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"상세 기록 목록 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_detailed_record_by_id(record_id: str, farm_id: str) -> DetailedRecordResponse:
        """상세 기록 단건 조회"""
        try:
            db = get_firestore_client()
            record_doc = db.collection('cow_detailed_records').document(record_id).get()
            
            if not record_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="기록을 찾을 수 없습니다"
                )
            
            record_data = record_doc.to_dict()
            
            if record_data.get("farm_id") != farm_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="기록을 찾을 수 없습니다"
                )
            
            cow_info = DetailedRecordService._get_cow_info(record_data["cow_id"], farm_id)
            
            return DetailedRecordResponse(
                id=record_data["id"],
                cow_id=record_data["cow_id"],
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType(record_data["record_type"]),
                record_date=record_data["record_date"],
                title=record_data["title"],
                description=record_data.get("description"),
                record_data=record_data["record_data"],
                farm_id=record_data["farm_id"],
                owner_id=record_data["owner_id"],
                created_at=record_data["created_at"],
                updated_at=record_data["updated_at"],
                is_active=record_data["is_active"]
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"상세 기록 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def delete_detailed_record(record_id: str, user: Dict) -> Dict:
        """상세 기록 삭제 (소프트 삭제)"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            existing_record = DetailedRecordService.get_detailed_record_by_id(record_id, farm_id)
            
            db.collection('cow_detailed_records').document(record_id).update({
                "is_active": False,
                "updated_at": datetime.utcnow(),
                "deleted_at": datetime.utcnow()
            })
            
            return {
                "message": f"기록 '{existing_record.title}'이 삭제되었습니다",
                "record_id": record_id
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"기록 삭제 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def _get_cow_info(cow_id: str, farm_id: str) -> Dict:
        """젖소 정보 조회 (내부 사용)"""
        db = get_firestore_client()
        cow_doc = db.collection('cows').document(cow_id).get()
        
        if not cow_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="젖소를 찾을 수 없습니다"
            )
        
        cow_data = cow_doc.to_dict()
        
        if cow_data.get("farm_id") != farm_id or not cow_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="젖소를 찾을 수 없습니다"
            )
        
        return cow_data
    
    @staticmethod
    def _extract_key_values(record_type: str, record_data: Dict) -> Dict[str, Any]:
        """기록 유형별 주요 수치 추출"""
        key_values = {}
        
        if record_type == DetailedRecordType.MILKING.value:
            if record_data.get("milk_yield"):
                key_values["milk_yield"] = f"{record_data['milk_yield']}L"
            if record_data.get("milking_session"):
                key_values["session"] = f"{record_data['milking_session']}회차"
            if record_data.get("fat_percentage"):
                key_values["fat"] = f"{record_data['fat_percentage']}%"
        
        elif record_type == DetailedRecordType.WEIGHT.value:
            if record_data.get("weight"):
                key_values["weight"] = f"{record_data['weight']}kg"
            if record_data.get("body_condition_score"):
                key_values["bcs"] = f"{record_data['body_condition_score']}"
        
        elif record_type == DetailedRecordType.ESTRUS.value:
            if record_data.get("estrus_intensity"):
                key_values["intensity"] = record_data["estrus_intensity"]
            if record_data.get("estrus_duration"):
                key_values["duration"] = f"{record_data['estrus_duration']}시간"
        
        elif record_type == DetailedRecordType.PREGNANCY_CHECK.value:
            if record_data.get("check_result"):
                key_values["result"] = record_data["check_result"]
            if record_data.get("pregnancy_stage"):
                key_values["stage"] = f"{record_data['pregnancy_stage']}일"
        
        elif record_type == DetailedRecordType.CALVING.value:
            if record_data.get("calf_count"):
                key_values["calf_count"] = f"{record_data['calf_count']}마리"
            if record_data.get("calving_difficulty"):
                key_values["difficulty"] = record_data["calving_difficulty"]
        
        elif record_type == DetailedRecordType.FEED.value:
            if record_data.get("feed_amount"):
                key_values["amount"] = f"{record_data['feed_amount']}kg"
            if record_data.get("feed_type"):
                key_values["type"] = record_data["feed_type"]
        
        elif record_type == DetailedRecordType.VACCINATION.value:
            if record_data.get("vaccine_name"):
                key_values["vaccine"] = record_data["vaccine_name"]
            if record_data.get("dosage"):
                key_values["dosage"] = f"{record_data['dosage']}ml"
        
        elif record_type == DetailedRecordType.TREATMENT.value:
            if record_data.get("diagnosis"):
                key_values["diagnosis"] = record_data["diagnosis"]
            if record_data.get("treatment_cost"):
                key_values["cost"] = f"{record_data['treatment_cost']:,}원"
        
        return key_values