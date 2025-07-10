# services/email_service.py

import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
from templates.email_templates import EmailTemplate
import os
import uuid

class EmailService:
    """이메일 발송 서비스 - 구글 SMTP 사용, HTML 템플릿 적용"""
    
    # SMTP 설정
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    FROM_EMAIL = "noreply@blackcowsdairy.com"
    FROM_NAME = "소담소담"
    
    @staticmethod
    def _get_smtp_config():
        """SMTP 설정 가져오기"""
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("FROM_EMAIL", "noreply@blackcowsdairy.com")
        from_name = os.getenv("FROM_NAME", "소담소담")
        
        if not smtp_username:
            raise ValueError("SMTP_USERNAME 환경변수가 설정되지 않았습니다")
        if not smtp_password:
            raise ValueError("SMTP_PASSWORD 환경변수가 설정되지 않았습니다")
        
        return {
            "server": smtp_server,
            "port": smtp_port,
            "username": smtp_username,
            "password": smtp_password,
            "from_email": from_email,
            "from_name": from_name
        }
    
    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
        """이메일 발송 (내부 메서드)"""
        try:
            smtp_config = EmailService._get_smtp_config()
            
            # 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
            msg['To'] = to_email
            
            # 이메일 헤더 추가
            msg['Message-ID'] = f"<{uuid.uuid4()}@blackcowsdairy.com>"
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            msg['X-Mailer'] = '소담소담 Email Service v2.0'
            msg['X-Priority'] = '1'
            
            # 텍스트 버전 자동 생성
            if not text_content:
                import re
                text_content = re.sub('<[^<]+?>', '', html_content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # 이메일 파트 생성
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
                server.starttls()
                server.login(smtp_config["username"], smtp_config["password"])
                
                # 수신자 검증
                try:
                    server.verify(to_email)
                except smtplib.SMTPException:
                    print(f"[WARNING] 수신자 주소 검증 실패: {to_email}")
                
                server.send_message(msg)
            
            print(f"[EMAIL] ✅ 이메일 발송 성공: {to_email}")
            print(f"[EMAIL] 📧 제목: {subject}")
            print(f"[EMAIL] 👤 발신자: {smtp_config['from_email']}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"[ERROR] 🔐 SMTP 인증 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="이메일 발송 인증에 실패했습니다. 관리자에게 문의하세요."
            )
        except smtplib.SMTPRecipientsRefused as e:
            print(f"[ERROR] 📧 수신자 주소 거부: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 이메일 주소입니다."
            )
        except Exception as e:
            print(f"[ERROR] ❌ 이메일 발송 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이메일 발송 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def _generate_temporary_password(length: int = 12) -> str:
        """강화된 임시 비밀번호 생성"""
    @staticmethod
    def _generate_temporary_password(length: int = 12) -> str:
        """강화된 임시 비밀번호 생성"""
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = "!@#$%^&*"
        
        # 최소 1개씩 포함 보장
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # 나머지 길이만큼 랜덤 문자 추가
        all_chars = uppercase + lowercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # 순서 섞기
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    @staticmethod
    def send_welcome_email(user_data: Dict):
        """회원가입 축하 이메일 발송"""
        try:
            subject = f"🐄 소담소담에 오신 것을 환영합니다, {user_data['username']}님!"
            html_content = EmailTemplate.get_welcome_template(user_data)
            EmailService._send_email(user_data['email'], subject, html_content)
            print(f"[EMAIL] 🎉 회원가입 환영 이메일 발송 완료: {user_data['email']}")
            
        except Exception as e:
            print(f"[WARNING] ⚠️ 회원가입 축하 이메일 발송 실패: {str(e)}")
    
    @staticmethod
    def send_user_id_email(user_data: Dict):
        """아이디 찾기 이메일 발송"""
        try:
            subject = f"🔍 {user_data['username']}님의 소담소담 아이디 안내"
            html_content = EmailTemplate.get_user_id_template(user_data)
            EmailService._send_email(user_data['email'], subject, html_content)
            print(f"[EMAIL] 🔍 아이디 찾기 이메일 발송 완료: {user_data['email']}")
            
        except Exception as e:
            print(f"[ERROR] ❌ 아이디 찾기 이메일 발송 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="아이디 찾기 이메일 발송에 실패했습니다"
            )
    
    @staticmethod
    def send_temporary_password_email(user_data: Dict, temp_password: str, expire_time: datetime):
        """임시 비밀번호 이메일 발송"""
        try:
            subject = f"🔐 {user_data['username']}님의 소담소담 임시 비밀번호"
            html_content = EmailTemplate.get_temp_password_template(user_data, temp_password, expire_time)
            EmailService._send_email(user_data['email'], subject, html_content)
            print(f"[EMAIL] 🔐 임시 비밀번호 이메일 발송 완료: {user_data['email']}")
            
        except Exception as e:
            print(f"[ERROR] ❌ 임시 비밀번호 이메일 발송 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="임시 비밀번호 이메일 발송에 실패했습니다"
            )
    
    @staticmethod
    def send_password_changed_notification(user_data: Dict):
        """비밀번호 변경 완료 알림 이메일"""
        try:
            subject = f"🔒 {user_data['username']}님의 비밀번호가 변경되었습니다"
            
            content = f"""
            <div class="greeting">
                안녕하세요, <span class="highlight">{user_data['username']}</span>님! 🔒
            </div>
            
            <p style="margin-bottom: 25px; font-size: 1.1rem; color: var(--text-secondary);">
                귀하의 소담소담 계정 비밀번호가 성공적으로 변경되었습니다.
            </p>
            
            <div class="info-card" style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-color: var(--success);">
                <h4 style="margin-bottom: 15px; color: var(--success);">✅ 변경 완료</h4>
                <div style="text-align: left;">
                    <div style="margin: 8px 0;"><strong>변경 시간:</strong> {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}</div>
                    <div style="margin: 8px 0;"><strong>계정:</strong> {user_data['user_id']}</div>
                    <div style="margin: 8px 0;"><strong>이메일:</strong> {user_data['email']}</div>
                </div>
            </div>
            
            <div class="warning-box">
                <h4 style="margin-bottom: 15px; color: var(--warning);">⚠️ 본인이 변경하지 않았다면?</h4>
                <p style="text-align: center; margin: 10px 0;">
                    즉시 <a href="mailto:support@blackcowsdairy.com" style="color: var(--warning); text-decoration: none; font-weight: 600;">support@blackcowsdairy.com</a>으로 연락하여 계정 보안 점검을 받으세요.
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 1.1rem; font-weight: 600; color: var(--success);">
                    안전한 계정 관리를 위해 주기적으로 비밀번호를 변경해 주세요! 🛡️
                </p>
            </div>
            """
            
            html_content = EmailTemplate.get_base_template().format(
                title="소담소담 비밀번호 변경 완료",
                brand_name="소담소담",
                header_title="비밀번호 변경 완료 ✅",
                content=content,
                year="2025",
                footer_info=f"발신시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')} | 문의: support@blackcowsdairy.com"
            )
            
            EmailService._send_email(user_data['email'], subject, html_content)
            print(f"[EMAIL] 🔒 비밀번호 변경 알림 이메일 발송 완료: {user_data['email']}")
            
        except Exception as e:
            print(f"[WARNING] ⚠️ 비밀번호 변경 알림 이메일 발송 실패: {str(e)}")
    
    @staticmethod
    def send_login_alert_email(user_data: Dict, login_info: Dict):
        """의심스러운 로그인 감지 알림"""
        try:
            subject = f"🚨 {user_data['username']}님 계정에 새로운 로그인이 감지되었습니다"
            
            content = f"""
            <div class="greeting">
                안녕하세요, <span class="highlight">{user_data['username']}</span>님! 🚨
            </div>
            
            <p style="margin-bottom: 25px; font-size: 1.1rem; color: var(--text-secondary);">
                귀하의 소담소담 계정에 새로운 로그인이 감지되었습니다.
            </p>
            
            <div class="danger-box">
                <h4 style="margin-bottom: 15px; color: var(--danger);">🔍 로그인 정보</h4>
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: left;">
                    <div style="margin: 8px 0;"><strong>시간:</strong> {login_info.get('timestamp', datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분'))}</div>
                    <div style="margin: 8px 0;"><strong>IP 주소:</strong> {login_info.get('ip_address', '알 수 없음')}</div>
                    <div style="margin: 8px 0;"><strong>디바이스:</strong> {login_info.get('device', '알 수 없음')}</div>
                    <div style="margin: 8px 0;"><strong>위치:</strong> {login_info.get('location', '알 수 없음')}</div>
                </div>
            </div>
            
            <div class="warning-box">
                <h4 style="margin-bottom: 15px; color: var(--warning);">⚠️ 본인의 로그인이 아니라면?</h4>
                <div style="text-align: left;">
                    <div style="margin: 8px 0;">1. 즉시 비밀번호를 변경하세요</div>
                    <div style="margin: 8px 0;">2. 다른 기기에서 로그아웃하세요</div>
                    <div style="margin: 8px 0;">3. <a href="mailto:support@blackcowsdairy.com" style="color: var(--warning); text-decoration: none; font-weight: 600;">support@blackcowsdairy.com</a>으로 신고하세요</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 1.1rem; font-weight: 600; color: var(--danger);">
                    계정 보안을 위해 정기적으로 비밀번호를 변경해 주세요! 🛡️
                </p>
            </div>
            """
            
            html_content = EmailTemplate.get_base_template().format(
                title="소담소담 로그인 알림",
                brand_name="소담소담",
                header_title="새로운 로그인 감지 🚨",
                content=content,
                year="2025",
                footer_info=f"발신시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')} | 문의: support@blackcowsdairy.com"
            )
            
            EmailService._send_email(user_data['email'], subject, html_content)
            print(f"[EMAIL] 🚨 로그인 알림 이메일 발송 완료: {user_data['email']}")
            
        except Exception as e:
            print(f"[WARNING] ⚠️ 로그인 알림 이메일 발송 실패: {str(e)}")
    
    @staticmethod
    def store_temporary_password(user_id: str, temp_password: str, expire_minutes: int = 60) -> str:
        """임시 비밀번호를 Firestore에 저장"""
        try:
            from services.firebase_user_service import FirebaseUserService
            
            db = get_firestore_client()
            temp_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            expire_time = current_time + timedelta(minutes=expire_minutes)
            
            # 임시 비밀번호 해시화
            hashed_temp_password = FirebaseUserService.get_password_hash(temp_password)
            
            temp_password_data = {
                "temp_id": temp_id,
                "user_id": user_id,
                "hashed_temp_password": hashed_temp_password,
                "created_at": current_time,
                "expires_at": expire_time,
                "is_used": False,
                "is_active": True,
                "attempt_count": 0,
                "max_attempts": 5
            }
            
            # 기존 임시 비밀번호 무효화
            existing_temps = db.collection('temporary_passwords').where('user_id', '==', user_id).where('is_active', '==', True).get()
            for temp_doc in existing_temps:
                db.collection('temporary_passwords').document(temp_doc.id).update({
                    'is_active': False,
                    'deactivated_at': current_time,
                    'deactivated_reason': 'new_request'
                })
            
            # 새 임시 비밀번호 저장
            db.collection('temporary_passwords').document(temp_id).set(temp_password_data)
            
            print(f"[EMAIL] 💾 임시 비밀번호 저장 완료: {user_id} (만료: {expire_time})")
            return temp_id
            
        except Exception as e:
            print(f"[ERROR] ❌ 임시 비밀번호 저장 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="임시 비밀번호 저장에 실패했습니다"
            )
    
    @staticmethod
    def verify_temporary_password(user_id: str, temp_password: str) -> Optional[str]:
        """임시 비밀번호 검증"""
        try:
            from services.firebase_user_service import FirebaseUserService
            
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 단순화된 쿼리: user_id만으로 조회 후 메모리에서 필터링
            temp_docs = (db.collection('temporary_passwords')
                        .where('user_id', '==', user_id)
                        .get())
            
            for temp_doc in temp_docs:
                temp_data = temp_doc.to_dict()
                
                # 메모리에서 조건 확인
                if not temp_data.get('is_active', False):
                    continue
                if temp_data.get('is_used', False):
                    continue
                if temp_data.get('expires_at') <= current_time:
                    continue
                
                # 시도 횟수 확인
                if temp_data.get('attempt_count', 0) >= temp_data.get('max_attempts', 5):
                    # 최대 시도 횟수 초과 - 무효화
                    db.collection('temporary_passwords').document(temp_doc.id).update({
                        'is_active': False,
                        'deactivated_at': current_time,
                        'deactivated_reason': 'max_attempts_exceeded'
                    })
                    continue
                
                # 시도 횟수 증가
                db.collection('temporary_passwords').document(temp_doc.id).update({
                    'attempt_count': temp_data.get('attempt_count', 0) + 1,
                    'last_attempt_at': current_time
                })
                
                # 비밀번호 검증
                if FirebaseUserService.verify_password(temp_password, temp_data['hashed_temp_password']):
                    # 사용 처리
                    db.collection('temporary_passwords').document(temp_doc.id).update({
                        'is_used': True,
                        'used_at': current_time
                    })
                    
                    print(f"[EMAIL] ✅ 임시 비밀번호 검증 성공: {user_id}")
                    return temp_data['temp_id']
            
            print(f"[EMAIL] ❌ 임시 비밀번호 검증 실패: {user_id}")
            return None
            
        except Exception as e:
            print(f"[ERROR] ❌ 임시 비밀번호 검증 실패: {str(e)}")
            return None
    
    @staticmethod
    def cleanup_expired_temporary_passwords():
        """만료된 임시 비밀번호 정리"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 모든 임시 비밀번호 조회 후 메모리에서 필터링
            all_temps = db.collection('temporary_passwords').get()
            
            deleted_count = 0
            for temp_doc in all_temps:
                temp_data = temp_doc.to_dict()
                
                # 만료된 활성 임시 비밀번호 비활성화
                if (temp_data.get('is_active', False) and 
                    temp_data.get('expires_at') and 
                    temp_data.get('expires_at') < current_time):
                    db.collection('temporary_passwords').document(temp_doc.id).update({
                        'is_active': False,
                        'deactivated_at': current_time,
                        'deactivated_reason': 'expired'
                    })
                    deleted_count += 1
            
            # 7일 이상 된 사용완료/비활성 레코드 삭제
            old_cutoff = current_time - timedelta(days=7)
            removed_count = 0
            for temp_doc in all_temps:
                temp_data = temp_doc.to_dict()
                
                if (not temp_data.get('is_active', True) and 
                    temp_data.get('deactivated_at') and 
                    temp_data.get('deactivated_at') < old_cutoff):
                    db.collection('temporary_passwords').document(temp_doc.id).delete()
                    removed_count += 1
            
            print(f"[EMAIL] 🧹 임시 비밀번호 정리 완료 - 비활성화: {deleted_count}개, 삭제: {removed_count}개")
            return {"deactivated": deleted_count, "deleted": removed_count}
            
        except Exception as e:
            print(f"[ERROR] ❌ 임시 비밀번호 정리 실패: {str(e)}")
            return {"deactivated": 0, "deleted": 0}

    @staticmethod
    def get_email_analytics():
        """이메일 발송 통계 조회"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            analytics = {
                "today_sent": 0,
                "active_temp_passwords": 0,
                "expired_temp_passwords": 0,
                "last_cleanup": None
            }
            
            # 모든 임시 비밀번호 조회 후 메모리에서 필터링
            all_temps = db.collection('temporary_passwords').get()
            
            active_count = 0
            expired_count = 0
            
            for temp_doc in all_temps:
                temp_data = temp_doc.to_dict()
                
                if temp_data.get('is_active', False):
                    active_count += 1
                    
                    # 만료된 활성 임시 비밀번호
                    if (temp_data.get('expires_at') and 
                        temp_data.get('expires_at') < current_time):
                        expired_count += 1
            
            analytics["active_temp_passwords"] = active_count
            analytics["expired_temp_passwords"] = expired_count
            
            return analytics
            
        except Exception as e:
            print(f"[ERROR] ❌ 이메일 통계 조회 실패: {str(e)}")
            return None