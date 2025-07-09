from datetime import datetime, timedelta
from typing import List, Dict, Any
from config.firebase_config import get_firestore_client
from services.notification_service import NotificationService
from schemas.notification import *
from schemas.task import TaskStatus, TaskPriority
import logging

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """자동 알림 스케줄러"""
    
    @staticmethod
    def check_task_due_notifications():
        """할일 마감 임박 알림 체크"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 마감 1시간 전인 할일들 조회
            due_soon_time = current_time + timedelta(hours=1)
            
            # 오늘 마감인 할일들 조회
            today = current_time.date().strftime('%Y-%m-%d')
            
            tasks_query = (db.collection('tasks')
                          .where('due_date', '==', today)
                          .where('is_active', '==', True)
                          .get())
            
            for task_doc in tasks_query:
                task_data = task_doc.to_dict()
                
                # 이미 완료된 할일은 제외
                if task_data['status'] in [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]:
                    continue
                
                # 마감 시간 확인
                due_datetime = task_data.get('due_datetime')
                if not due_datetime:
                    continue
                
                # 마감 1시간 전인지 확인
                if due_datetime <= due_soon_time and due_datetime > current_time:
                    # 이미 알림을 보냈는지 확인
                    if not NotificationScheduler._has_recent_notification(
                        user_id=task_data['owner_id'],
                        farm_id=task_data['farm_id'],
                        notification_type=NotificationType.TASK_DUE_SOON,
                        related_task_id=task_data['id'],
                        hours=1
                    ):
                        # 알림 생성
                        NotificationScheduler._create_task_due_notification(task_data)
            
            logger.info("할일 마감 임박 알림 체크 완료")
            
        except Exception as e:
            logger.error(f"할일 마감 임박 알림 체크 실패: {str(e)}")
    
    @staticmethod
    def check_overdue_task_notifications():
        """지연된 할일 알림 체크"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 지연된 할일들 조회
            tasks_query = (db.collection('tasks')
                          .where('is_active', '==', True)
                          .get())
            
            for task_doc in tasks_query:
                task_data = task_doc.to_dict()
                
                # 이미 완료된 할일은 제외
                if task_data['status'] in [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]:
                    continue
                
                # 마감 시간 확인
                due_datetime = task_data.get('due_datetime')
                if not due_datetime:
                    continue
                
                # 지연된 할일인지 확인
                if due_datetime < current_time:
                    # 이미 알림을 보냈는지 확인 (24시간 내)
                    if not NotificationScheduler._has_recent_notification(
                        user_id=task_data['owner_id'],
                        farm_id=task_data['farm_id'],
                        notification_type=NotificationType.TASK_OVERDUE,
                        related_task_id=task_data['id'],
                        hours=24
                    ):
                        # 알림 생성
                        NotificationScheduler._create_overdue_task_notification(task_data)
            
            logger.info("지연된 할일 알림 체크 완료")
            
        except Exception as e:
            logger.error(f"지연된 할일 알림 체크 실패: {str(e)}")
    
    @staticmethod
    def check_daily_summary_notifications():
        """일일 요약 알림 체크 (매일 오전 9시)"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 오늘 할일이 있는 사용자들 조회
            today = current_time.date().strftime('%Y-%m-%d')
            
            tasks_query = (db.collection('tasks')
                          .where('due_date', '==', today)
                          .where('is_active', '==', True)
                          .get())
            
            # 사용자별 할일 수 집계
            user_tasks = {}
            for task_doc in tasks_query:
                task_data = task_doc.to_dict()
                user_id = task_data['owner_id']
                farm_id = task_data['farm_id']
                
                if user_id not in user_tasks:
                    user_tasks[user_id] = {
                        'farm_id': farm_id,
                        'total_tasks': 0,
                        'completed_tasks': 0,
                        'pending_tasks': 0,
                        'overdue_tasks': 0
                    }
                
                user_tasks[user_id]['total_tasks'] += 1
                
                if task_data['status'] == TaskStatus.COMPLETED.value:
                    user_tasks[user_id]['completed_tasks'] += 1
                elif task_data['status'] == TaskStatus.OVERDUE.value:
                    user_tasks[user_id]['overdue_tasks'] += 1
                else:
                    user_tasks[user_id]['pending_tasks'] += 1
            
            # 각 사용자에게 일일 요약 알림 발송
            for user_id, task_summary in user_tasks.items():
                if task_summary['total_tasks'] > 0:
                    # 이미 오늘 요약 알림을 보냈는지 확인
                    if not NotificationScheduler._has_recent_notification(
                        user_id=user_id,
                        farm_id=task_summary['farm_id'],
                        notification_type=NotificationType.SYSTEM_MAINTENANCE,
                        hours=24,
                        metadata_filter={"type": "daily_summary"}
                    ):
                        NotificationScheduler._create_daily_summary_notification(user_id, task_summary)
            
            logger.info("일일 요약 알림 체크 완료")
            
        except Exception as e:
            logger.error(f"일일 요약 알림 체크 실패: {str(e)}")
    
    @staticmethod
    def check_weekly_summary_notifications():
        """주간 요약 알림 체크 (매주 월요일 오전 9시)"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 이번 주 할일들 조회
            week_ago = current_time - timedelta(days=7)
            
            tasks_query = (db.collection('tasks')
                          .where('created_at', '>=', week_ago)
                          .where('is_active', '==', True)
                          .get())
            
            # 사용자별 주간 통계 집계
            user_stats = {}
            for task_doc in tasks_query:
                task_data = task_doc.to_dict()
                user_id = task_data['owner_id']
                farm_id = task_data['farm_id']
                
                if user_id not in user_stats:
                    user_stats[user_id] = {
                        'farm_id': farm_id,
                        'total_tasks': 0,
                        'completed_tasks': 0,
                        'completion_rate': 0.0
                    }
                
                user_stats[user_id]['total_tasks'] += 1
                if task_data['status'] == TaskStatus.COMPLETED.value:
                    user_stats[user_id]['completed_tasks'] += 1
            
            # 완료율 계산
            for user_id, stats in user_stats.items():
                if stats['total_tasks'] > 0:
                    stats['completion_rate'] = (stats['completed_tasks'] / stats['total_tasks']) * 100
                    
                    # 이미 이번 주 요약 알림을 보냈는지 확인
                    if not NotificationScheduler._has_recent_notification(
                        user_id=user_id,
                        farm_id=stats['farm_id'],
                        notification_type=NotificationType.SYSTEM_MAINTENANCE,
                        hours=168,  # 7일
                        metadata_filter={"type": "weekly_summary"}
                    ):
                        NotificationScheduler._create_weekly_summary_notification(user_id, stats)
            
            logger.info("주간 요약 알림 체크 완료")
            
        except Exception as e:
            logger.error(f"주간 요약 알림 체크 실패: {str(e)}")
    
    # ===== 내부 메서드 =====
    
    @staticmethod
    def _has_recent_notification(
        user_id: str,
        farm_id: str,
        notification_type: NotificationType,
        hours: int = 24,
        related_task_id: str = None,
        metadata_filter: Dict[str, Any] = None
    ) -> bool:
        """최근에 동일한 알림을 보냈는지 확인"""
        try:
            db = get_firestore_client()
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            query = (db.collection('notifications')
                    .where('user_id', '==', user_id)
                    .where('farm_id', '==', farm_id)
                    .where('notification_type', '==', notification_type.value)
                    .where('created_at', '>=', time_threshold)
                    .get())
            
            for doc in query:
                notification_data = doc.to_dict()
                
                # 관련 할일 ID 확인
                if related_task_id and notification_data.get('related_task_id') == related_task_id:
                    return True
                
                # 메타데이터 필터 확인
                if metadata_filter:
                    metadata = notification_data.get('metadata', {})
                    if all(metadata.get(k) == v for k, v in metadata_filter.items()):
                        return True
                
                # 필터가 없는 경우 최근 알림이 있으면 True
                if not related_task_id and not metadata_filter:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"최근 알림 확인 실패: {str(e)}")
            return False
    
    @staticmethod
    def _create_task_due_notification(task_data: Dict[str, Any]):
        """할일 마감 임박 알림 생성"""
        try:
            # 젖소 이름 조회
            cow_name = None
            if task_data.get('related_cow_id'):
                try:
                    cow_info = NotificationScheduler._get_cow_info(task_data['related_cow_id'], task_data['farm_id'])
                    cow_name = cow_info.get('name')
                except:
                    cow_name = "삭제된 젖소"
            
            # 알림 메시지 생성
            title = "할일 마감 임박"
            message = f"'{task_data['title']}' 할일이 곧 마감됩니다."
            
            if cow_name:
                message += f" (관련 젖소: {cow_name})"
            
            # 우선순위에 따른 알림 우선순위 설정
            priority = NotificationPriority.NORMAL
            if task_data['priority'] in [TaskPriority.HIGH.value, TaskPriority.URGENT.value]:
                priority = NotificationPriority.HIGH
            
            notification_data = NotificationCreate(
                user_id=task_data['owner_id'],
                farm_id=task_data['farm_id'],
                notification_type=NotificationType.TASK_DUE_SOON,
                title=title,
                message=message,
                priority=priority,
                channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                related_task_id=task_data['id'],
                related_cow_id=task_data.get('related_cow_id'),
                metadata={"task_priority": task_data['priority']}
            )
            
            NotificationService.create_notification(notification_data)
            logger.info(f"할일 마감 임박 알림 생성: {task_data['title']}")
            
        except Exception as e:
            logger.error(f"할일 마감 임박 알림 생성 실패: {str(e)}")
    
    @staticmethod
    def _create_overdue_task_notification(task_data: Dict[str, Any]):
        """지연된 할일 알림 생성"""
        try:
            # 젖소 이름 조회
            cow_name = None
            if task_data.get('related_cow_id'):
                try:
                    cow_info = NotificationScheduler._get_cow_info(task_data['related_cow_id'], task_data['farm_id'])
                    cow_name = cow_info.get('name')
                except:
                    cow_name = "삭제된 젖소"
            
            # 알림 메시지 생성
            title = "할일 지연 알림"
            message = f"'{task_data['title']}' 할일이 마감일을 지났습니다."
            
            if cow_name:
                message += f" (관련 젖소: {cow_name})"
            
            # 우선순위에 따른 알림 우선순위 설정
            priority = NotificationPriority.HIGH
            if task_data['priority'] == TaskPriority.URGENT.value:
                priority = NotificationPriority.URGENT
            
            notification_data = NotificationCreate(
                user_id=task_data['owner_id'],
                farm_id=task_data['farm_id'],
                notification_type=NotificationType.TASK_OVERDUE,
                title=title,
                message=message,
                priority=priority,
                channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                related_task_id=task_data['id'],
                related_cow_id=task_data.get('related_cow_id'),
                metadata={"task_priority": task_data['priority']}
            )
            
            NotificationService.create_notification(notification_data)
            logger.info(f"지연된 할일 알림 생성: {task_data['title']}")
            
        except Exception as e:
            logger.error(f"지연된 할일 알림 생성 실패: {str(e)}")
    
    @staticmethod
    def _create_daily_summary_notification(user_id: str, task_summary: Dict[str, Any]):
        """일일 요약 알림 생성"""
        try:
            title = "오늘의 할일 요약"
            message = f"오늘 총 {task_summary['total_tasks']}개의 할일이 있습니다.\n"
            message += f"완료: {task_summary['completed_tasks']}개, "
            message += f"대기: {task_summary['pending_tasks']}개"
            
            if task_summary['overdue_tasks'] > 0:
                message += f", 지연: {task_summary['overdue_tasks']}개"
            
            notification_data = NotificationCreate(
                user_id=user_id,
                farm_id=task_summary['farm_id'],
                notification_type=NotificationType.SYSTEM_MAINTENANCE,
                title=title,
                message=message,
                priority=NotificationPriority.LOW,
                channels=[NotificationChannel.IN_APP],
                metadata={"type": "daily_summary", "task_summary": task_summary}
            )
            
            NotificationService.create_notification(notification_data)
            logger.info(f"일일 요약 알림 생성: {user_id}")
            
        except Exception as e:
            logger.error(f"일일 요약 알림 생성 실패: {str(e)}")
    
    @staticmethod
    def _create_weekly_summary_notification(user_id: str, stats: Dict[str, Any]):
        """주간 요약 알림 생성"""
        try:
            title = "이번 주 할일 요약"
            message = f"이번 주 총 {stats['total_tasks']}개의 할일을 완료했습니다.\n"
            message += f"완료율: {stats['completion_rate']:.1f}%"
            
            # 완료율에 따른 메시지 추가
            if stats['completion_rate'] >= 80:
                message += "\n훌륭한 한 주였습니다! 🎉"
            elif stats['completion_rate'] >= 60:
                message += "\n잘 하고 있습니다! 👍"
            else:
                message += "\n다음 주에는 더 많은 할일을 완료해보세요! 💪"
            
            notification_data = NotificationCreate(
                user_id=user_id,
                farm_id=stats['farm_id'],
                notification_type=NotificationType.SYSTEM_MAINTENANCE,
                title=title,
                message=message,
                priority=NotificationPriority.LOW,
                channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                metadata={"type": "weekly_summary", "stats": stats}
            )
            
            NotificationService.create_notification(notification_data)
            logger.info(f"주간 요약 알림 생성: {user_id}")
            
        except Exception as e:
            logger.error(f"주간 요약 알림 생성 실패: {str(e)}")
    
    @staticmethod
    def _get_cow_info(cow_id: str, farm_id: str) -> Dict[str, Any]:
        """젖소 정보 조회"""
        try:
            db = get_firestore_client()
            cow_doc = db.collection('cows').document(cow_id).get()
            if cow_doc.exists:
                cow_data = cow_doc.to_dict()
                if cow_data.get('farm_id') == farm_id:
                    return cow_data
            return {}
        except:
            return {} 