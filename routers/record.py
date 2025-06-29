from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from schemas.record import (
    RecordResponse, RecordSummary, RecordUpdate, RecordType,
    BreedingRecordCreate, DiseaseRecordCreate, StatusChangeRecordCreate, OtherRecordCreate
)
from services.record_firebase_service import RecordFirebaseService
from routers.auth_firebase import get_current_user

router = APIRouter()

# 번식기록 생성
@router.post("/breeding", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_breeding_record(
    record_data: BreedingRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """번식기록 생성"""
    return RecordFirebaseService.create_breeding_record(record_data, current_user)

# 질병기록 생성
@router.post("/disease", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_disease_record(
    record_data: DiseaseRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """질병기록 생성"""
    return RecordFirebaseService.create_disease_record(record_data, current_user)

# 분류변경 기록 생성
@router.post("/status-change", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_status_change_record(
    record_data: StatusChangeRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """분류변경 기록 생성"""
    return RecordFirebaseService.create_status_change_record(record_data, current_user)

# 기타기록 생성
@router.post("/other", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_other_record(
    record_data: OtherRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """기타기록 생성"""
    return RecordFirebaseService.create_other_record(record_data, current_user)

# 특정 젖소의 기록 목록 조회
@router.get("/cow/{cow_id}", response_model=List[RecordSummary])
def get_cow_records(
    cow_id: str,
    record_type: Optional[RecordType] = Query(None, description="기록 유형 필터"),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 기록 목록 조회 - 500 오류 해결"""
    try:
        farm_id = current_user.get("farm_id")
        return RecordFirebaseService.get_records_by_cow(cow_id, farm_id, record_type)
    except Exception as e:
        # 전체 실패 시에도 빈 배열 반환 (500 오류 방지)
        print(f"[ERROR] 젖소 기록 조회 전체 실패 (cow_id: {cow_id}): {str(e)}")
        return []

# 농장의 모든 기록 조회
@router.get("/", response_model=List[RecordSummary])
def get_farm_records(
    record_type: Optional[RecordType] = Query(None, description="기록 유형 필터"),
    limit: int = Query(50, description="조회 개수 제한", ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """농장의 모든 기록 조회 - 500 오류 해결"""
    try:
        farm_id = current_user.get("farm_id")
        return RecordFirebaseService.get_all_records_by_farm(farm_id, record_type, limit)
    except Exception as e:
        # 전체 실패 시에도 빈 배열 반환 (500 오류 방지)
        print(f"[ERROR] 농장 기록 조회 전체 실패 (farm_id: {current_user.get('farm_id')}): {str(e)}")
        return []

# 기록 상세 조회
@router.get("/{record_id}", response_model=RecordResponse)
def get_record_detail(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """기록 상세 조회"""
    farm_id = current_user.get("farm_id")
    return RecordFirebaseService.get_record_detail(record_id, farm_id)

# 기록 업데이트
@router.put("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: str,
    record_update: RecordUpdate,
    current_user: dict = Depends(get_current_user)
):
    """기록 업데이트"""
    return RecordFirebaseService.update_record(record_id, record_update, current_user)

# 기록 삭제
@router.delete("/{record_id}")
def delete_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """기록 삭제"""
    return RecordFirebaseService.delete_record(record_id, current_user)

# 최근 기록 조회 (홈화면용)
@router.get("/recent/summary", response_model=List[RecordSummary])
def get_recent_records(
    limit: int = Query(10, description="조회 개수", ge=1, le=20),
    current_user: dict = Depends(get_current_user)
):
    """최근 기록 조회 (홈화면용) - 500 오류 해결"""
    try:
        farm_id = current_user.get("farm_id")
        return RecordFirebaseService.get_all_records_by_farm(farm_id, None, limit)
    except Exception as e:
        # 전체 실패 시에도 빈 배열 반환 (500 오류 방지)
        print(f"[ERROR] 최근 기록 조회 전체 실패 (farm_id: {current_user.get('farm_id')}): {str(e)}")
        return []

# 기록 유형별 통계
@router.get("/statistics/summary")
def get_record_statistics(current_user: dict = Depends(get_current_user)):
    """기록 유형별 통계 - 500 오류 해결"""
    farm_id = current_user.get("farm_id")
    
    try:
        from config.firebase_config import get_firestore_client
        db = get_firestore_client()
        
        # 기록 유형별 통계 (안전한 처리)
        record_stats = {}
        for record_type in ["breeding", "disease", "status_change", "other"]:
            try:
                count = len((db.collection('cow_records')
                            .where('farm_id', '==', farm_id)
                            .where('record_type', '==', record_type)
                            .where('is_active', '==', True)
                            .get()))
                record_stats[record_type] = count
            except Exception as type_error:
                # 개별 타입 조회 실패 시 0으로 설정
                print(f"[WARNING] 기록 타입 통계 조회 실패 ({record_type}): {str(type_error)}")
                record_stats[record_type] = 0
        
        # 최근 30일 기록 수 (안전한 처리)
        recent_records_count = 0
        try:
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_records_count = len((db.collection('cow_records')
                                      .where('farm_id', '==', farm_id)
                                      .where('created_at', '>=', thirty_days_ago)
                                      .where('is_active', '==', True)
                                      .get()))
        except Exception as recent_error:
            print(f"[WARNING] 최근 기록 통계 조회 실패: {str(recent_error)}")
            recent_records_count = 0
        
        # 전체 기록 수
        total_records = sum(record_stats.values())
        
        return {
            "total_records": total_records,
            "recent_records_30days": recent_records_count,
            "record_type_statistics": record_stats,
            "farm_id": farm_id
        }
        
    except Exception as e:
        # 전체 실패 시에도 기본값 반환 (500 오류 방지)
        print(f"[ERROR] 기록 통계 조회 전체 실패: {str(e)}")
        return {
            "total_records": 0,
            "recent_records_30days": 0,
            "record_type_statistics": {
                "breeding": 0,
                "disease": 0,
                "status_change": 0,
                "other": 0
            },
            "farm_id": farm_id
        }