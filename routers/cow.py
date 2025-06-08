from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.cow import CowCreate, CowResponse, CowUpdate
from services.cow_firebase_service import CowFirebaseService
from routers.auth_firebase import get_current_user

router = APIRouter()

@router.post("/", response_model=CowResponse, status_code=status.HTTP_201_CREATED)
def register_cow(
    cow_data: CowCreate,
    current_user: dict = Depends(get_current_user)
):
    """새로운 젖소 등록"""
    return CowFirebaseService.create_cow(cow_data, current_user)

@router.get("/", response_model=List[CowResponse])
def list_cows(current_user: dict = Depends(get_current_user)):
    """현재 사용자의 농장에 등록된 젖소 목록 조회"""
    farm_id = current_user.get("farm_id")
    return CowFirebaseService.get_cows_by_farm(farm_id)

@router.get("/{cow_id}", response_model=CowResponse)
def get_cow_detail(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 상세 정보 조회"""
    farm_id = current_user.get("farm_id")
    cow = CowFirebaseService.get_cow_by_id(cow_id, farm_id)
    
    if not cow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="젖소를 찾을 수 없습니다"
        )
    
    return cow

@router.put("/{cow_id}", response_model=CowResponse)
def update_cow_info(
    cow_id: str,
    cow_update: CowUpdate,
    current_user: dict = Depends(get_current_user)
):
    """젖소 정보 업데이트"""
    return CowFirebaseService.update_cow(cow_id, cow_update, current_user)

@router.delete("/{cow_id}")
def delete_cow(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """젖소 삭제"""
    return CowFirebaseService.delete_cow(cow_id, current_user)

@router.get("/search/by-tag/{ear_tag_number}", response_model=CowResponse)
def get_cow_by_tag_number(
    ear_tag_number: str,
    current_user: dict = Depends(get_current_user)
):
    """이표번호로 젖소 검색"""
    farm_id = current_user.get("farm_id")
    
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        
        # 이표번호로 젖소 검색
        cows_query = db.collection('cows')\
            .where('farm_id', '==', farm_id)\
            .where('ear_tag_number', '==', ear_tag_number)\
            .where('is_active', '==', True)\
            .limit(1)\
            .get()
        
        if not cows_query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"이표번호 '{ear_tag_number}'인 젖소를 찾을 수 없습니다"
            )
        
        cow_data = cows_query[0].to_dict()
        from schemas.cow import HealthStatus, BreedingStatus
        
        return CowResponse(
            id=cow_data["id"],
            ear_tag_number=cow_data["ear_tag_number"],
            name=cow_data["name"],
            sensor_number=cow_data.get("sensor_number"),
            health_status=HealthStatus(cow_data["health_status"]) if cow_data.get("health_status") else None,
            breeding_status=BreedingStatus(cow_data["breeding_status"]) if cow_data.get("breeding_status") else None,
            birthdate=cow_data.get("birthdate"),
            breed=cow_data.get("breed"),
            notes=cow_data.get("notes"),
            farm_id=cow_data["farm_id"],
            owner_id=cow_data["owner_id"],
            created_at=cow_data["created_at"],
            updated_at=cow_data["updated_at"],
            is_active=cow_data["is_active"]
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"젖소 검색 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/statistics/summary")
def get_farm_statistics(current_user: dict = Depends(get_current_user)):
    """농장 젖소 통계 정보"""
    farm_id = current_user.get("farm_id")
    
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        
        # 전체 젖소 수
        total_cows = len(db.collection('cows')\
                         .where('farm_id', '==', farm_id)\
                         .where('is_active', '==', True)\
                         .get())
        
        # 건강상태별 통계
        health_stats = {}
        for status in ["excellent", "good", "average", "poor", "sick"]:
            count = len(db.collection('cows')\
                       .where('farm_id', '==', farm_id)\
                       .where('health_status', '==', status)\
                       .where('is_active', '==', True)\
                       .get())
            health_stats[status] = count
        
        # 번식상태별 통계
        breeding_stats = {}
        for status in ["calf", "heifer", "pregnant", "lactating", "dry", "breeding"]:
            count = len(db.collection('cows')\
                       .where('farm_id', '==', farm_id)\
                       .where('breeding_status', '==', status)\
                       .where('is_active', '==', True)\
                       .get())
            breeding_stats[status] = count
        
        return {
            "total_cows": total_cows,
            "health_statistics": health_stats,
            "breeding_statistics": breeding_stats,
            "farm_id": farm_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/{cow_id}/favorite")
def toggle_cow_favorite(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """젖소 즐겨찾기 토글"""
    return CowFirebaseService.toggle_favorite(cow_id, current_user)

@router.get("/favorites/list", response_model=List[CowResponse])
def get_favorite_cows(current_user: dict = Depends(get_current_user)):
    """즐겨찾기된 젖소 목록 조회"""
    farm_id = current_user.get("farm_id")
    return CowFirebaseService.get_favorite_cows(farm_id)