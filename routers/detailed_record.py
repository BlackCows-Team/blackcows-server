# routers/detailed_record.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from schemas.detailed_record import *
from services.detailed_record_service import DetailedRecordService
from routers.auth_firebase import get_current_user

router = APIRouter()

# ===== 착유 기록 =====
@router.post("/milking", 
             response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED,
             summary="착유 기록 생성",
             description="""
             착유 기록을 생성합니다.
             
             **필수 필드:**
             - cow_id: 젖소 ID
             - record_date: 착유 날짜 (YYYY-MM-DD 형식)
             - milk_yield: 착유량 (리터 단위, 0보다 큰 값)
             
             **선택적 필드:**
             - milking_start_time: 착유 시작 시간
             - milking_end_time: 착유 종료 시간
             - milking_session: 착유 횟수 (1회차, 2회차 등)
             - fat_percentage: 유지방 비율
             - protein_percentage: 유단백 비율
             - somatic_cell_count: 체세포수
             - temperature: 온도
             - conductivity: 전도율
             - 기타 모든 측정 필드들...
             """,
             responses={
                 201: {"description": "착유 기록 생성 성공"},
                 400: {"description": "잘못된 요청 (필수 필드 누락 또는 유효성 검사 실패)"},
                 404: {"description": "젖소를 찾을 수 없음"},
                 500: {"description": "서버 내부 오류"}
             })


