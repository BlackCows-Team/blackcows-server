# services/notification_service.py

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
from schemas.notification import *
from services.email_service import EmailService
import uuid
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """알림 관리 서비스"""
    
    @staticmethod
    def create_notification(notification_data: NotificationCreate) -> NotificationResponse:
        """알림 생성"""
        try:
            db = get_firestore_client()
            notification_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # 젖소 이름 조회
            cow_name = None
            if notification_data.related_cow_id:
                try:
                    cow_info = NotificationService._get_cow_info(notification_data.related_cow_id, notification_data.farm_id)
                    cow_name = cow_info.get('name')
                except:
                    cow_name = "삭제된 젖소"
            
            # 알림 문서 생성
            notification_document = {
                "id": notification_id,
                "user_id": notification_data.user_id,
                "farm_id": notification_data.farm_id,
                "notification_type": notification_data.notification_type.value,
                "title": notification_data.title,
                "message": notification_data.message,
                "priority": notification_data.priority.value,
                "status": NotificationStatus.PENDING.value,
                "channels": [channel.value for channel in notification_data.channels],
                
                # 관련 데이터
                "related_task_id": notification_data.related_task_id,
                "related_cow_id": notification_data.related_cow_id,
                "related_cow_name": cow_name,
                "related_record_id": notification_data.related_record_id,
                
                # 발송 정보
                "sent_at": None,
                "read_at": None,
                
                # 메타데이터
                "metadata": notification_data.metadata or {},
                "scheduled_at": notification_data.scheduled_at,
                "created_at": current_time,
                "updated_at": current_time
            }
            
            # Firestore에 저장
            db.collection('notifications').document(notification_id).set(notification_document)
            
            # 즉시 발송이 필요한 경우
            if not notification_data.scheduled_at or notification_data.scheduled_at <= current_time:
                NotificationService._send_notification(notification_document)
            
            return NotificationService._build_notification_response(notification_document)
            
        except Exception as e:
            logger.error(f"알림 생성 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알림 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_user_notifications(
        user_id: str, 
        farm_id: str,
        status_filter: Optional[NotificationStatus] = None,
        notification_type_filter: Optional[NotificationType] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[NotificationSummary]:
        """사용자 알림 목록 조회"""
        try:
            db = get_firestore_client()
            
            # 기본 쿼리
            query = (db.collection('notifications')
                    .where('user_id', '==', user_id)
                    .where('farm_id', '==', farm_id)
                    .order_by('created_at', direction='desc')
                    .limit(limit)
                    .offset(offset)
                    .get())
            
            notifications = []
            for doc in query:
                notification_data = doc.to_dict()
                
                # 필터링
                if status_filter and notification_data['status'] != status_filter.value:
                    continue
                if notification_type_filter and notification_data['notification_type'] != notification_type_filter.value:
                    continue
                
                # 메시지 축약
                message = notification_data['message']
                if len(message) > 100:
                    message = message[:97] + "..."
                
                notifications.append(NotificationSummary(
                    id=notification_data["id"],
                    notification_type=NotificationType(notification_data["notification_type"]),
                    title=notification_data["title"],
                    message=message,
                    priority=NotificationPriority(notification_data["priority"]),
                    status=NotificationStatus(notification_data["status"]),
                    is_read=notification_data["status"] == NotificationStatus.READ.value,
                    related_cow_name=notification_data.get("related_cow_name"),
                    created_at=notification_data["created_at"]
                ))
            
            return notifications
            
        except Exception as e:
            logger.error(f"알림 목록 조회 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알림 목록 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_notification_by_id(notification_id: str, user_id: str, farm_id: str) -> NotificationResponse:
        """특정 알림 조회"""
        try:
            db = get_firestore_client()
            
            doc = db.collection('notifications').document(notification_id).get()
            if not doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="알림을 찾을 수 없습니다"
                )
            
            notification_data = doc.to_dict()
            
            # 권한 확인
            if notification_data['user_id'] != user_id or notification_data['farm_id'] != farm_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="알림에 접근할 권한이 없습니다"
                )
            
            return NotificationService._build_notification_response(notification_data)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"알림 조회 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알림 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def mark_as_read(notification_id: str, user_id: str, farm_id: str) -> NotificationResponse:
        """알림 읽음 처리"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 알림 확인
            notification = NotificationService.get_notification_by_id(notification_id, user_id, farm_id)
            
            # 이미 읽은 경우
            if notification.status == NotificationStatus.READ:
                return notification
            
            # 상태 업데이트
            update_data = {
                "status": NotificationStatus.READ.value,
                "read_at": current_time,
                "updated_at": current_time
            }
            
            db.collection('notifications').document(notification_id).update(update_data)
            
            # 업데이트된 알림 반환
            return NotificationService.get_notification_by_id(notification_id, user_id, farm_id)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"알림 읽음 처리 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알림 읽음 처리 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def mark_all_as_read(user_id: str, farm_id: str) -> Dict[str, Any]:
        """모든 알림 읽음 처리"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 읽지 않은 알림들 조회
            unread_notifications = (db.collection('notifications')
                                  .where('user_id', '==', user_id)
                                  .where('farm_id', '==', farm_id)
                                  .where('status', '!=', NotificationStatus.READ.value)
                                  .get())
            
            updated_count = 0
            for doc in unread_notifications:
                doc.reference.update({
                    "status": NotificationStatus.READ.value,
                    "read_at": current_time,
                    "updated_at": current_time
                })
                updated_count += 1
            
            return {
                "success": True,
                "message": f"{updated_count}개의 알림을 읽음 처리했습니다",
                "updated_count": updated_count
            }
            
        except Exception as e:
            logger.error(f"전체 알림 읽음 처리 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"전체 알림 읽음 처리 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def delete_notification(notification_id: str, user_id: str, farm_id: str) -> Dict[str, Any]:
        """알림 삭제"""
        try:
            db = get_firestore_client()
            
            # 알림 확인
            notification = NotificationService.get_notification_by_id(notification_id, user_id, farm_id)
            
            # 삭제
            db.collection('notifications').document(notification_id).delete()
            
            return {
                "success": True,
                "message": "알림이 삭제되었습니다",
                "deleted_notification_id": notification_id
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"알림 삭제 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알림 삭제 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_notification_statistics(user_id: str, farm_id: str) -> NotificationStatistics:
        """알림 통계 조회"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            today = current_time.date()
            week_ago = current_time - timedelta(days=7)
            
            # 전체 알림 조회
            all_notifications = (db.collection('notifications')
                               .where('user_id', '==', user_id)
                               .where('farm_id', '==', farm_id)
                               .get())
            
            total_notifications = 0
            unread_count = 0
            today_count = 0
            this_week_count = 0
            type_stats = {}
            priority_stats = {}
            channel_stats = {}
            
            for doc in all_notifications:
                notification_data = doc.to_dict()
                total_notifications += 1
                
                # 읽지 않은 알림
                if notification_data['status'] != NotificationStatus.READ.value:
                    unread_count += 1
                
                # 오늘 알림
                if notification_data['created_at'].date() == today:
                    today_count += 1
                
                # 이번 주 알림
                if notification_data['created_at'] >= week_ago:
                    this_week_count += 1
                
                # 유형별 통계
                notification_type = notification_data['notification_type']
                type_stats[notification_type] = type_stats.get(notification_type, 0) + 1
                
                # 우선순위별 통계
                priority = notification_data['priority']
                priority_stats[priority] = priority_stats.get(priority, 0) + 1
                
                # 채널별 통계
                for channel in notification_data.get('channels', []):
                    channel_stats[channel] = channel_stats.get(channel, 0) + 1
            
            return NotificationStatistics(
                total_notifications=total_notifications,
                unread_count=unread_count,
                today_count=today_count,
                this_week_count=this_week_count,
                type_stats=type_stats,
                priority_stats=priority_stats,
                channel_stats=channel_stats
            )
            
        except Exception as e:
            logger.error(f"알림 통계 조회 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알림 통계 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_or_create_notification_settings(user_id: str, farm_id: str) -> NotificationSettings:
        """알림 설정 조회 또는 생성"""
        try:
            db = get_firestore_client()
            
            # 기존 설정 조회
            settings_doc = (db.collection('notification_settings')
                          .where('user_id', '==', user_id)
                          .where('farm_id', '==', farm_id)
                          .limit(1)
                          .get())
            
            if settings_doc:
                settings_data = settings_doc[0].to_dict()
                return NotificationSettings(**settings_data)
            
            # 기본 설정 생성
            current_time = datetime.utcnow()
            default_settings = {
                "user_id": user_id,
                "farm_id": farm_id,
                "in_app_enabled": True,
                "email_enabled": True,
                "push_enabled": False,
                "sms_enabled": False,
                "task_notifications": True,
                "cow_notifications": True,
                "system_notifications": True,
                "task_due_reminder_hours": 1,
                "quiet_hours_start": None,
                "quiet_hours_end": None,
                "created_at": current_time,
                "updated_at": current_time
            }
            
            settings_id = str(uuid.uuid4())
            db.collection('notification_settings').document(settings_id).set(default_settings)
            
            return NotificationSettings(**default_settings)
            
        except Exception as e:
            logger.error(f"알림 설정 조회/생성 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알림 설정 조회/생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def update_notification_settings(
        user_id: str, 
        farm_id: str, 
        settings_update: Dict[str, Any]
    ) -> NotificationSettings:
        """알림 설정 업데이트"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 기존 설정 조회
            settings = NotificationService.get_or_create_notification_settings(user_id, farm_id)
            
            # 업데이트할 데이터
            update_data = {"updated_at": current_time}
            for key, value in settings_update.items():
                if hasattr(settings, key):
                    update_data[key] = value
            
            # Firestore 업데이트
            settings_doc = (db.collection('notification_settings')
                          .where('user_id', '==', user_id)
                          .where('farm_id', '==', farm_id)
                          .limit(1)
                          .get())
            
            if settings_doc:
                settings_doc[0].reference.update(update_data)
            else:
                # 설정이 없는 경우 새로 생성
                settings_id = str(uuid.uuid4())
                db.collection('notification_settings').document(settings_id).set(update_data)
            
            # 업데이트된 설정 반환
            return NotificationService.get_or_create_notification_settings(user_id, farm_id)
            
        except Exception as e:
            logger.error(f"알림 설정 업데이트 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알림 설정 업데이트 중 오류가 발생했습니다: {str(e)}"
            )
    
    # ===== 내부 메서드 =====
    
    @staticmethod
    def _send_notification(notification_data: Dict[str, Any]):
        """알림 발송 처리"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 사용자 설정 조회
            settings = NotificationService.get_or_create_notification_settings(
                notification_data['user_id'], 
                notification_data['farm_id']
            )
            
            # 채널별 발송
            for channel in notification_data['channels']:
                if channel == NotificationChannel.IN_APP.value:
                    # 앱 내 알림은 이미 저장됨
                    pass
                
                elif channel == NotificationChannel.EMAIL.value and settings.email_enabled:
                    NotificationService._send_email_notification(notification_data)
                
                elif channel == NotificationChannel.PUSH.value and settings.push_enabled:
                    # 푸시 알림 발송
                    from services.fcm_service import FCMService
                    FCMService.send_push_notification(
                        user_id=notification_data['user_id'],
                        title=notification_data['title'],
                        body=notification_data['message'],
                        data={
                            'notification_id': notification_data['id'],
                            'notification_type': notification_data['notification_type'],
                            'related_cow_id': notification_data.get('related_cow_id', ''),
                            'related_task_id': notification_data.get('related_task_id', ''),
                            'related_record_id': notification_data.get('related_record_id', '')
                        }
                    )
                
                elif channel == NotificationChannel.SMS.value and settings.sms_enabled:
                    # SMS 알림 (향후 구현)
                    pass
            
            # 상태 업데이트
            db.collection('notifications').document(notification_data['id']).update({
                "status": NotificationStatus.SENT.value,
                "sent_at": current_time,
                "updated_at": current_time
            })
            
        except Exception as e:
            logger.error(f"알림 발송 실패: {str(e)}")
            # 실패 상태로 업데이트
            db = get_firestore_client()
            db.collection('notifications').document(notification_data['id']).update({
                "status": NotificationStatus.FAILED.value,
                "updated_at": datetime.utcnow()
            })
    
    @staticmethod
    def _send_email_notification(notification_data: Dict[str, Any]):
        """이메일 알림 발송"""
        try:
            # 사용자 정보 조회
            user_info = NotificationService._get_user_info(notification_data['user_id'])
            if not user_info or not user_info.get('email'):
                logger.warning(f"사용자 이메일 정보 없음: {notification_data['user_id']}")
                return
            
            # 이메일 제목 및 내용 생성
            subject = f"[BlackCows] {notification_data['title']}"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50;">{notification_data['title']}</h2>
                <p style="color: #34495e; line-height: 1.6;">{notification_data['message']}</p>
                
                {f'<p style="color: #7f8c8d; font-size: 14px;">관련 젖소: {notification_data.get("related_cow_name", "N/A")}</p>' if notification_data.get("related_cow_name") else ''}
                
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
                <p style="color: #95a5a6; font-size: 12px;">
                    이 이메일은 BlackCows 낙농 관리 시스템에서 자동으로 발송되었습니다.<br>
                    알림 설정을 변경하려면 앱에서 설정을 확인해주세요.
                </p>
            </div>
            """
            
            # 이메일 발송
            EmailService._send_email(
                to_email=user_info['email'],
                subject=subject,
                html_content=html_content
            )
            
            logger.info(f"이메일 알림 발송 성공: {user_info['email']} - {subject}")
            
        except Exception as e:
            logger.error(f"이메일 알림 발송 실패: {str(e)}")
            raise
    
    @staticmethod
    def _get_cow_info(cow_id: str, farm_id: str) -> Optional[Dict[str, Any]]:
        """젖소 정보 조회"""
        try:
            db = get_firestore_client()
            cow_doc = db.collection('cows').document(cow_id).get()
            if cow_doc.exists:
                cow_data = cow_doc.to_dict()
                if cow_data.get('farm_id') == farm_id:
                    return cow_data
            return None
        except:
            return None
    
    @staticmethod
    def _get_user_info(user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 정보 조회"""
        try:
            db = get_firestore_client()
            user_doc = db.collection('users').document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except:
            return None
    
    @staticmethod
    def _build_notification_response(notification_data: Dict[str, Any]) -> NotificationResponse:
        """알림 응답 객체 생성"""
        return NotificationResponse(
            id=notification_data["id"],
            user_id=notification_data["user_id"],
            farm_id=notification_data["farm_id"],
            notification_type=NotificationType(notification_data["notification_type"]),
            title=notification_data["title"],
            message=notification_data["message"],
            priority=NotificationPriority(notification_data["priority"]),
            status=NotificationStatus(notification_data["status"]),
            related_task_id=notification_data.get("related_task_id"),
            related_cow_id=notification_data.get("related_cow_id"),
            related_cow_name=notification_data.get("related_cow_name"),
            related_record_id=notification_data.get("related_record_id"),
            channels=[NotificationChannel(channel) for channel in notification_data.get("channels", [])],
            sent_at=notification_data.get("sent_at"),
            read_at=notification_data.get("read_at"),
            metadata=notification_data.get("metadata", {}),
            created_at=notification_data["created_at"],
            updated_at=notification_data["updated_at"]
        ) 