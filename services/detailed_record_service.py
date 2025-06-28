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
        """착유 기록 생성 (필수 필드: cow_id, record_date, milk_yield)"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 젖소 존재 확인
            cow_info = DetailedRecordService._get_cow_info(record_data.cow_id, farm_id)
            
            # 필수 필드 재검증 (Pydantic에서 이미 검증하지만 추가 보안)
            if not record_data.record_date or len(record_data.record_date.strip()) == 0:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                    detail="착유 날짜는 필수입니다"
                )
        
            if not record_data.milk_yield or record_data.milk_yield <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="착유량은 필수이며 0보다 커야 합니다"
                )
            
            record_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            milking_data = {
                # 필수 필드
                "record_date": record_data.record_date,
                "milk_yield": record_data.milk_yield,

                # 선택 필드
                "milking_start_time": record_data.milking_start_time,
                "milking_end_time": record_data.milking_end_time,
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
            title_parts = []
        
            if record_data.milk_yield:
                title_parts.append(f"{record_data.milk_yield}L")
        
            if record_data.milking_session:
                title_parts.append(f"{record_data.milking_session}회차")
        
            if record_data.milking_start_time:
                title_parts.append(f"{record_data.milking_start_time}")
        
            if title_parts:
                title += f" ({', '.join(title_parts)})"
            
            # 설명 자동 생성
            description_parts = []
            if record_data.fat_percentage:
                description_parts.append(f"유지방 {record_data.fat_percentage}%")
            if record_data.protein_percentage:
                description_parts.append(f"유단백 {record_data.protein_percentage}%")
            if record_data.somatic_cell_count:
                description_parts.append(f"체세포수 {record_data.somatic_cell_count:,}")
        
            auto_description = ", ".join(description_parts) if description_parts else None
            final_description = record_data.notes or auto_description
        

            record_document = {
                "id": record_id,
                "cow_id": record_data.cow_id,
                "record_type": DetailedRecordType.MILKING.value,
                "record_date": record_data.record_date,
                "title": title,
                "description": final_description,
                "record_data": milking_data,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            # Firestore에 저장
            db.collection('cow_detailed_records').document(record_id).set(record_document)
            
            return DetailedRecordResponse(
                id=record_id,
                cow_id=record_data.cow_id,
                cow_name=cow_info["name"],
                cow_ear_tag_number=cow_info["ear_tag_number"],
                record_type=DetailedRecordType.MILKING,
                record_date=record_data.record_date,
                title=title,
                description=final_description,
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
            print("🔥 저장될 record_data:", estrus_data)
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
            print("[DEBUG] 수신된 record_data:", record_data)
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
    def get_detailed_records_by_cow(cow_id: str, farm_id: str, record_type: Optional[DetailedRecordType] = None, limit: int = 100) -> List[DetailedRecordSummary]:
        """특정 젖소의 상세 기록 목록 조회 (500 오류 해결)"""
        try:
            db = get_firestore_client()
            
            # 젖소 정보 안전하게 조회 (실패해도 계속 진행)
            cow_info = None
            try:
                cow_info = DetailedRecordService._get_cow_info(cow_id, farm_id)
            except:
                # 젖소 정보 조회 실패 시 기본값 사용
                cow_info = {
                    "name": "알 수 없음",
                    "ear_tag_number": "N/A"
                }
            
            # 기본 쿼리 구성
            query = (db.collection('cow_detailed_records')
                    .where('cow_id', '==', cow_id)
                    .where('farm_id', '==', farm_id)
                    .where('is_active', '==', True))
            
            # 기록 타입 필터링 (선택적)
            if record_type:
                query = query.where('record_type', '==', record_type.value)
            
            # 정렬 및 제한 적용
            records_query = query.order_by('record_date', direction='DESCENDING').limit(limit).get()
            
            records = []
            for record_doc in records_query:
                try:
                    record_data = record_doc.to_dict()
                    
                    # 기록 유형별 주요 수치 추출 (안전하게)
                    key_values = DetailedRecordService._extract_key_values(
                        record_data.get("record_type", ""), 
                        record_data.get("record_data", {})
                    )
                    
                    # 수정된 부분: 필수 필드에 기본값 제공
                    records.append(DetailedRecordSummary(
                        id=record_data.get("id", ""),
                        cow_id=record_data.get("cow_id", cow_id),
                        cow_name=cow_info.get("name", "알 수 없음"),  # 기본값 제공
                        cow_ear_tag_number=cow_info.get("ear_tag_number", "N/A"),  # 기본값 제공
                        record_type=DetailedRecordType(record_data.get("record_type", "other")),
                        record_date=record_data.get("record_date", ""),
                        title=record_data.get("title", "제목 없음"),
                        description=record_data.get("description"),  # Optional 필드
                        key_values=key_values or {},  # 기본값 제공
                        created_at=record_data.get("created_at", datetime.utcnow())
                    ))
                except Exception as record_error:
                    # 개별 기록 처리 실패 시 로그만 남기고 계속 진행
                    print(f"[WARNING] 기록 처리 실패 (ID: {record_doc.id}): {str(record_error)}")
                    continue
            
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
        """젖소 정보 조회 (내부 사용) - 안전한 오류 처리"""
        try:
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
            
        except Exception as e:
            # 젖소 정보 조회 실패 시 기본 정보 반환 (500 에러 방지)
            print(f"[WARNING] 젖소 정보 조회 실패 (cow_id: {cow_id}): {str(e)}")
            return {
                "name": "알 수 없음",
                "ear_tag_number": "N/A",
                "id": cow_id,
                "farm_id": farm_id
            }
    
    @staticmethod
    def _extract_key_values(record_type: str, record_data: Dict) -> Dict[str, Any]:
        """기록 유형별 주요 수치 추출 - 안전한 처리"""
        try:
            key_values = {}
            
            if record_type == DetailedRecordType.MILKING.value:
                if record_data.get("milk_yield"):
                    key_values["milk_yield"] = f"{record_data['milk_yield']}L"
                if record_data.get("milking_session"):
                    key_values["session"] = f"{record_data['milking_session']}회차"
                if record_data.get("fat_percentage"):
                    key_values["fat"] = f"{record_data['fat_percentage']}%"
            
            elif record_type == DetailedRecordType.WEIGHT.value:
                print(f"[DEBUG] record_type: {record_type}, record_data: {record_data}")
                if record_data.get("weight"):
                    key_values["weight"] = f"{record_data['weight']}kg"
                if record_data.get("body_condition_score"):
                    key_values["bcs"] = f"{record_data['body_condition_score']}"
                if record_data.get("measurement_method"):
                    key_values["method"] = record_data["measurement_method"]
                if record_data.get("measurement_time"):
                    key_values["time"] = record_data["measurement_time"]
                if record_data.get("height_withers"):
                    key_values["height_withers"] = f"{record_data['height_withers']}cm"
                if record_data.get("body_length"):
                    key_values["body_length"] = f"{record_data['body_length']}cm"
                if record_data.get("chest_girth"):
                    key_values["chest_girth"] = f"{record_data['chest_girth']}cm"
                if record_data.get("growth_rate"):
                    key_values["growth_rate"] = f"{record_data['growth_rate']}%"
                if record_data.get("target_weight"):
                    key_values["target_weight"] = f"{record_data['target_weight']}kg"
                if record_data.get("weight_category"):
                    key_values["category"] = record_data["weight_category"]
                if record_data.get("measurer"):
                    key_values["measurer"] = record_data["measurer"]
                if record_data.get("notes"):
                    key_values["notes"] = record_data["notes"]
            
            elif record_type == DetailedRecordType.ESTRUS.value:
                if record_data.get("estrus_intensity"):
                    key_values["intensity"] = record_data["estrus_intensity"]
                if record_data.get("estrus_duration"):
                    key_values["duration"] = f"{record_data['estrus_duration']}시간"
                if record_data.get("visual_signs"):  # 👁️ 육안 관찰
                    key_values["visual_signs"] = record_data["visual_signs"]
                if record_data.get("next_expected_estrus"):  # 📅 다음 발정 예상일
                    key_values["next_expected_estrus"] = record_data["next_expected_estrus"]
                if "breeding_planned" in record_data:  # 🎯 교배 계획
                    key_values["breeding_planned"] = record_data["breeding_planned"]
            
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
                if record_data.get("vaccination_time"):
                    key_values["vaccination_time"] = record_data["vaccination_time"]
                if record_data.get("vaccine_name"):
                    key_values["vaccine"] = record_data["vaccine_name"]
                if record_data.get("vaccine_type"):
                    key_values["vaccine_type"] = record_data["vaccine_type"]
                if record_data.get("vaccine_batch"):
                    key_values["vaccine_batch"] = record_data["vaccine_batch"]
                if record_data.get("dosage"):
                    key_values["dosage"] = f"{record_data['dosage']}ml"
                if record_data.get("injection_site"):
                    key_values["injection_site"] = record_data["injection_site"]
                if record_data.get("injection_method"):
                    key_values["injection_method"] = record_data["injection_method"]
                if record_data.get("administrator"):
                    key_values["administrator"] = record_data["administrator"]
                if record_data.get("vaccine_manufacturer"):
                    key_values["vaccine_manufacturer"] = record_data["vaccine_manufacturer"]
                if record_data.get("expiry_date"):
                    key_values["expiry_date"] = record_data["expiry_date"]
                if record_data.get("adverse_reaction") is not None:
                    key_values["adverse_reaction"] = "있음" if record_data["adverse_reaction"] else "없음"
                if record_data.get("reaction_details"):
                    key_values["reaction_details"] = record_data["reaction_details"]
                if record_data.get("next_vaccination_due"):
                    key_values["next_vaccination_due"] = record_data["next_vaccination_due"]
                if record_data.get("cost"):
                    key_values["cost"] = f"{record_data['cost']}원"
                if record_data.get("notes"):
                    key_values["notes"] = record_data["notes"]

            
            elif record_type == DetailedRecordType.TREATMENT.value:
                print(f"[DEBUG] record_type: {record_type}, record_data: {record_data}")
                if record_data.get("diagnosis"):
                    key_values["진단명"] = record_data["diagnosis"]
                if record_data.get("treatment_cost"):
                    key_values["비용"] = f"{record_data['treatment_cost']:,}원"
                if record_data.get("treatment_method"):
                    key_values["치료 방법"] = record_data["treatment_method"]
                if record_data.get("veterinarian"):
                    key_values["수의사"] = record_data["veterinarian"]
                if record_data.get("medication_used"):
                    key_values["투여 약물"] = ", ".join(record_data["medication_used"])
                if record_data.get("treatment_duration"):
                    key_values["치료 기간"] = f"{record_data['treatment_duration']}일"
                if record_data.get("follow_up_date"):
                    key_values["추후 검사일"] = record_data["follow_up_date"]
                if record_data.get("withdrawal_period"):
                    key_values["휴약 기간"] = f"{record_data['withdrawal_period']}일"
                if record_data.get("side_effects"):
                    key_values["부작용"] = record_data["side_effects"]
                if record_data.get("treatment_response"):
                    key_values["치료 반응"] = record_data["treatment_response"]
                if record_data.get("notes"):
                    key_values["비고"] = record_data["notes"]

            
            elif record_type == DetailedRecordType.HEALTH_CHECK.value:
                if record_data.get("body_temperature"):
                    key_values["temperature"] = f"{record_data['body_temperature']}°C"
                if record_data.get("body_condition_score"):
                    key_values["bcs"] = f"{record_data['body_condition_score']}"
                if record_data.get("heart_rate"):
                    key_values["heart_rate"] = f"{record_data['heart_rate']}회/분"
                if record_data.get("respiratory_rate"):
                    key_values["respiratory_rate"] = f"{record_data['respiratory_rate']}회/분"
                if record_data.get("mobility_score"):
                    key_values["mobility"] = f"{record_data['mobility_score']}점"
                if record_data.get("appetite_level"):
                    key_values["appetite"] = record_data["appetite_level"]
                if record_data.get("activity_level"):
                    key_values["activity"] = record_data["activity_level"]
                if record_data.get("remarks"):
                    key_values["remarks"] = record_data["remarks"]
                if record_data.get("check_time"):
                    key_values["check_time"] = record_data["check_time"]
                if record_data.get("examiner"):
                    key_values["examiner"] = record_data["examiner"]
                if record_data.get("eye_condition"):
                    key_values["eye_condition"] = record_data["eye_condition"]
                if record_data.get("nose_condition"):
                    key_values["nose_condition"] = record_data["nose_condition"]
                if record_data.get("coat_condition"):
                    key_values["coat_condition"] = record_data["coat_condition"]
                if record_data.get("hoof_condition"):
                    key_values["hoof_condition"] = record_data["hoof_condition"]
                if record_data.get("udder_condition"):
                    key_values["udder_condition"] = record_data["udder_condition"]
                if record_data.get("abnormal_symptoms"):
                    key_values["abnormal_symptoms"] = record_data["abnormal_symptoms"]
                if record_data.get("next_check_date"):
                    key_values["next_check_date"] = record_data["next_check_date"]



            elif record_type == DetailedRecordType.INSEMINATION.value:
                print(f"[DEBUG] record_type: {record_type}, record_data: {record_data}")

                if record_data.get("insemination_time"):
                    key_values["insemination_time"] = record_data["insemination_time"]
                if record_data.get("bull_id"):
                    key_values["bull_id"] = record_data["bull_id"]
                if record_data.get("bull_breed"):
                    key_values["bull"] = record_data["bull_breed"]
                if record_data.get("semen_batch"):
                    key_values["semen_batch"] = record_data["semen_batch"]
                if record_data.get("semen_quality"):
                    key_values["semen_quality"] = record_data["semen_quality"]
                if record_data.get("technician_name"):
                    key_values["technician"] = record_data["technician_name"]
                if record_data.get("insemination_method"):
                    key_values["method"] = record_data["insemination_method"]
                if record_data.get("cervix_condition"):
                    key_values["cervix_condition"] = record_data["cervix_condition"]
                if record_data.get("success_probability") is not None:
                    key_values["success_probability"] = f"{record_data['success_probability']}%"
                if record_data.get("cost") is not None:
                    key_values["cost"] = f"{record_data['cost']}원"
                if record_data.get("pregnancy_check_scheduled"):
                    key_values["pregnancy_check_scheduled"] = record_data["pregnancy_check_scheduled"]
                if record_data.get("notes"):
                    key_values["notes"] = record_data["notes"]

            
            return key_values
            
        except Exception as e:
            # 키 값 추출 실패 시 빈 딕셔너리 반환
            print(f"[WARNING] 키 값 추출 실패 (record_type: {record_type}): {str(e)}")
            return {}