def create_milking_record(
    record_data: MilkingRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    착유 기록 생성
    
    - **필수**: 착유 날짜, 착유량
    - **선택**: 나머지 모든 필드
    """
    try:
        return DetailedRecordService.create_milking_record(record_data, current_user)
    except ValueError as e:
        # Pydantic 유효성 검사 오류
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"입력 데이터 오류: {str(e)}"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"착유 기록 생성 중 예상치 못한 오류가 발생했습니다: {str(e)}"
        )
# 착유 기록 조회 (젖소별)
@router.get("/cow/{cow_id}/milking", 
           response_model=List[DetailedRecordSummary],
           summary="젖소별 착유 기록 조회",
           description="특정 젖소의 착유 기록만 필터링하여 조회")
def get_cow_milking_records(
    cow_id: str,
    limit: int = Query(50, description="조회할 기록 수 제한", ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 착유 기록 목록 조회"""
    farm_id = current_user.get("farm_id")
    return DetailedRecordService.get_detailed_records_by_cow(
        cow_id, 
        farm_id, 
        DetailedRecordType.MILKING
    )

# 최근 착유 기록 조회 (농장 전체)
@router.get("/milking/recent", 
           response_model=List[DetailedRecordSummary],
           summary="최근 착유 기록 조회",
           description="농장 전체의 최근 착유 기록을 조회")
def get_recent_milking_records(
    limit: int = Query(20, description="조회할 기록 수", ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """농장 전체의 최근 착유 기록 조회"""
    try:
        from config.firebase_config import get_firestore_client
        
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 최근 착유 기록만 조회
        records_query = db.collection('cow_detailed_records')\
            .where('farm_id', '==', farm_id)\
            .where('record_type', '==', DetailedRecordType.MILKING.value)\
            .where('is_active', '==', True)\
            .order_by('record_date', direction='DESCENDING')\
            .order_by('created_at', direction='DESCENDING')\
            .limit(limit)\
            .get()
        
        records = []
        for record_doc in records_query:
            record_data = record_doc.to_dict()
            
            # 젖소 정보 조회
            try:
                cow_info = DetailedRecordService._get_cow_info(record_data["cow_id"], farm_id)
                
                # 착유량 정보 추출
                key_values = {}
                if record_data.get("record_data", {}).get("milk_yield"):
                    key_values["milk_yield"] = f"{record_data['record_data']['milk_yield']}L"
                if record_data.get("record_data", {}).get("milking_session"):
                    key_values["session"] = f"{record_data['record_data']['milking_session']}회차"
                if record_data.get("record_data", {}).get("fat_percentage"):
                    key_values["fat"] = f"{record_data['record_data']['fat_percentage']}%"
                
                records.append(DetailedRecordSummary(
                    id=record_data["id"],
                    cow_id=record_data["cow_id"],
                    cow_name=cow_info["name"],
                    cow_ear_tag_number=cow_info["ear_tag_number"],
                    record_type=DetailedRecordType.MILKING,
                    record_date=record_data["record_date"],
                    title=record_data["title"],
                    key_values=key_values,
                    created_at=record_data["created_at"]
                ))
            except:
                # 젖소가 삭제된 경우 등 예외 처리
                continue
        
        return records
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"최근 착유 기록 조회 중 오류가 발생했습니다: {str(e)}"
        )
    
# ===== 발정 기록 =====
@router.post("/estrus", response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED)
def create_estrus_record(
    record_data: EstrusRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """발정 기록 생성"""
    return DetailedRecordService.create_estrus_record(record_data, current_user)

# ===== 인공수정 기록 =====
@router.post("/insemination", response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED)
def create_insemination_record(
    record_data: InseminationRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """인공수정 기록 생성"""
    return DetailedRecordService.create_insemination_record(record_data, current_user)

# ===== 임신감정 기록 =====
@router.post("/pregnancy-check", response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED)
def create_pregnancy_check_record(
    record_data: PregnancyCheckRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """임신감정 기록 생성"""
    return DetailedRecordService.create_pregnancy_check_record(record_data, current_user)

# ===== 분만 기록 =====
@router.post("/calving", response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED)
def create_calving_record(
    record_data: CalvingRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """분만 기록 생성"""
    return DetailedRecordService.create_calving_record(record_data, current_user)

# ===== 사료급여 기록 =====
@router.post("/feed", response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED)
def create_feed_record(
    record_data: FeedRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """사료급여 기록 생성"""
    return DetailedRecordService.create_feed_record(record_data, current_user)

# ===== 건강검진 기록 =====
@router.post("/health-check", response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED)
def create_health_check_record(
    record_data: HealthCheckRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """건강검진 기록 생성"""
    return DetailedRecordService.create_health_check_record(record_data, current_user)

# ===== 백신접종 기록 =====
@router.post("/vaccination", response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED)
def create_vaccination_record(
    record_data: VaccinationRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """백신접종 기록 생성"""
    return DetailedRecordService.create_vaccination_record(record_data, current_user)

# ===== 체중측정 기록 =====
@router.post("/weight", response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED)
def create_weight_record(
    record_data: WeightRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """체중측정 기록 생성"""
    return DetailedRecordService.create_weight_record(record_data, current_user)

# ===== 치료 기록 =====
@router.post("/treatment", response_model=DetailedRecordResponse, status_code=status.HTTP_201_CREATED)
def create_treatment_record(
    record_data: TreatmentRecordCreate,
    current_user: dict = Depends(get_current_user)
):
    """치료 기록 생성"""
    return DetailedRecordService.create_treatment_record(record_data, current_user)

# ===== 기록 조회 API =====
@router.get("/cow/{cow_id}", response_model=List[DetailedRecordSummary])
def get_cow_detailed_records(
    cow_id: str,
    record_type: Optional[DetailedRecordType] = Query(None, description="기록 유형 필터"),
    current_user: dict = Depends(get_current_user)
):
    """특정 젖소의 상세 기록 목록 조회"""
    farm_id = current_user.get("farm_id")
    return DetailedRecordService.get_detailed_records_by_cow(cow_id, farm_id, record_type)

@router.get("/{record_id}", response_model=DetailedRecordResponse)
def get_detailed_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """상세 기록 단건 조회"""
    farm_id = current_user.get("farm_id")
    return DetailedRecordService.get_detailed_record_by_id(record_id, farm_id)

@router.delete("/{record_id}")
def delete_detailed_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """상세 기록 삭제"""
    return DetailedRecordService.delete_detailed_record(record_id, current_user)

# ===== 통계 및 분석 API =====
@router.get("/cow/{cow_id}/milking/statistics")
def get_milking_statistics(
    cow_id: str,
    days: int = Query(30, description="조회 기간(일)", ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """착유 통계 조회"""
    try:
        from config.firebase_config import get_firestore_client
        from datetime import datetime, timedelta
        
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 착유 기록 조회
        milking_records = db.collection('cow_detailed_records')\
            .where('cow_id', '==', cow_id)\
            .where('farm_id', '==', farm_id)\
            .where('record_type', '==', DetailedRecordType.MILKING.value)\
            .where('is_active', '==', True)\
            .where('record_date', '>=', start_date.strftime('%Y-%m-%d'))\
            .where('record_date', '<=', end_date.strftime('%Y-%m-%d'))\
            .get()
        
        total_yield = 0
        total_sessions = 0
        avg_fat = 0
        avg_protein = 0
        fat_count = 0
        protein_count = 0
        daily_yields = {}
        
        for record in milking_records:
            data = record.to_dict()
            record_data = data.get('record_data', {})
            record_date = data.get('record_date')
            
            # 착유량 누적
            if record_data.get('milk_yield'):
                yield_amount = float(record_data['milk_yield'])
                total_yield += yield_amount
                
                # 일별 착유량 누적
                if record_date in daily_yields:
                    daily_yields[record_date] += yield_amount
                else:
                    daily_yields[record_date] = yield_amount
            
            # 착유 횟수 누적
            if record_data.get('milking_session'):
                total_sessions += 1
            
            # 유지방 평균 계산
            if record_data.get('fat_percentage'):
                avg_fat += float(record_data['fat_percentage'])
                fat_count += 1
            
            # 유단백 평균 계산
            if record_data.get('protein_percentage'):
                avg_protein += float(record_data['protein_percentage'])
                protein_count += 1
        
        # 평균 계산
        avg_daily_yield = total_yield / days if days > 0 else 0
        avg_fat_percentage = avg_fat / fat_count if fat_count > 0 else 0
        avg_protein_percentage = avg_protein / protein_count if protein_count > 0 else 0
        
        return {
            "cow_id": cow_id,
            "period_days": days,
            "total_yield": round(total_yield, 2),
            "average_daily_yield": round(avg_daily_yield, 2),
            "total_milking_sessions": total_sessions,
            "average_fat_percentage": round(avg_fat_percentage, 2),
            "average_protein_percentage": round(avg_protein_percentage, 2),
            "daily_yields": daily_yields
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"착유 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/cow/{cow_id}/weight/trend")
def get_weight_trend(
    cow_id: str,
    months: int = Query(6, description="조회 기간(월)", ge=1, le=24),
    current_user: dict = Depends(get_current_user)
):
    """체중 변화 추이 조회"""
    try:
        from config.firebase_config import get_firestore_client
        from datetime import datetime, timedelta
        
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # 체중 기록 조회
        weight_records = db.collection('cow_detailed_records')\
            .where('cow_id', '==', cow_id)\
            .where('farm_id', '==', farm_id)\
            .where('record_type', '==', DetailedRecordType.WEIGHT.value)\
            .where('is_active', '==', True)\
            .where('record_date', '>=', start_date.strftime('%Y-%m-%d'))\
            .order_by('record_date')\
            .get()
        
        weight_data = []
        for record in weight_records:
            data = record.to_dict()
            record_data = data.get('record_data', {})
            
            if record_data.get('weight'):
                weight_data.append({
                    "date": data.get('record_date'),
                    "weight": float(record_data['weight']),
                    "body_condition_score": record_data.get('body_condition_score'),
                    "measurement_method": record_data.get('measurement_method')
                })
        
        # 증체율 계산
        growth_rate = 0
        if len(weight_data) >= 2:
            first_weight = weight_data[0]['weight']
            last_weight = weight_data[-1]['weight']
            first_date = datetime.strptime(weight_data[0]['date'], '%Y-%m-%d')
            last_date = datetime.strptime(weight_data[-1]['date'], '%Y-%m-%d')
            days_diff = (last_date - first_date).days
            
            if days_diff > 0:
                growth_rate = (last_weight - first_weight) / days_diff
        
        return {
            "cow_id": cow_id,
            "period_months": months,
            "weight_records": weight_data,
            "total_records": len(weight_data),
            "average_growth_rate": round(growth_rate, 3),
            "current_weight": weight_data[-1]['weight'] if weight_data else None,
            "weight_change": round(weight_data[-1]['weight'] - weight_data[0]['weight'], 2) if len(weight_data) >= 2 else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"체중 추이 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/cow/{cow_id}/reproduction/timeline")
def get_reproduction_timeline(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """번식 타임라인 조회"""
    try:
        from config.firebase_config import get_firestore_client
        
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 번식 관련 기록들 조회
        reproduction_types = [
            DetailedRecordType.ESTRUS.value,
            DetailedRecordType.INSEMINATION.value,
            DetailedRecordType.PREGNANCY_CHECK.value,
            DetailedRecordType.CALVING.value
        ]
        
        timeline_events = []
        
        for record_type in reproduction_types:
            records = db.collection('cow_detailed_records')\
                .where('cow_id', '==', cow_id)\
                .where('farm_id', '==', farm_id)\
                .where('record_type', '==', record_type)\
                .where('is_active', '==', True)\
                .order_by('record_date', direction='DESCENDING')\
                .get()
            
            for record in records:
                data = record.to_dict()
                record_data = data.get('record_data', {})
                
                event = {
                    "id": data.get('id'),
                    "date": data.get('record_date'),
                    "type": record_type,
                    "title": data.get('title'),
                    "key_info": {}
                }
                
                # 기록 유형별 주요 정보 추출
                if record_type == DetailedRecordType.ESTRUS.value:
                    event["key_info"]["intensity"] = record_data.get('estrus_intensity')
                    event["key_info"]["duration"] = record_data.get('estrus_duration')
                
                elif record_type == DetailedRecordType.INSEMINATION.value:
                    event["key_info"]["bull_breed"] = record_data.get('bull_breed')
                    event["key_info"]["success_probability"] = record_data.get('success_probability')
                
                elif record_type == DetailedRecordType.PREGNANCY_CHECK.value:
                    event["key_info"]["result"] = record_data.get('check_result')
                    event["key_info"]["pregnancy_stage"] = record_data.get('pregnancy_stage')
                    event["key_info"]["expected_calving"] = record_data.get('expected_calving_date')
                
                elif record_type == DetailedRecordType.CALVING.value:
                    event["key_info"]["calf_count"] = record_data.get('calf_count')
                    event["key_info"]["difficulty"] = record_data.get('calving_difficulty')
                    event["key_info"]["calf_weights"] = record_data.get('calf_weight')
                
                timeline_events.append(event)
        
        # 날짜순 정렬
        timeline_events.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            "cow_id": cow_id,
            "timeline_events": timeline_events,
            "total_events": len(timeline_events)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"번식 타임라인 조회 중 오류가 발생했습니다: {str(e)}"
        )

# ===== 젖소별 모든 기록 요약 =====
@router.get("/cow/{cow_id}/summary")
def get_cow_records_summary(
    cow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """젖소별 모든 기록 요약"""
    try:
        from config.firebase_config import get_firestore_client
        from datetime import datetime, timedelta
        
        db = get_firestore_client()
        farm_id = current_user.get("farm_id")
        
        # 기록 유형별 개수 집계
        record_counts = {}
        recent_records = []
        
        # 최근 30일 기준
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        for record_type in DetailedRecordType:
            # 전체 기록 수
            total_count = len(db.collection('cow_detailed_records')\
                .where('cow_id', '==', cow_id)\
                .where('farm_id', '==', farm_id)\
                .where('record_type', '==', record_type.value)\
                .where('is_active', '==', True)\
                .get())
            
            # 최근 30일 기록 수
            recent_count = len(db.collection('cow_detailed_records')\
                .where('cow_id', '==', cow_id)\
                .where('farm_id', '==', farm_id)\
                .where('record_type', '==', record_type.value)\
                .where('is_active', '==', True)\
                .where('record_date', '>=', thirty_days_ago)\
                .get())
            
            record_counts[record_type.value] = {
                "total": total_count,
                "recent": recent_count
            }
        
        # 최근 기록 5개 조회
        recent_query = db.collection('cow_detailed_records')\
            .where('cow_id', '==', cow_id)\
            .where('farm_id', '==', farm_id)\
            .where('is_active', '==', True)\
            .order_by('record_date', direction='DESCENDING')\
            .limit(5)\
            .get()
        
        for record in recent_query:
            data = record.to_dict()
            recent_records.append({
                "id": data.get('id'),
                "type": data.get('record_type'),
                "title": data.get('title'),
                "date": data.get('record_date'),
                "created_at": data.get('created_at')
            })
        
        return {
            "cow_id": cow_id,
            "record_counts": record_counts,
            "recent_records": recent_records,
            "summary_date": datetime.now().strftime('%Y-%m-%d')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기록 요약 조회 중 오류가 발생했습니다: {str(e)}"
        )