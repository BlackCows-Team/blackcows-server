# routers/task.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date
from schemas.task import *
from services.task_service import TaskService
from routers.auth_firebase import get_current_user

router = APIRouter(tags=["할일 관리"])

# 디버깅용 테스트 엔드포인트
@router.get("/test-auth", summary="인증 테스트")
def test_authentication(current_user: dict = Depends(get_current_user)):
    """인증 상태를 테스트하는 엔드포인트"""
    return {
        "success": True,
        "message": "인증 성공",
        "user": {
            "id": current_user.get("id"),
            "username": current_user.get("username"),
            "farm_id": current_user.get("farm_id")
        }
    }

@router.post("/create", 
             response_model=TaskResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="할일 생성",
             description="""
             새로운 할일을 생성합니다.
             
             **주요 기능:**
             - 개인/젖소별/농장 전체 할일 생성
             - 우선순위 및 카테고리 설정
             - 마감일/시간 설정
             - 반복 일정 설정 (일/주/월/년)
             - 젖소 연결 (젖소별 할일인 경우)
             
             **사용 예시:**
             - 매일 오전 6시 착유 체크
             - 특정 젖소 백신 접종 일정
             - 주간 시설 점검
             """)
def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """할일 생성"""
    return TaskService.create_task(task_data, current_user)

@router.get("/",
           response_model=List[TaskSummary],
           summary="할일 목록 조회",
           description="""
           할일 목록을 조회합니다. 다양한 필터링 옵션을 제공합니다.
           
           **필터링 옵션:**
           - 상태별 필터링 (대기중/진행중/완료/지연)
           - 우선순위별 필터링 (낮음/보통/높음/긴급)
           - 카테고리별 필터링 (착유/치료/백신 등)
           - 특정 젖소 할일만 조회
           """)
def get_tasks(
    status_filter: Optional[TaskStatus] = Query(None, description="상태 필터"),
    priority_filter: Optional[TaskPriority] = Query(None, description="우선순위 필터"),
    category_filter: Optional[TaskCategory] = Query(None, description="카테고리 필터"),
    cow_id_filter: Optional[str] = Query(None, description="젖소 ID 필터"),
    limit: int = Query(50, description="조회 개수 제한", ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """할일 목록 조회"""
    return TaskService.get_tasks(
        current_user, 
        status_filter, 
        priority_filter, 
        category_filter, 
        cow_id_filter, 
        limit
    )

@router.get("/today",
           response_model=List[TaskSummary],
           summary="오늘 할일 조회",
           description="""
           오늘 마감인 할일들을 조회합니다.
           
           **특징:**
           - 오늘 날짜가 마감일인 할일만 조회
           - 마감 시간 순으로 정렬
           - 미완료 상태인 할일만 포함
           - 모바일 홈화면에 최적화
           """)
def get_today_tasks(current_user: dict = Depends(get_current_user)):
    """오늘 할일 조회"""
    return TaskService.get_today_tasks(current_user)

@router.get("/overdue",
           response_model=List[TaskSummary],
           summary="지연된 할일 조회",
           description="""
           마감일이 지난 미완료 할일들을 조회합니다.
           
           **특징:**
           - 마감일이 현재 시간보다 이전인 할일
           - 자동으로 상태를 'overdue'로 업데이트
           - 마감일이 오래된 순으로 정렬
           - 긴급 처리가 필요한 할일 식별
           """)
def get_overdue_tasks(current_user: dict = Depends(get_current_user)):
    """지연된 할일 조회"""
    return TaskService.get_overdue_tasks(current_user)

@router.get("/statistics",
           response_model=TaskStatistics,
           summary="할일 통계 조회",
           description="""
           할일 관련 통계 정보를 조회합니다.
           
           **통계 정보:**
           - 전체/대기중/완료/지연된 할일 수
           - 오늘 할일 및 높은 우선순위 할일 수
           - 카테고리별 할일 분포
           - 우선순위별 할일 분포
           - 완료율 (백분율)
           """)
def get_task_statistics(current_user: dict = Depends(get_current_user)):
    """할일 통계 조회"""
    return TaskService.get_task_statistics(current_user)

@router.get("/calendar",
           response_model=CalendarResponse,
           summary="캘린더 뷰용 할일 조회",
           description="""
           캘린더 뷰용 할일 데이터를 조회합니다.
           
           **특징:**
           - 날짜별로 그룹화된 할일 목록
           - 최대 3개월 범위 제한
           - 할일 상태, 카테고리, 우선순위 정보 포함
           """)
def get_calendar_tasks(
    start_date: date = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="종료 날짜 (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    """캘린더 뷰용 할일 조회"""
    return TaskService.get_calendar_tasks(current_user, start_date, end_date)

@router.get("/{task_id}",
           response_model=TaskResponse,
           summary="할일 상세 조회",
           description="특정 할일의 상세 정보를 조회합니다.")
def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """할일 상세 조회"""
    farm_id = current_user.get("farm_id")
    return TaskService.get_task_by_id(task_id, farm_id)

@router.put("/{task_id}/update",
           response_model=TaskResponse,
           summary="할일 수정",
           description="""
           기존 할일을 수정합니다.
           
           **수정 가능한 항목:**
           - 제목 및 설명
           - 우선순위 및 상태
           - 마감일 및 시간
           - 카테고리
           - 추가 메모
           """)
def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user)
):
    """할일 수정"""
    return TaskService.update_task(task_id, task_update, current_user)

@router.patch("/{task_id}/complete",
              response_model=TaskResponse,
              summary="할일 완료 처리",
              description="""
              할일을 완료 상태로 변경합니다.
              
              **기능:**
              - 완료 시간 자동 기록
              - 완료 메모 추가 가능
              - 반복 할일인 경우 다음 할일 자동 생성
              - 완료율 통계에 반영
              """)
def complete_task(
    task_id: str,
    completion_data: TaskComplete,
    current_user: dict = Depends(get_current_user)
):
    """할일 완료 처리"""
    return TaskService.complete_task(task_id, completion_data, current_user)

@router.delete("/{task_id}",
              summary="할일 삭제",
              description="""
              할일을 삭제합니다 (소프트 삭제).
              
              **주의사항:**
              - 실제로는 비활성화 처리
              - 통계에서 제외됨
              - 복구 불가능
              """)
def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """할일 삭제"""
    return TaskService.delete_task(task_id, current_user)