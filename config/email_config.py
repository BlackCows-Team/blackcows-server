# config/email_config.py

import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from typing import List
from jinja2 import Template

class EmailConfig:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),  # 발송자 이메일
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),  # 앱 비밀번호 (Gmail의 경우)
            MAIL_FROM=os.getenv("MAIL_FROM"),          # 발송자 이메일
            MAIL_PORT=587,                             # Gmail SMTP 포트
            MAIL_SERVER="smtp.gmail.com",              # Gmail SMTP 서버
            MAIL_STARTTLS=True,                        # TLS 사용
            MAIL_SSL_TLS=False,                        # SSL/TLS 사용 안함
            USE_CREDENTIALS=True,                      # 인증 사용
            VALIDATE_CERTS=True                        # 인증서 검증
        )
        
        self.fastmail = FastMail(self.conf)
    
    async def send_password_reset_email(self, email: str, username: str, reset_token: str):
        """비밀번호 재설정 이메일 발송"""
        try:
            # 이메일 HTML 템플릿
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>비밀번호 재설정</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .button { background: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
                    .footer { padding: 20px; font-size: 12px; color: #666; text-align: center; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🐄 낙농 관리 시스템</h1>
                        <p>비밀번호 재설정 요청</p>
                    </div>
                    <div class="content">
                        <h2>안녕하세요, {{ username }}님!</h2>
                        <p>비밀번호 재설정을 요청하셨습니다.</p>
                        
                        <p><strong>재설정 토큰:</strong></p>
                        <div style="background: #fff; padding: 15px; border: 2px solid #4CAF50; font-family: monospace; font-size: 18px; text-align: center; margin: 20px 0;">
                            {{ reset_token }}
                        </div>
                        
                        <p><strong>사용 방법:</strong></p>
                        <ol>
                            <li>낙농 관리 앱을 열어주세요</li>
                            <li>비밀번호 재설정 화면에서 위의 토큰을 입력하세요</li>
                            <li>새로운 비밀번호를 설정하세요</li>
                        </ol>
                        
                        <p><strong>⚠️ 주의사항:</strong></p>
                        <ul>
                            <li>이 토큰은 1시간 동안만 유효합니다</li>
                            <li>토큰 사용 후 즉시 만료됩니다</li>
                            <li>본인이 요청하지 않았다면 이 이메일을 무시하세요</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>이 이메일은 자동으로 발송되었습니다.</p>
                        <p>문의사항이 있으시면 관리자에게 연락해주세요.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 템플릿에 데이터 삽입
            template = Template(html_template)
            html_content = template.render(username=username, reset_token=reset_token)
            
            # 이메일 메시지 생성
            message = MessageSchema(
                subject="🐄 낙농 관리 시스템 - 비밀번호 재설정",
                recipients=[email],
                body=html_content,
                subtype=MessageType.html
            )
            
            # 이메일 발송
            await self.fastmail.send_message(message)
            return True
            
        except Exception as e:
            print(f"[ERROR] 이메일 발송 실패: {str(e)}")
            return False
    
    async def send_welcome_email(self, email: str, username: str):
        """회원가입 환영 이메일 발송"""
        try:
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>회원가입 완료</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .footer { padding: 20px; font-size: 12px; color: #666; text-align: center; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🐄 낙농 관리 시스템</h1>
                        <p>회원가입을 축하합니다!</p>
                    </div>
                    <div class="content">
                        <h2>환영합니다, {{ username }}님!</h2>
                        <p>낙농 관리 시스템에 가입해주셔서 감사합니다.</p>
                        
                        <p><strong>이제 다음 기능들을 사용하실 수 있습니다:</strong></p>
                        <ul>
                            <li>🐄 젖소 기본 관리</li>
                            <li>📝 기록 관리</li>
                            <li>📊 상세 기록 관리 (착유, 발정, 인공수정 등)</li>
                            <li>📈 통계 및 분석</li>
                        </ul>
                        
                        <p>궁금한 점이 있으시면 언제든지 문의해주세요!</p>
                    </div>
                    <div class="footer">
                        <p>낙농 관리 시스템 팀 드림</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            template = Template(html_template)
            html_content = template.render(username=username)
            
            message = MessageSchema(
                subject="🐄 낙농 관리 시스템 - 회원가입 완료",
                recipients=[email],
                body=html_content,
                subtype=MessageType.html
            )
            
            await self.fastmail.send_message(message)
            return True
            
        except Exception as e:
            print(f"[ERROR] 환영 이메일 발송 실패: {str(e)}")
            return False

# 전역 인스턴스
email_config = EmailConfig() 