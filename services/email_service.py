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
import os
import uuid

class EmailService:
    """이메일 발송 서비스 - 구글 워크스페이스 SMTP 사용"""
    
    # SMTP 설정
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    FROM_EMAIL = "noreply@blackcowsdairy.com"
    FROM_NAME = "BlackCows Dairy"
    
    @staticmethod
    def _get_smtp_config():
        """SMTP 설정 가져오기"""
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("FROM_EMAIL", "noreply@blackcowsdairy.com")  # 발신자 표시용
        from_name = os.getenv("FROM_NAME", "BlackCows Dairy")
        
        if not smtp_username:
            raise ValueError("SMTP_USERNAME  환경변수가 설정되지 않았습니다")
        if not smtp_password:
            raise ValueError("SMTP_PASSWORD 환경변수가 설정되지 않았습니다")
        
        return {
            "server": smtp_server,
            "port": smtp_port,
            "username": smtp_username,  # 실제 로그인 계정 (예: admin@blackcowsdairy.com)
            "password": smtp_password,  # 앱 비밀번호
            "from_email": from_email,   # 발신자로 표시될 주소 (예: noreply@blackcowsdairy.com)
            "from_name": from_name      # 발신자 이름
        }
    
    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
        """이메일 발송 (내부 메서드)"""
        try:
            smtp_config = EmailService._get_smtp_config()
            
            # 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{EmailService.FROM_NAME} <{EmailService.FROM_EMAIL}>"
            msg['To'] = to_email
            
            # 텍스트 버전 (HTML에서 태그 제거한 버전)
            if not text_content:
                import re
                text_content = re.sub('<[^<]+?>', '', html_content)
            
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
                server.starttls()
                server.login(smtp_config["username"], smtp_config["password"])
                server.send_message(msg)
            
            print(f"[EMAIL] 이메일 발송 성공: {to_email} - {subject}")
            print(f"[EMAIL] 발신자: {smtp_config['from_email']} (로그인: {smtp_config['username']})")
            return True
            
        except Exception as e:
            print(f"[ERROR] 이메일 발송 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이메일 발송 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def _generate_temporary_password(length: int = 12) -> str:
        """임시 비밀번호 생성"""
        # 대문자, 소문자, 숫자, 특수문자 포함
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # 최소 1개씩 포함되도록 보장
        if not any(c.isupper() for c in password):
            password = password[:-1] + secrets.choice(string.ascii_uppercase)
        if not any(c.isdigit() for c in password):
            password = password[:-1] + secrets.choice(string.digits)
        
        return password
    
    @staticmethod
    def send_welcome_email(user_data: Dict):
        """회원가입 축하 이메일 발송"""
        try:
            subject = f"🐄 BlackCows Dairy에 오신 것을 환영합니다, {user_data['username']}님!"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; }}
                    .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
                    .highlight {{ color: #2E7D32; font-weight: bold; }}
                    .info-box {{ background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #4CAF50; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🐄 BlackCows Dairy</h1>
                        <h2>회원가입을 축하드립니다!</h2>
                    </div>
                    
                    <div class="content">
                        <h3>안녕하세요, <span class="highlight">{user_data['username']}</span>님!</h3>
                        
                        <p>BlackCows Dairy 스마트 낙농 관리 시스템에 가입해 주셔서 진심으로 감사드립니다.</p>
                        
                        <div class="info-box">
                            <h4>📋 가입 정보</h4>
                            <ul>
                                <li><strong>이름:</strong> {user_data['username']}</li>
                                <li><strong>아이디:</strong> {user_data['user_id']}</li>
                                <li><strong>이메일:</strong> {user_data['email']}</li>
                                <li><strong>목장명:</strong> {user_data['farm_nickname']}</li>
                                <li><strong>가입일:</strong> {user_data['created_at'].strftime('%Y년 %m월 %d일')}</li>
                            </ul>
                        </div>
                        
                        <h4>🚀 지금 바로 시작하세요!</h4>
                        <ul>
                            <li>젖소 등록 및 관리</li>
                            <li>착유량, 건강상태 기록</li>
                            <li>번식 관리 및 임신 추적</li>
                            <li>AI 챗봇 '소담이'와 상담</li>
                            <li>할일 관리 및 알림</li>
                        </ul>
                        
                        <p>궁금한 점이 있으시면 언제든지 문의해 주세요.</p>
                        <p><strong>행복한 낙농 라이프 되세요! 🐄💚</strong></p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2025 BlackCows Dairy. All rights reserved.</p>
                        <p>이 이메일은 발신전용입니다.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            EmailService._send_email(user_data['email'], subject, html_content)
            
        except Exception as e:
            print(f"[WARNING] 회원가입 축하 이메일 발송 실패: {str(e)}")
            # 회원가입 자체는 성공하도록 예외를 발생시키지 않음
    
    @staticmethod
    def send_user_id_email(user_data: Dict):
        """아이디 찾기 이메일 발송"""
        try:
            subject = f"🔍 {user_data['username']}님의 BlackCows Dairy 아이디 안내"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1976D2, #42A5F5); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; }}
                    .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
                    .user-id-box {{ background: #E3F2FD; padding: 20px; margin: 20px 0; border-radius: 10px; text-align: center; border: 2px solid #1976D2; }}
                    .user-id {{ font-size: 24px; font-weight: bold; color: #1976D2; font-family: monospace; letter-spacing: 2px; }}
                    .warning {{ background: #FFF3E0; padding: 15px; border-left: 4px solid #FF9800; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔍 아이디 찾기</h1>
                        <h2>요청하신 아이디를 안내드립니다</h2>
                    </div>
                    
                    <div class="content">
                        <h3>안녕하세요, <strong>{user_data['username']}</strong>님!</h3>
                        
                        <p>요청하신 BlackCows Dairy 계정의 아이디를 안내드립니다.</p>
                        
                        <div class="user-id-box">
                            <h4>💡 귀하의 아이디</h4>
                            <div class="user-id">{user_data['user_id']}</div>
                        </div>
                        
                        <div class="warning">
                            <h4>⚠️ 보안 안내</h4>
                            <ul>
                                <li>아이디는 타인에게 공유하지 마세요</li>
                                <li>본인이 요청하지 않았다면 계정 보안을 확인해 주세요</li>
                                <li>정기적으로 비밀번호를 변경해 주세요</li>
                            </ul>
                        </div>
                        
                        <p>로그인에 문제가 있으시면 비밀번호 재설정을 이용해 주세요.</p>
                        <p><strong>안전한 낙농 관리를 위해 계정 보안에 주의해 주세요! 🔒</strong></p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2025 BlackCows Dairy. All rights reserved.</p>
                        <p>발신시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            EmailService._send_email(user_data['email'], subject, html_content)
            
        except Exception as e:
            print(f"[ERROR] 아이디 찾기 이메일 발송 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="아이디 찾기 이메일 발송에 실패했습니다"
            )
    
    @staticmethod
    def send_temporary_password_email(user_data: Dict, temp_password: str, expire_time: datetime):
        """임시 비밀번호 이메일 발송"""
        try:
            expire_minutes = 60  # 1시간
            subject = f"🔐 {user_data['username']}님의 BlackCows Dairy 임시 비밀번호"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #D32F2F, #F44336); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; }}
                    .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
                    .password-box {{ background: #FFEBEE; padding: 20px; margin: 20px 0; border-radius: 10px; text-align: center; border: 2px solid #D32F2F; }}
                    .temp-password {{ font-size: 24px; font-weight: bold; color: #D32F2F; font-family: monospace; letter-spacing: 2px; }}
                    .warning {{ background: #FFF3E0; padding: 15px; border-left: 4px solid #FF9800; margin: 20px 0; }}
                    .urgent {{ background: #FFCDD2; padding: 15px; border-left: 4px solid #D32F2F; margin: 20px 0; }}
                    .steps {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 임시 비밀번호 발급</h1>
                        <h2>비밀번호 재설정을 위한 임시 비밀번호</h2>
                    </div>
                    
                    <div class="content">
                        <h3>안녕하세요, <strong>{user_data['username']}</strong>님!</h3>
                        
                        <p>요청하신 비밀번호 재설정을 위한 임시 비밀번호를 발급해드립니다.</p>
                        
                        <div class="password-box">
                            <h4>🔑 임시 비밀번호</h4>
                            <div class="temp-password">{temp_password}</div>
                        </div>
                        
                        <div class="urgent">
                            <h4>⏰ 중요: 만료 시간</h4>
                            <p><strong>만료 시간: {expire_time.strftime('%Y년 %m월 %d일 %H시 %M분')}</strong></p>
                            <p><strong>남은 시간: {expire_minutes}분</strong></p>
                            <p>시간 내에 반드시 비밀번호를 변경해주세요!</p>
                        </div>
                        
                        <div class="steps">
                            <h4>📝 비밀번호 변경 순서</h4>
                            <ol>
                                <li><strong>앱에 로그인</strong> - 아이디와 위 임시 비밀번호로 로그인</li>
                                <li><strong>비밀번호 변경</strong> - 로그인 즉시 새 비밀번호로 변경</li>
                                <li><strong>변경 완료</strong> - 임시 비밀번호는 자동으로 무효화됩니다</li>
                            </ol>
                        </div>
                        
                        <div class="warning">
                            <h4>⚠️ 보안 주의사항</h4>
                            <ul>
                                <li>임시 비밀번호는 타인에게 절대 공유하지 마세요</li>
                                <li>만료 시간이 지나면 다시 요청해야 합니다</li>
                                <li>본인이 요청하지 않았다면 즉시 문의해 주세요</li>
                                <li>새 비밀번호는 8자 이상, 영문+숫자 조합으로 설정하세요</li>
                            </ul>
                        </div>
                        
                        <p><strong>안전한 계정 관리를 위해 즉시 비밀번호를 변경해 주세요! 🔒</strong></p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2025 BlackCows Dairy. All rights reserved.</p>
                        <p>발신시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            EmailService._send_email(user_data['email'], subject, html_content)
            
        except Exception as e:
            print(f"[ERROR] 임시 비밀번호 이메일 발송 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="임시 비밀번호 이메일 발송에 실패했습니다"
            )
    
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
                "is_active": True
            }
            
            # 기존 임시 비밀번호 무효화
            existing_temps = db.collection('temporary_passwords').where('user_id', '==', user_id).where('is_active', '==', True).get()
            for temp_doc in existing_temps:
                db.collection('temporary_passwords').document(temp_doc.id).update({
                    'is_active': False,
                    'deactivated_at': current_time
                })
            
            # 새 임시 비밀번호 저장
            db.collection('temporary_passwords').document(temp_id).set(temp_password_data)
            
            return temp_id
            
        except Exception as e:
            print(f"[ERROR] 임시 비밀번호 저장 실패: {str(e)}")
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
            
            # 활성 임시 비밀번호 조회
            temp_docs = (db.collection('temporary_passwords')
                        .where('user_id', '==', user_id)
                        .where('is_active', '==', True)
                        .where('is_used', '==', False)
                        .where('expires_at', '>', current_time)
                        .get())
            
            for temp_doc in temp_docs:
                temp_data = temp_doc.to_dict()
                
                # 비밀번호 검증
                if FirebaseUserService.verify_password(temp_password, temp_data['hashed_temp_password']):
                    # 사용 처리
                    db.collection('temporary_passwords').document(temp_doc.id).update({
                        'is_used': True,
                        'used_at': current_time
                    })
                    
                    return temp_data['temp_id']
            
            return None
            
        except Exception as e:
            print(f"[ERROR] 임시 비밀번호 검증 실패: {str(e)}")
            return None
    
    @staticmethod
    def cleanup_expired_temporary_passwords():
        """만료된 임시 비밀번호 정리"""
        try:
            db = get_firestore_client()
            current_time = datetime.utcnow()
            
            # 만료된 임시 비밀번호 조회
            expired_temps = (db.collection('temporary_passwords')
                           .where('expires_at', '<', current_time)
                           .where('is_active', '==', True)
                           .get())
            
            deleted_count = 0
            for temp_doc in expired_temps:
                db.collection('temporary_passwords').document(temp_doc.id).update({
                    'is_active': False,
                    'deactivated_at': current_time,
                    'deactivated_reason': 'expired'
                })
                deleted_count += 1
            
            print(f"[INFO] 만료된 임시 비밀번호 {deleted_count}개 정리 완료")
            return deleted_count
            
        except Exception as e:
            print(f"[ERROR] 임시 비밀번호 정리 실패: {str(e)}")
            return 0