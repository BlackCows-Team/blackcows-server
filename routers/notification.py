# routers/notification.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from services.notification_service import NotificationService
from schemas.notification import *
from routers.auth_firebase import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create",
           response_model=NotificationResponse,
           summary="알림 생성",
           description="""
           새로운 알림을 생성합니다.
           
           **특징:**
           - 즉시 발송 또는 예약 발송 지원
           - 다중 채널 발송 (앱 내, 이메일, 푸시, SMS)
           - 관련 데이터 연결 (할일, 젖소, 기록)
           - 우선순위 설정 가능
           """)
def create_notification(
    notification_data: NotificationCreate,
    current_user: dict = Depends(get_current_user)
):
    """알림 생성"""
    # 권한 확인 - 자신의 알림만 생성 가능
    if notification_data.user_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 알림을 생성할 수 없습니다"
        )
    
    # 농장 ID 설정
    notification_data.farm_id = current_user.get("farm_id")
    
    return NotificationService.create_notification(notification_data)

@router.get("/",
           response_model=List[NotificationSummary],
           summary="알림 목록 조회",
           description="""
           사용자의 알림 목록을 조회합니다.
           
           **필터링 옵션:**
           - 상태별 필터링 (읽음/읽지 않음)
           - 알림 유형별 필터링
           - 페이지네이션 지원
           """)
def get_notifications(
    status_filter: Optional[NotificationStatus] = Query(None, description="알림 상태 필터"),
    notification_type_filter: Optional[NotificationType] = Query(None, description="알림 유형 필터"),
    limit: int = Query(50, ge=1, le=100, description="조회할 알림 수"),
    offset: int = Query(0, ge=0, description="건너뛸 알림 수"),
    current_user: dict = Depends(get_current_user)
):
    """알림 목록 조회"""
    return NotificationService.get_user_notifications(
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id"),
        status_filter=status_filter,
        notification_type_filter=notification_type_filter,
        limit=limit,
        offset=offset
    )

@router.get("/unread",
           response_model=List[NotificationSummary],
           summary="읽지 않은 알림 조회",
           description="읽지 않은 알림만 조회합니다.")
def get_unread_notifications(
    limit: int = Query(20, ge=1, le=50, description="조회할 알림 수"),
    current_user: dict = Depends(get_current_user)
):
    """읽지 않은 알림 조회"""
    return NotificationService.get_user_notifications(
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id"),
        status_filter=NotificationStatus.SENT,  # 발송되었지만 읽지 않은 알림
        limit=limit
    )

@router.get("/{notification_id}",
           response_model=NotificationResponse,
           summary="알림 상세 조회",
           description="특정 알림의 상세 정보를 조회합니다.")
def get_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """알림 상세 조회"""
    return NotificationService.get_notification_by_id(
        notification_id=notification_id,
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id")
    )

@router.patch("/{notification_id}/read",
           response_model=NotificationResponse,
           summary="알림 읽음 처리",
           description="알림을 읽음 상태로 변경합니다.")
def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """알림 읽음 처리"""
    return NotificationService.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id")
    )

@router.patch("/read-all",
           summary="모든 알림 읽음 처리",
           description="모든 읽지 않은 알림을 읽음 상태로 변경합니다.")
def mark_all_notifications_as_read(
    current_user: dict = Depends(get_current_user)
):
    """모든 알림 읽음 처리"""
    return NotificationService.mark_all_as_read(
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id")
    )

@router.delete("/{notification_id}",
             summary="알림 삭제",
             description="특정 알림을 삭제합니다.")
def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """알림 삭제"""
    return NotificationService.delete_notification(
        notification_id=notification_id,
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id")
    )

@router.get("/statistics",
           response_model=NotificationStatistics,
           summary="알림 통계 조회",
           description="""
           알림 관련 통계 정보를 조회합니다.
           
           **포함 정보:**
           - 총 알림 수, 읽지 않은 알림 수
           - 오늘/이번 주 받은 알림 수
           - 유형별, 우선순위별, 채널별 통계
           """)
def get_notification_statistics(
    current_user: dict = Depends(get_current_user)
):
    """알림 통계 조회"""
    return NotificationService.get_notification_statistics(
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id")
    )

@router.get("/settings",
           response_model=NotificationSettings,
           summary="알림 설정 조회",
           description="사용자의 알림 설정을 조회합니다.")
def get_notification_settings(
    current_user: dict = Depends(get_current_user)
):
    """알림 설정 조회"""
    return NotificationService.get_or_create_notification_settings(
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id")
    )

@router.put("/settings",
           response_model=NotificationSettings,
           summary="알림 설정 업데이트",
           description="""
           알림 설정을 업데이트합니다.
           
           **설정 가능 항목:**
           - 채널별 알림 활성화/비활성화
           - 알림 유형별 설정
           - 할일 마감 알림 시간
           - 방해 금지 시간 설정
           """)
