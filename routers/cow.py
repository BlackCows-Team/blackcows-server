from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.cow import CowCreate, CowResponse, CowUpdate
from services.cow_firebase_service import CowFirebaseService
from routers.auth_firebase import get_current_user
from schemas.cow import CowDetailUpdate, CowDetailResponse

router = APIRouter()

@router.post("/", 
            response_model=CowResponse, 
            status_code=status.HTTP_201_CREATED,
            summary="젖소 등록",
            description="새로운 젖소를 농장에 등록합니다.")
def register_cow(
    cow_data: CowCreate,
    current_user: dict = Depends(get_current_user)
):
    """새로운 젖소 등록"""
    return CowFirebaseService.create_cow(cow_data, current_user)

@router.get("/", 
           response_model=List[CowResponse],
           summary="젖소 목록 조회",
           description="현재 사용자의 농장에 등록된 모든 젖소 목록을 조회합니다.")
def list_cows(current_user: dict = Depends(get_current_user)):
    """현재 사용자의 농장에 등록된 젖소 목록 조회"""
    farm_id = current_user.get("farm_id")
    return CowFirebaseService.get_cows_by_farm(farm_id)

@router.patch("/{cow_id}/favorite",
              summary="즐겨찾기 토글",
              description="특정 젖소의 즐겨찾기 상태를 토글합니다.")
def toggle_cow_favorite(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """젖소 즐겨찾기 토글"""
    return CowFirebaseService.toggle_favorite(cow_id, current_user)

@router.get("/{cow_id}", 
           response_model=CowResponse,
           summary="젖소 상세 조회",
           description="특정 젖소의 상세 정보를 조회합니다.")
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

@router.put("/{cow_id}", 
           response_model=CowResponse,
           summary="젖소 정보 수정",
           description="특정 젖소의 기본 정보를 수정합니다.")
def update_cow_info(
    cow_id: str,
    cow_update: CowUpdate,
    current_user: dict = Depends(get_current_user)
):
    """젖소 정보 업데이트"""
    return CowFirebaseService.update_cow(cow_id, cow_update, current_user)

@router.delete("/{cow_id}",
              summary="젖소 삭제",
              description="특정 젖소를 삭제합니다.")
def delete_cow(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """젖소 삭제"""
    return CowFirebaseService.delete_cow(cow_id, current_user)

@router.get("/search/by-tag/{ear_tag_number}", 
           response_model=CowResponse,
           summary="이표번호로 젖소 검색",
           description="이표번호를 이용하여 특정 젖소를 검색합니다.")
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
            .where(filter=('farm_id', '==', farm_id))\
            .where(filter=('ear_tag_number', '==', ear_tag_number))\
            .where(filter=('is_active', '==', True))\
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

@router.get("/statistics/summary",
           summary="농장 통계 조회",
           description="농장의 젖소 통계 정보를 조회합니다 (전체 수, 건강상태별, 번식상태별 통계).")
def get_farm_statistics(current_user: dict = Depends(get_current_user)):
    """농장 젖소 통계 정보"""
    farm_id = current_user.get("farm_id")
    
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        
        # 전체 젖소 수
        total_cows = len(db.collection('cows')\
                         .where(filter=('farm_id', '==', farm_id))\
                         .where(filter=('is_active', '==', True))\
                         .get())
        
        # 건강상태별 통계
        health_stats = {}
        for status in ["normal", "warning", "danger"]:
            count = len(db.collection('cows')\
                       .where(filter=('farm_id', '==', farm_id))\
                       .where(filter=('health_status', '==', status))\
                       .where(filter=('is_active', '==', True))\
                       .get())
            health_stats[status] = count
        
        # 번식상태별 통계
        breeding_stats = {}
        for status in ["calf", "heifer", "pregnant", "lactating", "dry", "breeding"]:
            count = len(db.collection('cows')\
                       .where(filter=('farm_id', '==', farm_id))\
                       .where(filter=('breeding_status', '==', status))\
                       .where(filter=('is_active', '==', True))\
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

@router.get("/favorites/list", 
           response_model=List[CowResponse],
           summary="즐겨찾기 젖소 목록",
           description="즐겨찾기로 등록된 젖소들의 목록을 조회합니다.")
def get_favorite_cows(current_user: dict = Depends(get_current_user)):
    """즐겨찾기된 젖소 목록 조회"""
    farm_id = current_user.get("farm_id")
    return CowFirebaseService.get_favorite_cows(farm_id)

# 젖소 상세 정보 업데이트 (수정하기에서 사용)
@router.put("/{cow_id}/details", 
           response_model=CowDetailResponse,
           summary="젖소 상세 정보 수정",
           description="젖소의 상세 정보를 수정합니다 (수정하기 화면에서 사용).")
def update_cow_details(
    cow_id: str,
    cow_detail_update: CowDetailUpdate,
    current_user: dict = Depends(get_current_user)
):
    """젖소 상세 정보 업데이트 (수정하기 화면에서 사용)"""
    return CowFirebaseService.update_cow_details(cow_id, cow_detail_update, current_user)

# 젖소 상세 정보 조회
@router.get("/{cow_id}/details", 
           response_model=CowDetailResponse,
           summary="젖소 상세 정보 조회",
           description="젖소의 상세 정보를 포함하여 조회합니다.")
def get_cow_details(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """젖소 상세 정보 포함 조회"""
    farm_id = current_user.get("farm_id")
    cow = CowFirebaseService.get_cow_details_by_id(cow_id, farm_id)
    
    if not cow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="젖소를 찾을 수 없습니다"
        )
    
    return cow

# 젖소 상세 정보 여부 확인
@router.get("/{cow_id}/has-details",
           summary="상세 정보 보유 확인",
           description="젖소가 상세 정보를 가지고 있는지 확인합니다.")
def check_cow_has_details(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """젖소가 상세 정보를 가지고 있는지 확인"""
    farm_id = current_user.get("farm_id")
    has_details = CowFirebaseService.check_has_detailed_info(cow_id, farm_id)
    
    return {
        "cow_id": cow_id,
        "has_detailed_info": has_details,
        "message": "상세 정보가 있습니다" if has_details else "상세 정보가 없습니다"
    }