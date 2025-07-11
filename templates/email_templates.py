# templates/email_templates.py

from datetime import datetime, timedelta, timezone

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))

class EmailTemplate:
    """이메일 템플릿 클래스 - 구글 SMTP 사용, 통일된 디자인 템플릿"""
    
    @staticmethod
    def get_base_template():
        """HTML 이메일 베이스 템플릿 반환 - CSS 제거, 인라인 스타일만 사용"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="padding: 0; background: #F9F9F9; font-family: Arial, sans-serif; color: #222;">
  <div style="max-width: 600px; min-width: 320px; background: #F9F9F9; border-radius: 18px; overflow: hidden; padding: 0;">
    <div style="background: linear-gradient(90deg, #2E7E32 0%, #4BAE4F 100%); padding: 44px 48px 28px 48px; text-align: left; border-radius: 18px 18px 0 0;">
      <div style="font-size: 2.1rem; font-weight: 700; color: #fff; letter-spacing: -1px; text-align: left;">🐄 소담소담</div>
      <div style="font-size: 1.35rem; font-weight: 700; color: #fff; text-align: left; letter-spacing: -0.5px;">{header_message}</div>
    </div>
    <div style="padding: 40px 48px 40px 48px; background: #F9F9F9; text-align: left;">{content}</div>
    <div style="background: #333333; color: #fff; padding: 28px 32px 22px 32px; text-align: left; border-radius: 0 0 18px 18px;">
      <div style="font-size: 1.08rem; font-weight: 700; letter-spacing: -0.5px; color: #fff;">{footer_message}</div>
      <div style="font-size: 0.95rem; opacity: 0.93; color: #fff;">© {year} 소담소담. All rights reserved.</div>
      <div style="font-size: 0.9rem; opacity: 0.8; line-height: 1.6; color: #fff;">이 이메일은 발신전용입니다.<br>고객지원: <a href="mailto:support@blackcowsdairy.com" style="color:#fff;text-decoration:underline;">support@blackcowsdairy.com</a></div>
    </div>
  </div>
</body>
</html>"""

    @staticmethod
    def get_welcome_template(user_data):
        current_time = datetime.now(KST)
        
        greeting_html = '<div style="font-size: 1.15rem; font-weight: 700; color: #222; text-align: left;">안녕하세요, <span style="color: #468B49; font-weight: 700;">{}</span>님!</div>'.format(user_data['username'])
        
        desc_html = '<div style="font-size: 1rem; color: #444; text-align: left; font-weight: 400;">소담소담 스마트 낙농 관리 시스템에 가입해 주셔서 진심으로 감사드립니다.</div>'
        
        info_box_html = '''<div style="background: #fff; border-radius: 12px; padding: 28px 28px 18px 28px; text-align: left; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-left: 6px solid #4BAE4F; border-right: 1px solid #E0E0E0; border-top: 1px solid #E0E0E0; border-bottom: 1px solid #E0E0E0; max-width: 100%;">
          <div style="font-size: 1.08rem; font-weight: 700; color: #219653; text-align: left;">가입 정보</div>
          <ul style="padding: 0; list-style: none; text-align: left;">
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">이름</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">아이디</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">이메일</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">목장명</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">가입일</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
          </ul>
        </div>'''.format(
            user_data['username'],
            user_data['user_id'],
            user_data['email'],
            user_data['farm_nickname'],
            user_data['created_at'].strftime('%Y년 %m월 %d일')
        )
        
        feature_html = '''<div style="max-width: 540px; text-align: left;">
          <div style="font-size:1.08rem; font-weight:700; color:#159957;">🚀 지금 바로 시작하세요!</div>
          <ul style="padding-left: 1.2em; color:#222; font-size:1rem; line-height:1.7;">
            <li>젖소 등록 및 관리</li>
            <li>착유량, 건강상태 기록</li>
            <li>번식 관리 및 임신 추적</li>
            <li>AI 챗봇 \'소담이\'와 상담</li>
          </ul>
        </div>'''
        
        footer_html = '<div style="max-width: 540px; text-align: left; color:#666; font-size:0.98rem;">궁금한 점이 있으시면 언제든지 문의해 주세요.</div>'
        
        content = greeting_html + desc_html + info_box_html + feature_html + footer_html
        
        return EmailTemplate.get_base_template().format(
            title="[소담소담] 회원가입을 축하드립니다!",
            header_message="회원가입을 축하드립니다!",
            content=content,
            footer_message="행복한 낙농 라이프 되세요! 🐮💚",
            year="2025"
        )

    @staticmethod
    def get_user_id_template(user_data):
        current_time = datetime.now(KST)
        
        greeting_html = '<div style="font-size: 1.15rem; font-weight: 700; color: #222; text-align: left;">안녕하세요, <span style="color: #468B49; font-weight: 700;">{}</span>님!</div>'.format(user_data['username'])
        
        desc_html = '<div style="font-size: 1rem; color: #444; text-align: left; font-weight: 400;">요청하신 소담소담 계정의 아이디를 안전하게 안내드립니다.<br>아래 정보를 확인하시고 안전하게 로그인해 주세요.</div>'
        
        info_box_html = '''<div style="background: #fff; border-radius: 12px; padding: 28px 28px 18px 28px; text-align: left; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-left: 6px solid #4BAE4F; border-right: 1px solid #E0E0E0; border-top: 1px solid #E0E0E0; border-bottom: 1px solid #E0E0E0; max-width: 100%;">
          <div style="font-size: 1.08rem; font-weight: 700; color: #219653; text-align: left;">아이디 찾기 결과</div>
          <ul style="padding: 0; list-style: none; text-align: left;">
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">이름</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">아이디</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">요청시간</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
          </ul>
        </div>'''.format(
            user_data['username'],
            user_data['user_id'],
            current_time.strftime('%Y년 %m월 %d일 %H시 %M분')
        )
        
        security_html = '''<div style="max-width:540px;text-align:left;">
          <div style="font-size:1.08rem;font-weight:700;color:#219653;">보안 안내사항</div>
          <ul style="padding-left:1.2em;color:#222;font-size:1rem;line-height:1.7;">
            <li>아이디 보안 관리 - 타인에게 공유 금지</li>
            <li>계정 보안 확인 - 본인 요청이 아닌 경우 문의</li>
            <li>정기 비밀번호 변경 - 보안 강화 권장</li>
            <li>고객 지원 - 24시간 문의 가능</li>
          </ul>
        </div>'''
        
        content = greeting_html + desc_html + info_box_html + security_html
        
        return EmailTemplate.get_base_template().format(
            title="[소담소담] 아이디 찾기 결과",
            header_message="요청하신 아이디 안내",
            content=content,
            footer_message="행복한 낙농 라이프 되세요! 🐮💚",
            year="2025"
        )

    @staticmethod
    def get_temp_password_template(user_data, temp_password, expire_time=None):
        current_time = datetime.now(KST)
        if expire_time is None:
            expire_time = current_time + timedelta(minutes=60)
            
        greeting_html = '<div style="font-size: 1.15rem; font-weight: 700; color: #222; text-align: left;">안녕하세요, <span style="color: #468B49; font-weight: 700;">{}</span>님!</div>'.format(user_data['username'])
        
        desc_html = '<div style="font-size: 1rem; color: #444; text-align: left; font-weight: 400;">요청하신 소담소담 계정의 임시 비밀번호를 안내드립니다.<br>아래 정보를 확인하시고 60분 이내에 비밀번호를 변경해 주세요.</div>'
        
        info_box_html = '''<div style="background: #fff; border-radius: 12px; padding: 28px 28px 18px 28px; text-align: left; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-left: 6px solid #4BAE4F; border-right: 1px solid #E0E0E0; border-top: 1px solid #E0E0E0; border-bottom: 1px solid #E0E0E0; max-width: 100%;">
          <div style="font-size: 1.08rem; font-weight: 700; color: #219653; text-align: left;">임시 비밀번호 정보</div>
          <ul style="padding: 0; list-style: none; text-align: left;">
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">이름</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">임시 비밀번호</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">만료 시간</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{} (KST)</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">발급 시간</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{} (KST)</span></li>
          </ul>
        </div>'''.format(
            user_data['username'],
            temp_password,
            expire_time.strftime('%Y년 %m월 %d일 %H시 %M분'),
            current_time.strftime('%Y년 %m월 %d일 %H시 %M분')
        )
        
        steps_html = '''<div style="max-width:540px;text-align:left;">
          <div style="font-size:1.08rem;font-weight:700;color:#219653;">📝 비밀번호 변경 순서</div>
          <ul style="padding-left:1.2em;color:#222;font-size:1rem;line-height:1.7;">
            <li>앱에 로그인 - 아이디와 위 임시 비밀번호로 로그인하세요</li>
            <li>비밀번호 변경 - 로그인 즉시 새로운 비밀번호로 변경하세요</li>
            <li>변경 완료 - 임시 비밀번호는 자동으로 무효화됩니다</li>
          </ul>
        </div>'''
        
        security_html = '''<div style="max-width:540px;text-align:left;">
          <div style="font-size:1.08rem;font-weight:700;color:#219653;">보안 주의사항</div>
          <ul style="padding-left:1.2em;color:#222;font-size:1rem;line-height:1.7;">
            <li>비밀번호 보안 - 타인 공유 절대 금지</li>
            <li>만료 시간 확인 - 60분 내 변경 필수</li>
            <li>본인 확인 - 요청하지 않은 경우 즉시 문의</li>
            <li>강력한 비밀번호 - 영문+숫자+특수문자 조합</li>
          </ul>
        </div>'''
        
        contact_html = '''<div style="max-width:540px;text-align:left;color:#666;font-size:0.98rem;">
          문제가 지속되면<br>support@blackcowsdairy.com으로 문의해 주세요.<br><b>안전한 계정 관리를 위해 즉시<br>비밀번호를 변경해 주세요.</b>
        </div>'''
        
        content = greeting_html + desc_html + info_box_html + steps_html + security_html + contact_html
        
        return EmailTemplate.get_base_template().format(
            title="[소담소담] 임시 비밀번호 발급",
            header_message="임시 비밀번호 발급 안내",
            content=content,
            footer_message="안전한 계정 관리를 위해 즉시 비밀번호를 변경해 주세요.",
            year="2025"
        )

    @staticmethod
    def get_password_changed_template(user_data):
        current_time = datetime.now(KST)
        
        greeting_html = '<div style="font-size: 1.15rem; font-weight: 700; color: #222; text-align: left;">안녕하세요, <span style="color: #468B49; font-weight: 700;">{}</span>님!</div>'.format(user_data['username'])
        
        desc_html = '<div style="font-size: 1rem; color: #444; text-align: left; font-weight: 400;">소담소담 계정의 비밀번호가 성공적으로 변경되었습니다.</div>'
        
        info_box_html = '''<div style="background: #fff; border-radius: 12px; padding: 28px 28px 18px 28px; text-align: left; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-left: 6px solid #4BAE4F; border-right: 1px solid #E0E0E0; border-top: 1px solid #E0E0E0; border-bottom: 1px solid #E0E0E0; max-width: 100%;">
          <div style="font-size: 1.08rem; font-weight: 700; color: #219653; text-align: left;">비밀번호 변경 정보</div>
          <ul style="padding: 0; list-style: none; text-align: left;">
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">이름</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">변경 시간</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
          </ul>
        </div>'''.format(
            user_data['username'],
            current_time.strftime('%Y년 %m월 %d일 %H시 %M분')
        )
        
        security_html = '''<div style="max-width: 540px; text-align: left;">
          <div style="font-size:1.08rem; font-weight:700; color:#219653;">보안 안내사항</div>
          <ul style="padding-left: 1.2em; color:#222; font-size:1rem; line-height:1.7;">
            <li>본인이 변경하지 않았다면 즉시 고객지원에 연락하여 계정 보안 점검을 받으세요.</li>
            <li>정기적으로 비밀번호를 변경해 주세요.</li>
          </ul>
        </div>'''
        
        content = greeting_html + desc_html + info_box_html + security_html
        
        return EmailTemplate.get_base_template().format(
            title="[소담소담] 비밀번호 변경 완료",
            header_message="비밀번호 변경 완료 안내",
            content=content,
            footer_message="정기적으로 비밀번호를 변경해 주세요.",
            year="2025"
        )

    @staticmethod
    def get_login_alert_template(user_data, login_info):
        current_time = datetime.now(KST)
        
        greeting_html = '<div style="font-size: 1.15rem; font-weight: 700; color: #222; text-align: left;">안녕하세요, <span style="color: #468B49; font-weight: 700;">{}</span>님!</div>'.format(user_data['username'])
        
        desc_html = '<div style="font-size: 1rem; color: #444; text-align: left; font-weight: 400;">소담소담 계정에 새로운 로그인이 감지되었습니다.<br>아래 로그인 정보를 확인해 주세요.</div>'
        
        info_box_html = '''<div style="background: #fff; border-radius: 12px; padding: 28px 28px 18px 28px; text-align: left; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-left: 6px solid #4BAE4F; border-right: 1px solid #E0E0E0; border-top: 1px solid #E0E0E0; border-bottom: 1px solid #E0E0E0; max-width: 100%;">
          <div style="font-size: 1.08rem; font-weight: 700; color: #219653; text-align: left;">로그인 정보</div>
          <ul style="padding: 0; list-style: none; text-align: left;">
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">이름</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">시간</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">IP 주소</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">디바이스</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
            <li style="font-size: 1rem; color: #222; font-weight: 400; display: flex; align-items: baseline;"><span style="font-weight: 700; min-width: 70px; color: #222; display: inline-block;">위치</span><span style="font-weight: 400; color: #222; flex: 1; word-break: break-all;">{}</span></li>
          </ul>
        </div>'''.format(
            user_data['username'],
            login_info.get('timestamp', current_time.strftime('%Y년 %m월 %d일 %H시 %M분')),
            login_info.get('ip_address', '알 수 없음'),
            login_info.get('device', '알 수 없음'),
            login_info.get('location', '알 수 없음')
        )
        
        content = greeting_html + desc_html + info_box_html
        
        return EmailTemplate.get_base_template().format(
            title="[소담소담] 로그인 알림",
            header_message="새로운 로그인 감지 안내",
            content=content,
            footer_message="계정 보안을 위해 비밀번호를 주기적으로 변경해 주세요.",
            year="2025"
        )