# services/fcm_service.py

import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Dict, Optional, Any
import logging
from config.firebase_config import get_firestore_client

logger = logging.getLogger(__name__)

class FCMService:
    """Firebase Cloud Messaging 서비스"""
    
    _initialized = False
    
    @classmethod
    def initialize_fcm(cls):
        """FCM 초기화"""
        if not cls._initialized:
            try:
                # 서비스 계정 키 파일로 초기화
                cred = credentials.Certificate("firebase-adminsdk.json")
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                logger.info("FCM 초기화 완료")
            except Exception as e:
                logger.error(f"FCM 초기화 실패: {str(e)}")
                raise
    
    @classmethod
    def send_push_notification(
        cls,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """단일 사용자에게 푸시 알림 발송"""
        try:
            cls.initialize_fcm()
            
            # 사용자의 FCM 토큰 조회
            fcm_token = cls._get_user_fcm_token(user_id)
            if not fcm_token:
                logger.warning(f"사용자 {user_id}의 FCM 토큰이 없습니다")
                return False
            
            # 메시지 생성
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                ),
                data=data or {},
                token=fcm_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#4CAF50',
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            # 메시지 발송
            response = messaging.send(message)
            logger.info(f"푸시 알림 발송 성공: {user_id} - {response}")
            return True
            
        except Exception as e:
            logger.error(f"푸시 알림 발송 실패: {str(e)}")
            return False
    
    @classmethod
    def send_multicast_notification(
        cls,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """다수 사용자에게 푸시 알림 발송"""
        try:
            cls.initialize_fcm()
            
            # FCM 토큰들 조회
            tokens = []
            valid_user_ids = []
            
            for user_id in user_ids:
                token = cls._get_user_fcm_token(user_id)
                if token:
                    tokens.append(token)
                    valid_user_ids.append(user_id)
            
            if not tokens:
                logger.warning("유효한 FCM 토큰이 없습니다")
                return {"success": False, "message": "유효한 FCM 토큰이 없습니다"}
            
            # 멀티캐스트 메시지 생성
            message = messaging.MulticastMessage(
                tokens=tokens,
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                ),
                data=data or {},
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#4CAF50',
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            # 메시지 발송
            response = messaging.send_multicast(message)
            
            # 결과 정리
            success_count = response.success_count
            failure_count = response.failure_count
            
            logger.info(f"멀티캐스트 푸시 알림 발송 완료: 성공 {success_count}, 실패 {failure_count}")
            
            return {
                "success": True,
                "total_sent": len(tokens),
                "success_count": success_count,
                "failure_count": failure_count,
                "user_ids": valid_user_ids
            }
            
        except Exception as e:
            logger.error(f"멀티캐스트 푸시 알림 발송 실패: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @classmethod
    def send_topic_notification(
        cls,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """토픽 구독자들에게 푸시 알림 발송"""
        try:
            cls.initialize_fcm()
            
            # 토픽 메시지 생성
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                ),
                data=data or {},
                topic=topic,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#4CAF50',
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            # 메시지 발송
            response = messaging.send(message)
            logger.info(f"토픽 푸시 알림 발송 성공: {topic} - {response}")
            return True
            
        except Exception as e:
            logger.error(f"토픽 푸시 알림 발송 실패: {str(e)}")
            return False
    
    @classmethod
    def subscribe_to_topic(cls, user_id: str, topic: str) -> bool:
        """사용자를 토픽에 구독"""
        try:
            cls.initialize_fcm()
            
            # 사용자의 FCM 토큰 조회
            fcm_token = cls._get_user_fcm_token(user_id)
            if not fcm_token:
                logger.warning(f"사용자 {user_id}의 FCM 토큰이 없습니다")
                return False
            
            # 토픽 구독
            response = messaging.subscribe_to_topic([fcm_token], topic)
            
            if response.success_count > 0:
                logger.info(f"토픽 구독 성공: {user_id} -> {topic}")
                return True
            else:
                logger.warning(f"토픽 구독 실패: {user_id} -> {topic}")
                return False
                
        except Exception as e:
            logger.error(f"토픽 구독 실패: {str(e)}")
            return False
    
    @classmethod
    def unsubscribe_from_topic(cls, user_id: str, topic: str) -> bool:
        """사용자를 토픽에서 구독 해제"""
        try:
            cls.initialize_fcm()
            
            # 사용자의 FCM 토큰 조회
            fcm_token = cls._get_user_fcm_token(user_id)
            if not fcm_token:
                logger.warning(f"사용자 {user_id}의 FCM 토큰이 없습니다")
                return False
            
            # 토픽 구독 해제
            response = messaging.unsubscribe_from_topic([fcm_token], topic)
            
            if response.success_count > 0:
                logger.info(f"토픽 구독 해제 성공: {user_id} -> {topic}")
                return True
            else:
                logger.warning(f"토픽 구독 해제 실패: {user_id} -> {topic}")
                return False
                
        except Exception as e:
            logger.error(f"토픽 구독 해제 실패: {str(e)}")
            return False
    
    @staticmethod
    def _get_user_fcm_token(user_id: str) -> Optional[str]:
        """사용자의 FCM 토큰 조회"""
        try:
            db = get_firestore_client()
            user_doc = db.collection('users').document(user_id).get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return user_data.get('fcm_token')
            
            return None
            
        except Exception as e:
            logger.error(f"FCM 토큰 조회 실패: {str(e)}")
            return None
    
    @staticmethod
    def save_user_fcm_token(user_id: str, fcm_token: str) -> bool:
        """사용자의 FCM 토큰 저장"""
        try:
            db = get_firestore_client()
            
            db.collection('users').document(user_id).update({
                'fcm_token': fcm_token,
                'fcm_token_updated_at': firebase_admin.firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"FCM 토큰 저장 성공: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"FCM 토큰 저장 실패: {str(e)}")
            return False
    
    @staticmethod
    def remove_user_fcm_token(user_id: str) -> bool:
        """사용자의 FCM 토큰 삭제"""
        try:
            db = get_firestore_client()
            
            db.collection('users').document(user_id).update({
                'fcm_token': None,
                'fcm_token_updated_at': firebase_admin.firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"FCM 토큰 삭제 성공: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"FCM 토큰 삭제 실패: {str(e)}")
            return False 