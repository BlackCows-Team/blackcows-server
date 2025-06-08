from datetime import datetime
from typing import List, Dict, Optional
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
from schemas.cow import CowCreate, CowResponse, CowUpdate, HealthStatus, BreedingStatus
import uuid

# Firestore 클라이언트
db = get_firestore_client()

class CowFirebaseService:
    
    @staticmethod
    def create_cow(cow_data: CowCreate, user: Dict) -> CowResponse:
        """새로운 젖소 등록"""
        try:
            # 동일한 농장 내에서 이표번호 중복 확인
            farm_id = user.get("farm_id")
            existing_cow_query = db.collection('cows')\
                .where('farm_id', '==', farm_id)\
                .where('ear_tag_number', '==', cow_data.ear_tag_number)\
                .where('is_active', '==', True)\
                .get()
            
            if existing_cow_query:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"이표번호 '{cow_data.ear_tag_number}'는 이미 등록되어 있습니다"
                )
            
            # 센서 번호가 제공된 경우에만 중복 확인
            if cow_data.sensor_number:
                existing_sensor_query = db.collection('cows')\
                    .where('farm_id', '==', farm_id)\
                    .where('sensor_number', '==', cow_data.sensor_number)\
                    .where('is_active', '==', True)\
                    .get()
                
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
        """농장별 젖소 목록 조회"""
        try:
            cows_query = db.collection('cows')\
                .where('farm_id', '==', farm_id)\
                .where('is_active', '==', is_active)\
                .order_by('created_at', direction='desc')\
                .get()
            
            cows = []
            for cow_doc in cows_query:
                cow_data = cow_doc.to_dict()
                cows.append(CowResponse(
                    id=cow_data["id"],
                    ear_tag_number=cow_data["ear_tag_number"],
                    name=cow_data["name"],
                    birthdate=cow_data.get("birthdate"),
                    sensor_number=cow_data.get("sensor_number"),
                    health_status=HealthStatus(cow_data["health_status"]) if cow_data.get("health_status") else None,
                    breeding_status=BreedingStatus(cow_data["breeding_status"]) if cow_data.get("breeding_status") else None,
                    breed=cow_data.get("breed"),
                    notes=cow_data.get("notes"),
                    is_favorite=cow_data.get("is_favorite", False),
                    farm_id=cow_data["farm_id"],
                    owner_id=cow_data["owner_id"],
                    created_at=cow_data["created_at"],
                    updated_at=cow_data["updated_at"],
                    is_active=cow_data["is_active"]
                ))
            
            return cows
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"젖소 목록 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
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
            
            return CowResponse(
                id=cow_data["id"],
                ear_tag_number=cow_data["ear_tag_number"],
                name=cow_data["name"],
                birthdate=cow_data.get("birthdate"),
                sensor_number=cow_data.get("sensor_number"),
                health_status=HealthStatus(cow_data["health_status"]) if cow_data.get("health_status") else None,
                breeding_status=BreedingStatus(cow_data["breeding_status"]) if cow_data.get("breeding_status") else None,
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
                    existing_sensor_query = db.collection('cows')\
                        .where('farm_id', '==', farm_id)\
                        .where('sensor_number', '==', cow_update.sensor_number)\
                        .where('is_active', '==', True)\
                        .get()
                    
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
        """젖소 삭제 (소프트 삭제)"""
        try:
            farm_id = user.get("farm_id")
            
            # 기존 젖소 정보 확인
            existing_cow = CowFirebaseService.get_cow_by_id(cow_id, farm_id)
            if not existing_cow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="젖소를 찾을 수 없습니다"
                )
            
            # 소프트 삭제 (is_active를 False로 변경)
            db.collection('cows').document(cow_id).update({
                "is_active": False,
                "updated_at": datetime.utcnow(),
                "deleted_at": datetime.utcnow()
            })
            
            return {
                "message": f"젖소 '{existing_cow.name}' (이표번호: {existing_cow.ear_tag_number})가 삭제되었습니다",
                "cow_id": cow_id
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
        """즐겨찾기된 젖소 목록 조회"""
        try:
            cows_query = db.collection('cows')\
                .where('farm_id', '==', farm_id)\
                .where('is_favorite', '==', True)\
                .where('is_active', '==', True)\
                .order_by('updated_at', direction='desc')\
                .get()
            
            cows = []
            for cow_doc in cows_query:
                cow_data = cow_doc.to_dict()
                cows.append(CowResponse(
                    id=cow_data["id"],
                    ear_tag_number=cow_data["ear_tag_number"],
                    name=cow_data["name"],
                    birthdate=cow_data.get("birthdate"),
                    sensor_number=cow_data.get("sensor_number"),
                    health_status=HealthStatus(cow_data["health_status"]) if cow_data.get("health_status") else None,
                    breeding_status=BreedingStatus(cow_data["breeding_status"]) if cow_data.get("breeding_status") else None,
                    breed=cow_data.get("breed"),
                    notes=cow_data.get("notes"),
                    is_favorite=cow_data.get("is_favorite", False),
                    farm_id=cow_data["farm_id"],
                    owner_id=cow_data["owner_id"],
                    created_at=cow_data["created_at"],
                    updated_at=cow_data["updated_at"],
                    is_active=cow_data["is_active"]
                ))
            
            return cows
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"즐겨찾기 젖소 목록 조회 중 오류가 발생했습니다: {str(e)}"
            )