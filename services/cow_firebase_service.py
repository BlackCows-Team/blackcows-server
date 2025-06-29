# services/cow_firebase_service.py

from datetime import datetime
from typing import List, Dict, Optional
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
from schemas.cow import (
    CowCreate, CowResponse, CowUpdate, HealthStatus, BreedingStatus,
    CowDetailUpdate, CowDetailResponse, Temperament, MilkingBehavior
)
import uuid

# Firestore 클라이언트
db = get_firestore_client()

class CowFirebaseService:
    
    @staticmethod
    def create_cow(cow_data: CowCreate, user: Dict) -> CowResponse:
        """새로운 젖소 등록"""
        try:
            # 전체 시스템에서 이표번호 중복 확인 (농장 구분 없이)
            existing_cow_query = (db.collection('cows')
                                .where('ear_tag_number', '==', cow_data.ear_tag_number)
                                .where('is_active', '==', True)
                                .get())
            
            if existing_cow_query:
                existing_cow = existing_cow_query[0].to_dict()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"이표번호 '{cow_data.ear_tag_number}'는 이미 다른 농장에서 등록되어 있습니다"
                )
            
            # 센서 번호가 제공된 경우에만 중복 확인 (농장별로)
            farm_id = user.get("farm_id")
            if cow_data.sensor_number:
                existing_sensor_query = (db.collection('cows')
                                       .where('farm_id', '==', farm_id)
                                       .where('sensor_number', '==', cow_data.sensor_number)
                                       .where('is_active', '==', True)
                                       .get())
                
                if existing_sensor_query:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"센서 번호 '{cow_data.sensor_number}'는 이미 사용 중입니다"
                    )
            
            # 새 젖소 ID 생성
            cow_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # 젖소 데이터 구성
            cow_document = {
                "id": cow_id,
                "ear_tag_number": cow_data.ear_tag_number,
                "name": cow_data.name,
                "birthdate": cow_data.birthdate,
                "sensor_number": cow_data.sensor_number,
                "health_status": cow_data.health_status.value if cow_data.health_status else None,
                "breeding_status": cow_data.breeding_status.value if cow_data.breeding_status else None,
                "breed": cow_data.breed,
                "notes": cow_data.notes,
                "is_favorite": False,  # 기본값: 즐겨찾기 아님
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            # Firestore에 젖소 정보 저장
            db.collection('cows').document(cow_id).set(cow_document)
            
            # 응답 데이터 구성
            return CowResponse(
                id=cow_id,
                ear_tag_number=cow_data.ear_tag_number,
                name=cow_data.name,
                birthdate=cow_data.birthdate,
                sensor_number=cow_data.sensor_number,
                health_status=cow_data.health_status if cow_data.health_status else None,
                breeding_status=cow_data.breeding_status if cow_data.breeding_status else None,
                breed=cow_data.breed,
                notes=cow_data.notes,
                is_favorite=False,  # 새로 등록된 젖소는 기본적으로 즐겨찾기 아님
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
                detail=f"젖소 등록 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_cows_by_farm(farm_id: str, is_active: bool = True) -> List[CowResponse]:
        """농장별 젖소 목록 조회 - 500 오류 해결"""
        try:
            cows_query = (db.collection('cows')
                         .where('farm_id', '==', farm_id)
                         .where('is_active', '==', is_active)
                         .order_by('created_at', direction='DESCENDING')
                         .get())
            
            cows = []
            for cow_doc in cows_query:
                try:
                    cow_data = cow_doc.to_dict()
                    
                    # HealthStatus와 BreedingStatus 안전하게 변환
                    health_status = None
                    if cow_data.get("health_status"):
                        try:
                            health_status = HealthStatus(cow_data["health_status"])
                        except ValueError:
                            print(f"[WARNING] 잘못된 health_status 값: {cow_data.get('health_status')} (젖소 ID: {cow_data.get('id')})")
                            # 기본값으로 설정하거나 None으로 유지
                            health_status = HealthStatus.NORMAL  # 또는 None
                    
                    breeding_status = None
                    if cow_data.get("breeding_status"):
                        try:
                            breeding_status = BreedingStatus(cow_data["breeding_status"])
                        except ValueError:
                            print(f"[WARNING] 잘못된 breeding_status 값: {cow_data.get('breeding_status')} (젖소 ID: {cow_data.get('id')})")
                            breeding_status = None
                    
                    cows.append(CowResponse(
                        id=cow_data.get("id", ""),
                        ear_tag_number=cow_data.get("ear_tag_number", ""),
                        name=cow_data.get("name", "이름 없음"),
                        birthdate=cow_data.get("birthdate"),
                        sensor_number=cow_data.get("sensor_number"),
                        health_status=health_status,
                        breeding_status=breeding_status,
                        breed=cow_data.get("breed"),
                        notes=cow_data.get("notes"),
                        is_favorite=cow_data.get("is_favorite", False),
                        farm_id=cow_data.get("farm_id", farm_id),
                        owner_id=cow_data.get("owner_id", ""),
                        created_at=cow_data.get("created_at", datetime.utcnow()),
                        updated_at=cow_data.get("updated_at", datetime.utcnow()),
                        is_active=cow_data.get("is_active", True)
                    ))
                except Exception as cow_error:
                    # 개별 젖소 처리 실패 시 로그만 남기고 계속 진행
                    print(f"[WARNING] 젖소 처리 실패 (ID: {cow_doc.id}): {str(cow_error)}")
                    continue
            
            return cows
            
        except Exception as e:
            # 전체 실패 시에도 빈 배열 반환 (500 오류 방지)
            print(f"[ERROR] 젖소 목록 조회 전체 실패 (farm_id: {farm_id}): {str(e)}")
            return []
    
    @staticmethod
    def get_cow_by_id(cow_id: str, farm_id: str) -> Optional[CowResponse]:
        """특정 젖소 정보 조회"""
        try:
            cow_doc = db.collection('cows').document(cow_id).get()
            
            if not cow_doc.exists:
                return None
            
            cow_data = cow_doc.to_dict()
            
            # 농장 ID 확인 (보안)
            if cow_data.get("farm_id") != farm_id:
                return None
            
            # HealthStatus와 BreedingStatus 안전하게 변환
            health_status = None
            if cow_data.get("health_status"):
                try:
                    health_status = HealthStatus(cow_data["health_status"])
                except ValueError:
                    print(f"[WARNING] 잘못된 health_status 값: {cow_data['health_status']} (젖소 ID: {cow_data['id']})")
                    health_status = HealthStatus.NORMAL
            
            breeding_status = None
            if cow_data.get("breeding_status"):
                try:
                    breeding_status = BreedingStatus(cow_data["breeding_status"])
                except ValueError:
                    print(f"[WARNING] 잘못된 breeding_status 값: {cow_data['breeding_status']} (젖소 ID: {cow_data['id']})")
                    breeding_status = None
            
            return CowResponse(
                id=cow_data["id"],
                ear_tag_number=cow_data["ear_tag_number"],
                name=cow_data["name"],
                birthdate=cow_data.get("birthdate"),
                sensor_number=cow_data.get("sensor_number"),
                health_status=health_status,
                breeding_status=breeding_status,
                breed=cow_data.get("breed"),
                notes=cow_data.get("notes"),
                is_favorite=cow_data.get("is_favorite", False),
                farm_id=cow_data["farm_id"],
                owner_id=cow_data["owner_id"],
                created_at=cow_data["created_at"],
                updated_at=cow_data["updated_at"],
                is_active=cow_data["is_active"]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"젖소 정보 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def update_cow(cow_id: str, cow_update: CowUpdate, user: Dict) -> CowResponse:
        """젖소 정보 업데이트"""
        try:
            farm_id = user.get("farm_id")
            
            # 기존 젖소 정보 조회
            existing_cow = CowFirebaseService.get_cow_by_id(cow_id, farm_id)
            if not existing_cow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="젖소를 찾을 수 없습니다"
                )
            
            # 업데이트할 데이터 구성
            update_data = {"updated_at": datetime.utcnow()}
            
            # 변경된 필드만 업데이트
            if cow_update.name is not None:
                update_data["name"] = cow_update.name.strip()
            
            if cow_update.sensor_number is not None:
                # 센서 번호가 제공된 경우에만 중복 확인
                if cow_update.sensor_number.strip():  # 빈 문자열이 아닌 경우
                    existing_sensor_query = (db.collection('cows')
                                           .where('farm_id', '==', farm_id)
                                           .where('sensor_number', '==', cow_update.sensor_number)
                                           .where('is_active', '==', True)
                                           .get())
                    
                    for doc in existing_sensor_query:
                        if doc.to_dict().get("id") != cow_id:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"센서 번호 '{cow_update.sensor_number}'는 이미 사용 중입니다"
                            )
                    
                    update_data["sensor_number"] = cow_update.sensor_number.strip()
                else:
                    # 빈 문자열인 경우 None으로 처리
                    update_data["sensor_number"] = None
            
            if cow_update.health_status is not None:
                update_data["health_status"] = cow_update.health_status.value
            
            if cow_update.breeding_status is not None:
                update_data["breeding_status"] = cow_update.breeding_status.value
            
            if cow_update.birthdate is not None:
                update_data["birthdate"] = cow_update.birthdate
            
            if cow_update.birthdate is not None:
                update_data["birthdate"] = cow_update.birthdate
            
            if cow_update.breed is not None:
                update_data["breed"] = cow_update.breed
            
            if cow_update.notes is not None:
                update_data["notes"] = cow_update.notes
            
            # Firestore 업데이트
            db.collection('cows').document(cow_id).update(update_data)
            
            # 업데이트된 젖소 정보 반환
            return CowFirebaseService.get_cow_by_id(cow_id, farm_id)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"젖소 정보 업데이트 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def delete_cow(cow_id: str, user: Dict) -> Dict:
        """젖소 삭제 (하드 삭제 - Firebase DB에서 완전 삭제)"""
        try:
            farm_id = user.get("farm_id")
            
            # 기존 젖소 정보 확인
            existing_cow = CowFirebaseService.get_cow_by_id(cow_id, farm_id)
            if not existing_cow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="젖소를 찾을 수 없습니다"
                )
            
            # 1. 젖소 관련 모든 기록 삭제
            # 상세 기록 삭제
            detailed_records_query = (db.collection('cow_detailed_records')
                                    .where('cow_id', '==', cow_id)
                                    .where('farm_id', '==', farm_id)
                                    .get())
            
            for record in detailed_records_query:
                record.reference.delete()
            
            # 기본 기록 삭제
            basic_records_query = (db.collection('cow_records')
                                 .where('cow_id', '==', cow_id)
                                 .where('farm_id', '==', farm_id)
                                 .get())
            
            for record in basic_records_query:
                record.reference.delete()
            
            # 2. 젖소 정보 완전 삭제
            db.collection('cows').document(cow_id).delete()
            
            return {
                "message": f"젖소 '{existing_cow.name}' (이표번호: {existing_cow.ear_tag_number})와 관련된 모든 데이터가 완전히 삭제되었습니다",
                "cow_id": cow_id,
                "deleted_records_count": len(detailed_records_query) + len(basic_records_query)
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"젖소 삭제 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def toggle_favorite(cow_id: str, user: Dict) -> Dict:
        """젖소 즐겨찾기 토글"""
        try:
            farm_id = user.get("farm_id")
            
            # 기존 젖소 정보 확인
            existing_cow = CowFirebaseService.get_cow_by_id(cow_id, farm_id)
            if not existing_cow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="젖소를 찾을 수 없습니다"
                )
            
            # 즐겨찾기 상태 토글
            new_favorite_status = not existing_cow.is_favorite
            
            # Firestore 업데이트
            db.collection('cows').document(cow_id).update({
                "is_favorite": new_favorite_status,
                "updated_at": datetime.utcnow()
            })
            
            action = "추가" if new_favorite_status else "제거"
            
            return {
                "message": f"젖소 '{existing_cow.name}'이 즐겨찾기에서 {action}되었습니다",
                "cow_id": cow_id,
                "is_favorite": new_favorite_status
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"즐겨찾기 설정 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_favorite_cows(farm_id: str) -> List[CowResponse]:
        """즐겨찾기된 젖소 목록 조회 - 500 오류 해결"""
        try:
            cows_query = (db.collection('cows')
                         .where('farm_id', '==', farm_id)
                         .where('is_favorite', '==', True)
                         .where('is_active', '==', True)
                         .order_by('updated_at', direction='DESCENDING')
                         .get())
            
            cows = []
            for cow_doc in cows_query:
                try:
                    cow_data = cow_doc.to_dict()
                    
                    # HealthStatus와 BreedingStatus 안전하게 변환
                    health_status = None
                    if cow_data.get("health_status"):
                        try:
                            health_status = HealthStatus(cow_data["health_status"])
                        except ValueError:
                            print(f"[WARNING] 잘못된 health_status 값: {cow_data.get('health_status')} (젖소 ID: {cow_data.get('id')})")
                            health_status = HealthStatus.NORMAL
                    
                    breeding_status = None
                    if cow_data.get("breeding_status"):
                        try:
                            breeding_status = BreedingStatus(cow_data["breeding_status"])
                        except ValueError:
                            print(f"[WARNING] 잘못된 breeding_status 값: {cow_data.get('breeding_status')} (젖소 ID: {cow_data.get('id')})")
                            breeding_status = None
                            
                    cows.append(CowResponse(
                        id=cow_data.get("id", ""),
                        ear_tag_number=cow_data.get("ear_tag_number", ""),
                        name=cow_data.get("name", "이름 없음"),
                        birthdate=cow_data.get("birthdate"),
                        sensor_number=cow_data.get("sensor_number"),
                        health_status=health_status,
                        breeding_status=breeding_status,
                        breed=cow_data.get("breed"),
                        notes=cow_data.get("notes"),
                        is_favorite=cow_data.get("is_favorite", False),
                        farm_id=cow_data.get("farm_id", farm_id),
                        owner_id=cow_data.get("owner_id", ""),
                        created_at=cow_data.get("created_at", datetime.utcnow()),
                        updated_at=cow_data.get("updated_at", datetime.utcnow()),
                        is_active=cow_data.get("is_active", True)
                    ))
                except Exception as cow_error:
                    # 개별 젖소 처리 실패 시 로그만 남기고 계속 진행
                    print(f"[WARNING] 즐겨찾기 젖소 처리 실패 (ID: {cow_doc.id}): {str(cow_error)}")
                    continue
            
            return cows
            
        except Exception as e:
            # 전체 실패 시에도 빈 배열 반환 (500 오류 방지)
            print(f"[ERROR] 즐겨찾기 젖소 목록 조회 전체 실패: {str(e)}")
            return []
        
    @staticmethod
    def _get_cow_info(cow_id: str, farm_id: str) -> Dict:
        """젖소 기본 정보 조회 (안전한 처리)"""
        try:
            cow_doc = db.collection('cows').document(cow_id).get()
            
            if not cow_doc.exists:
                return {
                    "name": "알 수 없음",
                    "ear_tag_number": "N/A"
                }
            
            cow_data = cow_doc.to_dict()
            
            # 농장 ID 확인 (보안)
            if cow_data.get("farm_id") != farm_id:
                return {
                    "name": "알 수 없음", 
                    "ear_tag_number": "N/A"
                }
            
            return {
                "name": cow_data.get("name", "알 수 없음"),
                "ear_tag_number": cow_data.get("ear_tag_number", "N/A")
            }
            
        except Exception as e:
            print(f"[WARNING] 젖소 정보 조회 실패 (cow_id: {cow_id}): {str(e)}")
            return {
                "name": "알 수 없음",
                "ear_tag_number": "N/A"
            }

    @staticmethod
    def _extract_key_values(record_type: str, record_data: Dict) -> Dict:
        """기록 데이터에서 주요 값들 추출 (안전한 처리)"""
        try:
            key_values = {}
            
            if record_type == "milking":
                key_values = {
                    "milk_yield": record_data.get("milk_yield", 0),
                    "fat_content": record_data.get("fat_content"),
                    "protein_content": record_data.get("protein_content")
                }
            elif record_type == "feed":
                key_values = {
                    "feed_type": record_data.get("feed_type", ""),
                    "amount": record_data.get("amount", 0),
                    "unit": record_data.get("unit", "kg")
                }
            elif record_type == "weight":
                key_values = {
                    "weight": record_data.get("weight", 0),
                    "body_condition_score": record_data.get("body_condition_score")
                }
            elif record_type == "health_check":
                key_values = {
                    "temperature": record_data.get("temperature"),
                    "pulse": record_data.get("pulse"),
                    "overall_condition": record_data.get("overall_condition", "정상")
                }
            elif record_type == "vaccination":
                key_values = {
                    "vaccine_name": record_data.get("vaccine_name", ""),
                    "next_vaccination_date": record_data.get("next_vaccination_date")
                }
            elif record_type == "treatment":
                key_values = {
                    "diagnosis": record_data.get("diagnosis", ""),
                    "medication": record_data.get("medication", ""),
                    "treatment_result": record_data.get("treatment_result", "진행중")
                }
            elif record_type in ["estrus", "insemination", "pregnancy_check", "calving"]:
                if record_type == "estrus":
                    key_values = {
                        "estrus_intensity": record_data.get("estrus_intensity", "보통"),
                        "estrus_symptoms": record_data.get("estrus_symptoms", [])
                    }
                elif record_type == "insemination":
                    key_values = {
                        "semen_info": record_data.get("semen_info", ""),
                        "technician": record_data.get("technician", "")
                    }
                elif record_type == "pregnancy_check":
                    key_values = {
                        "pregnancy_status": record_data.get("pregnancy_status", "확인중"),
                        "expected_calving_date": record_data.get("expected_calving_date")
                    }
                elif record_type == "calving":
                    key_values = {
                        "calf_gender": record_data.get("calf_gender", ""),
                        "calving_difficulty": record_data.get("calving_difficulty", "정상")
                    }
            
            return key_values
            
        except Exception as e:
            print(f"[WARNING] 키 값 추출 실패 (record_type: {record_type}): {str(e)}")
            return {}

# 젖소 상세 정보 업데이트
@staticmethod
def update_cow_details(cow_id: str, cow_detail_update: CowDetailUpdate, user: Dict) -> CowDetailResponse:
    """젖소 상세 정보 업데이트 (수정하기 화면에서 사용)"""
    try:
        farm_id = user.get("farm_id")
        
        # 기존 젖소 정보 확인
        existing_cow = CowFirebaseService.get_cow_by_id(cow_id, farm_id)
        if not existing_cow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="젖소를 찾을 수 없습니다"
            )
        
        current_time = datetime.utcnow()
        
        # 업데이트할 데이터 구성
        update_data = {
            "updated_at": current_time,
            "detail_updated_at": current_time,
            "has_detailed_info": True  # 상세 정보 입력 플래그
        }
        
        # 기본 정보 업데이트
        if cow_detail_update.name is not None:
            update_data["name"] = cow_detail_update.name
        if cow_detail_update.birthdate is not None:
            update_data["birthdate"] = cow_detail_update.birthdate
        if cow_detail_update.sensor_number is not None:
            update_data["sensor_number"] = cow_detail_update.sensor_number
        if cow_detail_update.health_status is not None:
            update_data["health_status"] = cow_detail_update.health_status.value
        if cow_detail_update.breeding_status is not None:
            update_data["breeding_status"] = cow_detail_update.breeding_status.value
        if cow_detail_update.breed is not None:
            update_data["breed"] = cow_detail_update.breed
        if cow_detail_update.notes is not None:
            update_data["notes"] = cow_detail_update.notes
        
        # 상세 정보 업데이트
        detailed_info = {}
        
        # 신체 정보
        if any([cow_detail_update.body_weight, cow_detail_update.body_height, 
                cow_detail_update.body_length, cow_detail_update.chest_girth, 
                cow_detail_update.body_condition_score]):
            detailed_info["body_info"] = {
                "weight": cow_detail_update.body_weight,
                "height": cow_detail_update.body_height,
                "body_length": cow_detail_update.body_length,
                "chest_girth": cow_detail_update.chest_girth,
                "body_condition_score": cow_detail_update.body_condition_score
            }
        
        # 생산 정보
        if any([cow_detail_update.lactation_number, cow_detail_update.milk_yield_record,
                cow_detail_update.lifetime_milk_yield, cow_detail_update.average_daily_yield]):
            detailed_info["production_info"] = {
                "lactation_number": cow_detail_update.lactation_number,
                "milk_yield_record": cow_detail_update.milk_yield_record,
                "lifetime_milk_yield": cow_detail_update.lifetime_milk_yield,
                "average_daily_yield": cow_detail_update.average_daily_yield
            }
        
        # 번식 정보
        if any([cow_detail_update.first_calving_date, cow_detail_update.last_calving_date,
                cow_detail_update.total_calves, cow_detail_update.breeding_efficiency]):
            detailed_info["breeding_info"] = {
                "first_calving_date": cow_detail_update.first_calving_date,
                "last_calving_date": cow_detail_update.last_calving_date,
                "total_calves": cow_detail_update.total_calves,
                "breeding_efficiency": cow_detail_update.breeding_efficiency
            }
        
        # 건강 정보
        if any([cow_detail_update.vaccination_status, cow_detail_update.last_health_check,
                cow_detail_update.chronic_conditions, cow_detail_update.allergy_info]):
            detailed_info["health_info"] = {
                "vaccination_status": cow_detail_update.vaccination_status,
                "last_health_check": cow_detail_update.last_health_check,
                "chronic_conditions": cow_detail_update.chronic_conditions or [],
                "allergy_info": cow_detail_update.allergy_info
            }
        
        # 관리 정보
        if any([cow_detail_update.purchase_date, cow_detail_update.purchase_price,
                cow_detail_update.current_value, cow_detail_update.insurance_policy,
                cow_detail_update.special_management]):
            detailed_info["management_info"] = {
                "purchase_date": cow_detail_update.purchase_date,
                "purchase_price": cow_detail_update.purchase_price,
                "current_value": cow_detail_update.current_value,
                "insurance_policy": cow_detail_update.insurance_policy,
                "special_management": cow_detail_update.special_management
            }
        
        # 혈통 정보
        if any([cow_detail_update.mother_id, cow_detail_update.father_info,
                cow_detail_update.genetic_info]):
            detailed_info["pedigree_info"] = {
                "mother_id": cow_detail_update.mother_id,
                "father_info": cow_detail_update.father_info,
                "genetic_info": cow_detail_update.genetic_info
            }
        
        # 사료 정보
        if any([cow_detail_update.feed_type, cow_detail_update.daily_feed_amount,
                cow_detail_update.supplement_info]):
            detailed_info["feed_info"] = {
                "feed_type": cow_detail_update.feed_type,
                "daily_feed_amount": cow_detail_update.daily_feed_amount,
                "supplement_info": cow_detail_update.supplement_info
            }
        
        # 위치 정보
        if any([cow_detail_update.barn_section, cow_detail_update.stall_number]):
            detailed_info["location_info"] = {
                "barn_section": cow_detail_update.barn_section,
                "stall_number": cow_detail_update.stall_number
            }
        
        # 행동 특성
        if any([cow_detail_update.temperament, cow_detail_update.milking_behavior,
                cow_detail_update.retirement_plan]):
            detailed_info["behavioral_info"] = {
                "temperament": cow_detail_update.temperament.value if cow_detail_update.temperament else None,
                "milking_behavior": cow_detail_update.milking_behavior.value if cow_detail_update.milking_behavior else None,
                "retirement_plan": cow_detail_update.retirement_plan
            }
        
        # 상세 정보가 있다면 업데이트
        if detailed_info:
            update_data["detailed_info"] = detailed_info
        
        # Firestore 업데이트
        db.collection('cows').document(cow_id).update(update_data)
        
        # 업데이트된 젖소 상세 정보 반환
        return CowFirebaseService.get_cow_details_by_id(cow_id, farm_id)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"젖소 상세 정보 업데이트 중 오류가 발생했습니다: {str(e)}"
        )