def update_notification_settings(
    settings_update: dict,
    current_user: dict = Depends(get_current_user)
):
    """알림 설정 업데이트"""
    return NotificationService.update_notification_settings(
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id"),
        settings_update=settings_update
    )

# ===== 관리자용 엔드포인트 =====

@router.post("/batch",
           summary="알림 일괄 생성 (관리자용)",
           description="""
           여러 사용자에게 동시에 알림을 발송합니다.
           
           **사용 예시:**
           - 시스템 점검 알림
           - 농장 전체 공지사항
           - 긴급 상황 알림
           """)
def create_batch_notifications(
    batch_data: NotificationBatchRequest,
    current_user: dict = Depends(get_current_user)
):
    """알림 일괄 생성"""
    # 관리자 권한 확인 (향후 구현)
    # if not current_user.get("is_admin"):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="관리자만 일괄 알림을 생성할 수 있습니다"
    #     )
    
    results = []
    for user_id in batch_data.user_ids:
        try:
            notification_data = NotificationCreate(
                user_id=user_id,
                farm_id=batch_data.farm_id,
                notification_type=batch_data.notification_type,
                title=batch_data.title,
                message=batch_data.message,
                priority=NotificationPriority.MEDIUM,
                channels=batch_data.channels,
                related_task_id=batch_data.related_task_id,
                related_cow_id=batch_data.related_cow_id,
                related_record_id=batch_data.related_record_id,
                scheduled_at=batch_data.scheduled_at,
                metadata=batch_data.metadata
            )
            
            notification = NotificationService.create_notification(notification_data)
            results.append({
                "user_id": user_id,
                "success": True,
                "notification_id": notification.id
            })
            
        except Exception as e:
            results.append({
                "user_id": user_id,
                "success": False,
                "error": str(e)
            })
    
    return {
        "success": True,
        "message": f"{len(batch_data.user_ids)}명에게 알림 발송 완료",
        "results": results
    }

@router.post("/test",
           summary="알림 테스트 (개발용)",
           description="알림 시스템을 테스트하기 위한 엔드포인트입니다.")
def test_notification(
    current_user: dict = Depends(get_current_user)
):
    """알림 테스트"""
    test_notification_data = NotificationCreate(
        user_id=current_user.get("id"),
        farm_id=current_user.get("farm_id"),
        notification_type=NotificationType.SYSTEM_MAINTENANCE,
        title="알림 시스템 테스트",
        message="이것은 알림 시스템 테스트 메시지입니다. 정상적으로 작동하고 있습니다!",
        priority=NotificationPriority.MEDIUM,
        channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
        metadata={"test": True}
    )
    
    return NotificationService.create_notification(test_notification_data)

@router.post("/fcm/token",
           summary="FCM 토큰 등록",
           description="사용자의 FCM 토큰을 등록합니다.")
def register_fcm_token(
    fcm_token: str,
    current_user: dict = Depends(get_current_user)
):
    """FCM 토큰 등록"""
    from services.fcm_service import FCMService
    
    success = FCMService.save_user_fcm_token(
        user_id=current_user.get("id"),
        fcm_token=fcm_token
    )
    
    if success:
        return {"success": True, "message": "FCM 토큰이 등록되었습니다"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FCM 토큰 등록에 실패했습니다"
        )

@router.delete("/fcm/token",
             summary="FCM 토큰 삭제",
             description="사용자의 FCM 토큰을 삭제합니다.")
def remove_fcm_token(
    current_user: dict = Depends(get_current_user)
):
    """FCM 토큰 삭제"""
    from services.fcm_service import FCMService
    
    success = FCMService.remove_user_fcm_token(
        user_id=current_user.get("id")
    )
    
    if success:
        return {"success": True, "message": "FCM 토큰이 삭제되었습니다"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FCM 토큰 삭제에 실패했습니다"
        )

@router.post("/fcm/topic/{topic}/subscribe",
           summary="토픽 구독",
           description="특정 토픽에 구독합니다.")
def subscribe_to_topic(
    topic: str,
    current_user: dict = Depends(get_current_user)
):
    """토픽 구독"""
    from services.fcm_service import FCMService
    
    success = FCMService.subscribe_to_topic(
        user_id=current_user.get("id"),
        topic=topic
    )
    
    if success:
        return {"success": True, "message": f"토픽 '{topic}'에 구독되었습니다"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토픽 구독에 실패했습니다"
        )

@router.delete("/fcm/topic/{topic}/unsubscribe",
             summary="토픽 구독 해제",
             description="특정 토픽 구독을 해제합니다.")
def unsubscribe_from_topic(
    topic: str,
    current_user: dict = Depends(get_current_user)
):
    """토픽 구독 해제"""
    from services.fcm_service import FCMService
    
    success = FCMService.unsubscribe_from_topic(
        user_id=current_user.get("id"),
        topic=topic
    )
    
    if success:
        return {"success": True, "message": f"토픽 '{topic}' 구독이 해제되었습니다"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토픽 구독 해제에 실패했습니다"
        ) 