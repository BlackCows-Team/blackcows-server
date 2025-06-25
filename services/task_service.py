# services/task_service.py

from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
from schemas.task import *
import uuid

class TaskService:
    
    @staticmethod
    def create_task(task_data: TaskCreate, user: Dict) -> TaskResponse:
        """할일 생성"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 젖소별 할일인 경우 젖소 존재 확인
            cow_info = None
            if task_data.task_type == TaskType.COW_SPECIFIC and task_data.related_cow_id:
                cow_info = TaskService._get_cow_info(task_data.related_cow_id, farm_id)
            
            task_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # 마감일시 조합
            due_datetime = None
            if task_data.due_date:
                due_date_obj = datetime.strptime(task_data.due_date, '%Y-%m-%d').date()
                if task_data.due_time:
                    due_time_obj = datetime.strptime(task_data.due_time, '%H:%M').time()
                    due_datetime = datetime.combine(due_date_obj, due_time_obj)
                else:
                    due_datetime = datetime.combine(due_date_obj, datetime.min.time())
            
            # 초기 상태 설정
            initial_status = TaskStatus.PENDING
            if due_datetime and due_datetime < current_time:
                initial_status = TaskStatus.OVERDUE
            
            task_document = {
                "id": task_id,
                "title": task_data.title,
                "description": task_data.description,
                "task_type": task_data.task_type.value,
                "priority": task_data.priority.value,
                "status": initial_status.value,
                "due_date": task_data.due_date,
                "due_time": task_data.due_time,
                "due_datetime": due_datetime,
                "category": task_data.category.value,
                "related_cow_id": task_data.related_cow_id,
                "auto_generated": task_data.auto_generated,
                "recurrence": task_data.recurrence.value,
                "notes": task_data.notes,
                "farm_id": farm_id,
                "owner_id": user.get("id"),
                "completed_at": None,
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True
            }
            
            # Firestore에 저장
            db.collection('tasks').document(task_id).set(task_document)
            
            # 반복 할일인 경우 다음 할일 자동 생성
            if task_data.recurrence != TaskRecurrence.NONE:
                TaskService._create_recurring_task(task_data, task_id, user, due_datetime)
            
            return TaskService._build_task_response(task_document, cow_info)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"할일 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_tasks(
        user: Dict, 
        status_filter: Optional[TaskStatus] = None,
        priority_filter: Optional[TaskPriority] = None,
        category_filter: Optional[TaskCategory] = None,
        cow_id_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[TaskSummary]:
        """할일 목록 조회"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 기본 쿼리
            query = (db.collection('tasks')
                    .where('farm_id', '==', farm_id)
                    .where('is_active', '==', True)
                    .get())
            
            # 필터 적용
            if status_filter:
                query = query.where('status', '==', status_filter.value)
            if priority_filter:
                query = query.where('priority', '==', priority_filter.value)
            if category_filter:
                query = query.where('category', '==', category_filter.value)
            if cow_id_filter:
                query = query.where('related_cow_id', '==', cow_id_filter)
            
            # 정렬 및 제한
            tasks_query = query.order_by('created_at', direction='DESCENDING').limit(limit).get()
            
            tasks = []
            current_time = datetime.utcnow()
            
            for task_doc in tasks_query:
                task_data = task_doc.to_dict()
                
                # 지연 상태 체크
                is_overdue = False
                if (task_data.get('due_datetime') and 
                    task_data['status'] in [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value] and
                    task_data['due_datetime'] < current_time):
                    is_overdue = True
                    # 상태 업데이트
                    db.collection('tasks').document(task_data['id']).update({
                        'status': TaskStatus.OVERDUE.value,
                        'updated_at': current_time
                    })
                
                # 젖소 정보 조회
                cow_name = None
                if task_data.get('related_cow_id'):
                    try:
                        cow_info = TaskService._get_cow_info(task_data['related_cow_id'], farm_id)
                        cow_name = cow_info['name']
                    except:
                        cow_name = "삭제된 젖소"
                
                tasks.append(TaskSummary(
                    id=task_data["id"],
                    title=task_data["title"],
                    task_type=TaskType(task_data["task_type"]),
                    priority=TaskPriority(task_data["priority"]),
                    status=TaskStatus.OVERDUE if is_overdue else TaskStatus(task_data["status"]),
                    due_date=task_data.get("due_date"),
                    due_time=task_data.get("due_time"),
                    category=TaskCategory(task_data["category"]),
                    related_cow_name=cow_name,
                    is_overdue=is_overdue,
                    created_at=task_data["created_at"]
                ))
            
            return tasks
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"할일 목록 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_today_tasks(user: Dict) -> List[TaskSummary]:
        """오늘 할일 조회"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            today = date.today().strftime('%Y-%m-%d')
            
            # 오늘 마감인 할일들 조회
            tasks_query = (db.collection('tasks')
                          .where('farm_id', '==', farm_id)
                          .where('due_date', '==', today)
                          .where('is_active', '==', True)
                          .where('status', 'in', [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value])
                          .order_by('due_time')
                          .get())
            
            tasks = []
            for task_doc in tasks_query:
                task_data = task_doc.to_dict()
                
                # 젖소 정보 조회
                cow_name = None
                if task_data.get('related_cow_id'):
                    try:
                        cow_info = TaskService._get_cow_info(task_data['related_cow_id'], farm_id)
                        cow_name = cow_info['name']
                    except:
                        cow_name = "삭제된 젖소"
                
                tasks.append(TaskSummary(
                    id=task_data["id"],
                    title=task_data["title"],
                    task_type=TaskType(task_data["task_type"]),
                    priority=TaskPriority(task_data["priority"]),
                    status=TaskStatus(task_data["status"]),
                    due_date=task_data.get("due_date"),
                    due_time=task_data.get("due_time"),
                    category=TaskCategory(task_data["category"]),
                    related_cow_name=cow_name,
                    is_overdue=False,
                    created_at=task_data["created_at"]
                ))
            
            return tasks
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"오늘 할일 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_overdue_tasks(user: Dict) -> List[TaskSummary]:
        """지연된 할일 조회"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            current_time = datetime.utcnow()
            
            # 지연된 할일들 조회
            tasks_query = (db.collection('tasks')
                          .where('farm_id', '==', farm_id)
                          .where('is_active', '==', True)
                          .where('status', 'in', [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value, TaskStatus.OVERDUE.value])
                          .order_by('due_datetime')
                          .get())
            
            overdue_tasks = []
            for task_doc in tasks_query:
                task_data = task_doc.to_dict()
                
                # 지연 체크
                if (task_data.get('due_datetime') and 
                    task_data['due_datetime'] < current_time):
                    
                    # 상태 업데이트
                    if task_data['status'] != TaskStatus.OVERDUE.value:
                        db.collection('tasks').document(task_data['id']).update({
                            'status': TaskStatus.OVERDUE.value,
                            'updated_at': current_time
                        })
                    
                    # 젖소 정보 조회
                    cow_name = None
                    if task_data.get('related_cow_id'):
                        try:
                            cow_info = TaskService._get_cow_info(task_data['related_cow_id'], farm_id)
                            cow_name = cow_info['name']
                        except:
                            cow_name = "삭제된 젖소"
                    
                    overdue_tasks.append(TaskSummary(
                        id=task_data["id"],
                        title=task_data["title"],
                        task_type=TaskType(task_data["task_type"]),
                        priority=TaskPriority(task_data["priority"]),
                        status=TaskStatus.OVERDUE,
                        due_date=task_data.get("due_date"),
                        due_time=task_data.get("due_time"),
                        category=TaskCategory(task_data["category"]),
                        related_cow_name=cow_name,
                        is_overdue=True,
                        created_at=task_data["created_at"]
                    ))
            
            return overdue_tasks
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"지연된 할일 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def update_task(task_id: str, task_update: TaskUpdate, user: Dict) -> TaskResponse:
        """할일 수정"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 기존 할일 확인
            existing_task = TaskService.get_task_by_id(task_id, farm_id)
            
            # 업데이트할 데이터 구성
            update_data = {"updated_at": datetime.utcnow()}
            
            if task_update.title is not None:
                update_data["title"] = task_update.title
            if task_update.description is not None:
                update_data["description"] = task_update.description
            if task_update.priority is not None:
                update_data["priority"] = task_update.priority.value
            if task_update.due_date is not None:
                update_data["due_date"] = task_update.due_date
            if task_update.due_time is not None:
                update_data["due_time"] = task_update.due_time
            if task_update.category is not None:
                update_data["category"] = task_update.category.value
            if task_update.status is not None:
                update_data["status"] = task_update.status.value
            if task_update.notes is not None:
                update_data["notes"] = task_update.notes
            
            # 마감일시 업데이트
            if task_update.due_date is not None or task_update.due_time is not None:
                due_date = task_update.due_date or existing_task.due_date
                due_time = task_update.due_time or existing_task.due_time
                
                if due_date:
                    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
                    if due_time:
                        due_time_obj = datetime.strptime(due_time, '%H:%M').time()
                        update_data["due_datetime"] = datetime.combine(due_date_obj, due_time_obj)
                    else:
                        update_data["due_datetime"] = datetime.combine(due_date_obj, datetime.min.time())
            
            # Firestore 업데이트
            db.collection('tasks').document(task_id).update(update_data)
            
            # 업데이트된 할일 반환
            return TaskService.get_task_by_id(task_id, farm_id)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"할일 수정 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def complete_task(task_id: str, completion_data: TaskComplete, user: Dict) -> TaskResponse:
        """할일 완료 처리"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            current_time = datetime.utcnow()
            
            # 기존 할일 확인
            existing_task = TaskService.get_task_by_id(task_id, farm_id)
            
            if existing_task.status == TaskStatus.COMPLETED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 완료된 할일입니다"
                )
            
            # 완료 처리
            update_data = {
                "status": TaskStatus.COMPLETED.value,
                "completed_at": current_time,
                "updated_at": current_time
            }
            
            if completion_data.completion_notes:
                update_data["completion_notes"] = completion_data.completion_notes
            
            # Firestore 업데이트
            db.collection('tasks').document(task_id).update(update_data)
            
            # 반복 할일인 경우 다음 할일 자동 생성
            if existing_task.recurrence != TaskRecurrence.NONE:
                TaskService._create_next_recurring_task(existing_task, user)
            
            # 완료된 할일 반환
            return TaskService.get_task_by_id(task_id, farm_id)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"할일 완료 처리 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def delete_task(task_id: str, user: Dict) -> Dict:
        """할일 삭제"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            
            # 기존 할일 확인
            existing_task = TaskService.get_task_by_id(task_id, farm_id)
            
            # 소프트 삭제
            db.collection('tasks').document(task_id).update({
                "is_active": False,
                "updated_at": datetime.utcnow(),
                "deleted_at": datetime.utcnow()
            })
            
            return {
                "message": f"할일 '{existing_task.title}'이 삭제되었습니다",
                "task_id": task_id
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"할일 삭제 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_task_statistics(user: Dict) -> TaskStatistics:
        """할일 통계 조회"""
        try:
            db = get_firestore_client()
            farm_id = user.get("farm_id")
            today = date.today().strftime('%Y-%m-%d')
            
            # 전체 할일 조회
            all_tasks = (db.collection('tasks')
                        .where('farm_id', '==', farm_id)
                        .where('is_active', '==', True)
                        .get())
            
            total_tasks = len(all_tasks)
            pending_tasks = 0
            completed_tasks = 0
            overdue_tasks = 0
            today_tasks = 0
            high_priority_tasks = 0
            
            category_stats = {}
            priority_stats = {}
            
            current_time = datetime.utcnow()
            
            for task_doc in all_tasks:
                task_data = task_doc.to_dict()
                
                # 상태별 집계
                if task_data['status'] == TaskStatus.COMPLETED.value:
                    completed_tasks += 1
                elif task_data['status'] in [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]:
                    pending_tasks += 1
                elif task_data['status'] == TaskStatus.OVERDUE.value:
                    overdue_tasks += 1
                
                # 지연 상태 재체크
                if (task_data.get('due_datetime') and 
                    task_data['status'] in [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value] and
                    task_data['due_datetime'] < current_time):
                    overdue_tasks += 1
                    pending_tasks -= 1
                
                # 오늘 할일
                if task_data.get('due_date') == today:
                    today_tasks += 1
                
                # 높은 우선순위
                if task_data['priority'] in [TaskPriority.HIGH.value, TaskPriority.URGENT.value]:
                    high_priority_tasks += 1
                
                # 카테고리별 집계
                category = task_data['category']
                category_stats[category] = category_stats.get(category, 0) + 1
                
                # 우선순위별 집계
                priority = task_data['priority']
                priority_stats[priority] = priority_stats.get(priority, 0) + 1
            
            # 완료율 계산
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            return TaskStatistics(
                total_tasks=total_tasks,
                pending_tasks=pending_tasks,
                completed_tasks=completed_tasks,
                overdue_tasks=overdue_tasks,
                today_tasks=today_tasks,
                high_priority_tasks=high_priority_tasks,
                by_category=category_stats,
                by_priority=priority_stats,
                completion_rate=round(completion_rate, 2)
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"할일 통계 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_task_by_id(task_id: str, farm_id: str) -> TaskResponse:
        """할일 상세 조회"""
        try:
            db = get_firestore_client()
            task_doc = db.collection('tasks').document(task_id).get()
            
            if not task_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="할일을 찾을 수 없습니다"
                )
            
            task_data = task_doc.to_dict()
            
            if task_data.get("farm_id") != farm_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="할일을 찾을 수 없습니다"
                )
            
            # 젖소 정보 조회
            cow_info = None
            if task_data.get('related_cow_id'):
                try:
                    cow_info = TaskService._get_cow_info(task_data['related_cow_id'], farm_id)
                except:
                    pass
            
            return TaskService._build_task_response(task_data, cow_info)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"할일 조회 중 오류가 발생했습니다: {str(e)}"
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
    def _build_task_response(task_data: Dict, cow_info: Optional[Dict] = None) -> TaskResponse:
        """할일 응답 객체 생성"""
        return TaskResponse(
            id=task_data["id"],
            title=task_data["title"],
            description=task_data.get("description"),
            task_type=TaskType(task_data["task_type"]),
            priority=TaskPriority(task_data["priority"]),
            status=TaskStatus(task_data["status"]),
            due_date=task_data.get("due_date"),
            due_time=task_data.get("due_time"),
            category=TaskCategory(task_data["category"]),
            related_cow_id=task_data.get("related_cow_id"),
            related_cow_name=cow_info["name"] if cow_info else None,
            related_cow_ear_tag=cow_info["ear_tag_number"] if cow_info else None,
            auto_generated=task_data.get("auto_generated", False),
            recurrence=TaskRecurrence(task_data["recurrence"]),
            notes=task_data.get("notes"),
            farm_id=task_data["farm_id"],
            owner_id=task_data["owner_id"],
            completed_at=task_data.get("completed_at"),
            created_at=task_data["created_at"],
            updated_at=task_data["updated_at"],
            is_active=task_data["is_active"]
        )
    
    @staticmethod
    def _create_recurring_task(task_data: TaskCreate, parent_task_id: str, user: Dict, due_datetime: Optional[datetime]):
        """반복 할일 생성"""
        if not due_datetime or task_data.recurrence == TaskRecurrence.NONE:
            return
        
        # 다음 실행일 계산
        next_due_datetime = TaskService._calculate_next_due_date(due_datetime, task_data.recurrence)
        
        if next_due_datetime:
            # 다음 할일 자동 생성 (백그라운드에서)
            # 실제로는 백그라운드 작업으로 처리해야함.
            pass
    
    @staticmethod
    def _create_next_recurring_task(completed_task: TaskResponse, user: Dict):
        """완료된 반복 할일의 다음 할일 생성"""
        if completed_task.recurrence == TaskRecurrence.NONE:
            return
        
        # 다음 실행일 계산
        if completed_task.due_date:
            current_due = datetime.strptime(completed_task.due_date, '%Y-%m-%d')
            if completed_task.due_time:
                time_obj = datetime.strptime(completed_task.due_time, '%H:%M').time()
                current_due = datetime.combine(current_due.date(), time_obj)
            
            next_due_datetime = TaskService._calculate_next_due_date(current_due, completed_task.recurrence)
            
            if next_due_datetime:
                # 새로운 할일 생성
                next_task_data = TaskCreate(
                    title=completed_task.title,
                    description=completed_task.description,
                    task_type=completed_task.task_type,
                    priority=completed_task.priority,
                    due_date=next_due_datetime.strftime('%Y-%m-%d'),
                    due_time=next_due_datetime.strftime('%H:%M') if completed_task.due_time else None,
                    category=completed_task.category,
                    related_cow_id=completed_task.related_cow_id,
                    auto_generated=True,
                    recurrence=completed_task.recurrence,
                    notes=completed_task.notes
                )
                
                TaskService.create_task(next_task_data, user)
    
    @staticmethod
    def _calculate_next_due_date(current_due: datetime, recurrence: TaskRecurrence) -> Optional[datetime]:
        """다음 실행일 계산"""
        if recurrence == TaskRecurrence.DAILY:
            return current_due + timedelta(days=1)
        elif recurrence == TaskRecurrence.WEEKLY:
            return current_due + timedelta(weeks=1)
        elif recurrence == TaskRecurrence.MONTHLY:
            # 월 단위 계산 (같은 날짜)
            if current_due.month == 12:
                next_month = current_due.replace(year=current_due.year + 1, month=1)
            else:
                next_month = current_due.replace(month=current_due.month + 1)
            return next_month
        elif recurrence == TaskRecurrence.YEARLY:
            return current_due.replace(year=current_due.year + 1)
        
        return None