# 젖소 상세 정보 포함 조회
@staticmethod
def get_cow_details_by_id(cow_id: str, farm_id: str) -> Optional[CowDetailResponse]:
    """젖소 상세 정보 포함하여 조회"""
    try:
        cow_doc = db.collection('cows').document(cow_id).get()
        
        if not cow_doc.exists:
            return None
        
        cow_data = cow_doc.to_dict()
        
        # 농장 ID 확인 (보안)
        if cow_data.get("farm_id") != farm_id:
            return None
        
        # 상세 정보 추출
        detailed_info = cow_data.get("detailed_info", {})
        body_info = detailed_info.get("body_info", {})
        production_info = detailed_info.get("production_info", {})
        breeding_info = detailed_info.get("breeding_info", {})
        health_info = detailed_info.get("health_info", {})
        management_info = detailed_info.get("management_info", {})
        pedigree_info = detailed_info.get("pedigree_info", {})
        feed_info = detailed_info.get("feed_info", {})
        location_info = detailed_info.get("location_info", {})
        behavioral_info = detailed_info.get("behavioral_info", {})
        
        # HealthStatus와 BreedingStatus 안전하게 변환
        health_status = None
        if cow_data.get("health_status"):
            try:
                health_status = HealthStatus(cow_data["health_status"])
            except ValueError:
                print(f"[WARNING] 잘못된 health_status 값: {cow_data['health_status']} (젖소 ID: {cow_data['id']})")
                health_status = HealthStatus.NORMAL
        
        breeding_status = None
        if cow_data.get("breeding_status"):
            try:
                breeding_status = BreedingStatus(cow_data["breeding_status"])
            except ValueError:
                print(f"[WARNING] 잘못된 breeding_status 값: {cow_data['breeding_status']} (젖소 ID: {cow_data['id']})")
                breeding_status = None
                
        return CowDetailResponse(
            # 기본 정보
            id=cow_data["id"],
            ear_tag_number=cow_data["ear_tag_number"],
            name=cow_data["name"],
            birthdate=cow_data.get("birthdate"),
            sensor_number=cow_data.get("sensor_number"),
            health_status=health_status,
            breeding_status=breeding_status,
            breed=cow_data.get("breed"),
            notes=cow_data.get("notes"),
            is_favorite=cow_data.get("is_favorite", False),
            farm_id=cow_data["farm_id"],
            owner_id=cow_data["owner_id"],
            created_at=cow_data["created_at"],
            updated_at=cow_data["updated_at"],
            is_active=cow_data["is_active"],
            
            # 상세 정보 메타데이터
            has_detailed_info=cow_data.get("has_detailed_info", False),
            detail_updated_at=cow_data.get("detail_updated_at"),
            
            # 신체 정보
            body_weight=body_info.get("weight"),
            body_height=body_info.get("height"),
            body_length=body_info.get("body_length"),
            chest_girth=body_info.get("chest_girth"),
            body_condition_score=body_info.get("body_condition_score"),
            
            # 생산 정보
            lactation_number=production_info.get("lactation_number"),
            milk_yield_record=production_info.get("milk_yield_record"),
            lifetime_milk_yield=production_info.get("lifetime_milk_yield"),
            average_daily_yield=production_info.get("average_daily_yield"),
            
            # 번식 정보
            first_calving_date=breeding_info.get("first_calving_date"),
            last_calving_date=breeding_info.get("last_calving_date"),
            total_calves=breeding_info.get("total_calves"),
            breeding_efficiency=breeding_info.get("breeding_efficiency"),
            
            # 건강 정보
            vaccination_status=health_info.get("vaccination_status"),
            last_health_check=health_info.get("last_health_check"),
            chronic_conditions=health_info.get("chronic_conditions"),
            allergy_info=health_info.get("allergy_info"),
            
            # 관리 정보
            purchase_date=management_info.get("purchase_date"),
            purchase_price=management_info.get("purchase_price"),
            current_value=management_info.get("current_value"),
            insurance_policy=management_info.get("insurance_policy"),
            special_management=management_info.get("special_management"),
            
            # 혈통 정보
            mother_id=pedigree_info.get("mother_id"),
            father_info=pedigree_info.get("father_info"),
            genetic_info=pedigree_info.get("genetic_info"),
            
            # 사료 정보
            feed_type=feed_info.get("feed_type"),
            daily_feed_amount=feed_info.get("daily_feed_amount"),
            supplement_info=feed_info.get("supplement_info"),
            
            # 위치 정보
            barn_section=location_info.get("barn_section"),
            stall_number=location_info.get("stall_number"),
            
            # 행동 특성
            temperament=Temperament(behavioral_info["temperament"]) if behavioral_info.get("temperament") else None,
            milking_behavior=MilkingBehavior(behavioral_info["milking_behavior"]) if behavioral_info.get("milking_behavior") else None,
            retirement_plan=behavioral_info.get("retirement_plan")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"젖소 상세 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )

# 젖소 상세 정보 여부 확인
@staticmethod
def check_has_detailed_info(cow_id: str, farm_id: str) -> bool:
    """젖소가 상세 정보를 가지고 있는지 확인"""
    try:
        cow_doc = db.collection('cows').document(cow_id).get()
        
        if not cow_doc.exists:
            return False
        
        cow_data = cow_doc.to_dict()
        
        # 농장 ID 확인
        if cow_data.get("farm_id") != farm_id:
            return False
        
        return cow_data.get("has_detailed_info", False)
        
    except Exception as e:
        return False