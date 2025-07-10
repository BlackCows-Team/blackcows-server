# templates/email_templates.py

class EmailTemplate:
    """이메일 템플릿 클래스"""
    
    @staticmethod
    def get_base_template():
        """기본 템플릿 구조"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Reset & Base */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #2d3748;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }
        
        /* 소담소담 브랜드 컬러 */
        :root {
            --primary: #48bb78;
            --primary-dark: #38a169;
            --primary-light: #68d391;
            --secondary: #4299e1;
            --accent: #ed8936;
            --success: #48bb78;
            --warning: #ed8936;
            --danger: #f56565;
            --text-primary: #2d3748;
            --text-secondary: #4a5568;
            --text-muted: #718096;
            --bg-white: #ffffff;
            --bg-gray-50: #f7fafc;
            --bg-gray-100: #edf2f7;
            --border: #e2e8f0;
            --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --radius: 16px;
            --radius-sm: 8px;
        }
        
        /* 메인 컨테이너 */
        .email-wrapper {
            padding: 40px 20px;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            min-height: 100vh;
        }
        
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background: var(--bg-white);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border);
        }
        
        /* 헤더 - 소담소담 스타일 */
        .email-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            padding: 50px 40px;
            text-align: center;
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .email-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 2px, transparent 2px),
                radial-gradient(circle at 75% 75%, rgba(255,255,255,0.05) 1px, transparent 1px);
            background-size: 50px 50px, 30px 30px;
            animation: float 30s infinite linear;
        }
        
        @keyframes float {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(-100px, -100px) rotate(360deg); }
        }
        
        .logo {
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 12px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            position: relative;
            z-index: 2;
        }
        
        .header-title {
            font-size: 1.4rem;
            font-weight: 500;
            opacity: 0.95;
            position: relative;
            z-index: 2;
        }
        
        /* 네비게이션 바 */
        .nav-bar {
            background: var(--bg-white);
            padding: 0;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .nav-item {
            padding: 16px 20px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .nav-item:hover {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        
        .nav-item.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        
        /* 컨텐츠 영역 */
        .email-content {
            padding: 50px 40px;
            background: var(--bg-white);
        }
        
        .greeting {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 24px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .highlight {
            color: var(--primary);
            font-weight: 700;
        }
        
        /* 카드 스타일 */
        .info-card {
            background: var(--bg-gray-50);
            border-radius: var(--radius-sm);
            padding: 32px;
            margin: 32px 0;
            border-left: 4px solid var(--primary);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border);
        }
        
        .primary-card {
            background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
            border: 2px solid var(--primary-light);
            border-radius: var(--radius-sm);
            padding: 32px;
            text-align: center;
            margin: 32px 0;
            position: relative;
            overflow: hidden;
        }
        
        .primary-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(72,187,120,0.1) 0%, transparent 70%);
        }
        
        .warning-card {
            background: linear-gradient(135deg, #fffaf0 0%, #fef5e7 100%);
            border: 2px solid var(--warning);
            border-radius: var(--radius-sm);
            padding: 24px;
            margin: 24px 0;
        }
        
        .danger-card {
            background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
            border: 2px solid var(--danger);
            border-radius: var(--radius-sm);
            padding: 24px;
            margin: 24px 0;
        }
        
        /* 특별한 텍스트 스타일 */
        .large-text {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
            letter-spacing: 2px;
            text-shadow: 0 2px 4px rgba(72,187,120,0.2);
            background: var(--bg-white);
            padding: 24px;
            border-radius: var(--radius-sm);
            border: 3px dashed var(--primary-light);
            position: relative;
            z-index: 1;
        }
        
        /* 단계별 안내 */
        .steps-container {
            background: var(--bg-white);
            border-radius: var(--radius-sm);
            padding: 32px;
            margin: 32px 0;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border);
        }
        
        .steps-list {
            list-style: none;
            counter-reset: step-counter;
        }
        
        .steps-list li {
            counter-increment: step-counter;
            margin-bottom: 20px;
            padding-left: 60px;
            position: relative;
            font-size: 1.05rem;
        }
        
        .steps-list li::before {
            content: counter(step-counter);
            position: absolute;
            left: 0;
            top: 2px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1rem;
            box-shadow: var(--shadow-md);
        }
        
        /* 기능 그리드 */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }
        
        .feature-item {
            text-align: center;
            padding: 20px 16px;
            background: var(--bg-white);
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-item::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .feature-item:hover::before {
            transform: scaleX(1);
        }
        
        /* 버튼 */
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            text-decoration: none;
            padding: 16px 32px;
            border-radius: var(--radius-sm);
            font-weight: 600;
            text-align: center;
            margin: 24px 0;
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .cta-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s ease;
        }
        
        .cta-button:hover::before {
            left: 100%;
        }
        
        /* 푸터 */
        .email-footer {
            background: linear-gradient(135deg, var(--text-primary) 0%, #1a202c 100%);
            color: white;
            padding: 40px;
            text-align: center;
            font-size: 0.9rem;
        }
        
        .footer-content {
            margin-bottom: 20px;
            opacity: 0.9;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 24px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .footer-link {
            color: var(--primary-light);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }
        
        .footer-link:hover {
            color: white;
        }
        
        .company-info {
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid rgba(255,255,255,0.1);
            opacity: 0.7;
            font-size: 0.85rem;
        }
        
        /* 반응형 */
        @media only screen and (max-width: 600px) {
            .email-wrapper { padding: 20px 10px; }
            .email-header { padding: 40px 20px; }
            .email-content { padding: 30px 20px; }
            .email-footer { padding: 30px 20px; }
            .logo { font-size: 2.2rem; }
            .header-title { font-size: 1.2rem; }
            .large-text { font-size: 1.5rem; padding: 20px; }
            .features-grid { grid-template-columns: 1fr; }
            .footer-links { flex-direction: column; gap: 12px; }
            .nav-bar { flex-direction: column; }
            .steps-list li { padding-left: 50px; }
            .steps-list li::before { width: 32px; height: 32px; font-size: 0.9rem; }
        }
        
        /* 다크모드 지원 */
        @media (prefers-color-scheme: dark) {
            .email-container { 
                border: 1px solid #4a5568;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            }
        }
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="email-container">
            <div class="email-header">
                <div class="logo">🐄 {brand_name}</div>
                <div class="header-title">{header_title}</div>
            </div>
            
            <div class="nav-bar">
                <a href="https://blackcows-team.github.io/blackcows-privacy/index.html" class="nav-item">프로젝트 소개</a>
                <a href="https://blackcows-team.github.io/blackcows-privacy/index.html#features" class="nav-item">핵심 기능</a>
                <a href="https://blackcows-team.github.io/blackcows-privacy/index.html#team" class="nav-item">팀 소개</a>
                <a href="mailto:support@blackcowsdairy.com" class="nav-item">문의하기</a>
            </div>
            
            <div class="email-content">
                {content}
            </div>
            
            <div class="email-footer">
                <div class="footer-content">
                    © {year} {brand_name}. All rights reserved.
                </div>
                
                <div class="footer-links">
                    <a href="https://blackcows-team.github.io/blackcows-privacy/index.html" class="footer-link">🌐 프로젝트 소개</a>
                    <a href="mailto:support@blackcowsdairy.com" class="footer-link">📧 고객지원</a>
                    <a href="https://blackcows-team.github.io/blackcows-privacy/privacy-policy.html" class="footer-link">🔒 개인정보처리방침</a>
                </div>
                
                <div class="company-info">
                    {footer_info}<br>
                    AI가 함께하는 낙농 젖소 전문 관리 - "소와 나누는 이야기 '소담소담'"
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

    @staticmethod
    def get_welcome_template(user_data):
        """회원가입 환영 템플릿"""
        content = f"""
        <div class="greeting">
            👋 안녕하세요, <span class="highlight">{user_data['username']}</span>님!
        </div>
        
        <p style="margin-bottom: 32px; font-size: 1.15rem; color: var(--text-secondary); line-height: 1.7;">
            <strong>소담소담</strong> 스마트 낙농 관리 시스템에 가입해 주셔서 진심으로 감사드립니다.<br>
            이제 AI가 함께하는 더 효율적이고 스마트한 낙농 관리를 시작해보세요!
        </p>
        
        <div class="info-card">
            <h4 style="margin-bottom: 20px; color: var(--text-primary); font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
                📋 가입 정보 확인
            </h4>
            <div style="display: grid; gap: 12px; font-size: 1.05rem;">
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border);">
                    <strong>이름:</strong> <span>{user_data['username']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border);">
                    <strong>아이디:</strong> <code style="background: var(--bg-gray-100); padding: 4px 8px; border-radius: 4px; font-weight: 600;">{user_data['user_id']}</code>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border);">
                    <strong>이메일:</strong> <span>{user_data['email']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border);">
                    <strong>목장명:</strong> <span style="color: var(--primary); font-weight: 600;">{user_data['farm_nickname']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                    <strong>가입일:</strong> <span>{user_data['created_at'].strftime('%Y년 %m월 %d일')}</span>
                </div>
            </div>
        </div>
        
        <div class="primary-card">
            <h4 style="margin-bottom: 24px; color: var(--primary); font-size: 1.3rem; position: relative; z-index: 2;">
                🚀 지금 바로 시작하세요!
            </h4>
            <div class="features-grid" style="position: relative; z-index: 2;">
                <div class="feature-item">
                    <div style="font-size: 2rem; margin-bottom: 8px;">🐄</div>
                    <div style="font-weight: 600; color: var(--text-primary);">젖소 등록 및 관리</div>
                </div>
                <div class="feature-item">
                    <div style="font-size: 2rem; margin-bottom: 8px;">📊</div>
                    <div style="font-weight: 600; color: var(--text-primary);">착유량, 건강상태 기록</div>
                </div>
                <div class="feature-item">
                    <div style="font-size: 2rem; margin-bottom: 8px;">💕</div>
                    <div style="font-weight: 600; color: var(--text-primary);">번식 관리 및 임신 추적</div>
                </div>
                <div class="feature-item">
                    <div style="font-size: 2rem; margin-bottom: 8px;">🤖</div>
                    <div style="font-weight: 600; color: var(--text-primary);">AI 챗봇 '소담이'와 상담</div>
                </div>
                <div class="feature-item">
                    <div style="font-size: 2rem; margin-bottom: 8px;">📅</div>
                    <div style="font-weight: 600; color: var(--text-primary);">할일 관리 및 알림</div>
                </div>
                <div class="feature-item">
                    <div style="font-size: 2rem; margin-bottom: 8px;">📱</div>
                    <div style="font-weight: 600; color: var(--text-primary);">모바일 기반 직관적 관리</div>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 40px 0; padding: 32px; background: var(--bg-gray-50); border-radius: var(--radius-sm); border: 1px solid var(--border);">
            <h4 style="margin-bottom: 16px; color: var(--text-primary); font-size: 1.2rem;">🔗 바로 시작하기</h4>
            <p style="margin-bottom: 20px; color: var(--text-secondary);">
                궁금한 점이 있으시면 언제든지 <a href="mailto:support@blackcowsdairy.com" style="color: var(--primary); text-decoration: none; font-weight: 600;">support@blackcowsdairy.com</a>으로 문의해 주세요.
            </p>
            <p style="font-size: 1.3rem; font-weight: 700; color: var(--primary); margin-bottom: 8px;">
                행복한 낙농 라이프 되세요! 🐄💚
            </p>
            <p style="font-size: 0.95rem; color: var(--text-muted);">
                "소와 나누는 이야기 '소담소담'"에서 더 스마트한 목장 관리를 경험해보세요.
            </p>
        </div>
        """
        
        return EmailTemplate.get_base_template().format(
            title="소담소담 가입을 환영합니다",
            brand_name="소담소담",
            header_title="회원가입을 축하드립니다! 🎉",
            content=content,
            year="2025",
            footer_info="이 이메일은 발신전용입니다. 문의사항은 support@blackcowsdairy.com으로 연락주세요."
        )

    @staticmethod
    def get_user_id_template(user_data):
        """아이디 찾기 템플릿"""
        content = f"""
        <div class="greeting">
            🔍 안녕하세요, <span class="highlight">{user_data['username']}</span>님!
        </div>
        
        <p style="margin-bottom: 32px; font-size: 1.15rem; color: var(--text-secondary); line-height: 1.7;">
            요청하신 <strong>소담소담</strong> 계정의 아이디를 안전하게 안내드립니다.
        </p>
        
        <div class="primary-card">
            <h4 style="margin-bottom: 24px; color: var(--primary); font-size: 1.3rem; display: flex; align-items: center; justify-content: center; gap: 8px;">
                💡 귀하의 아이디
            </h4>
            <div class="large-text">
                {user_data['user_id']}
            </div>
        </div>
        
        <div class="warning-card">
            <h4 style="margin-bottom: 20px; color: var(--warning); font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
                ⚠️ 보안 안내사항
            </h4>
            <div style="display: grid; gap: 12px; font-size: 1.05rem;">
                <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0;">
                    <span style="color: var(--warning); font-size: 1.2rem;">🔒</span>
                    <span>아이디는 타인에게 절대 공유하지 마세요</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0;">
                    <span style="color: var(--warning); font-size: 1.2rem;">👤</span>
                    <span>본인이 요청하지 않았다면 계정 보안을 즉시 확인해 주세요</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0;">
                    <span style="color: var(--warning); font-size: 1.2rem;">🔄</span>
                    <span>정기적으로 비밀번호를 변경하여 보안을 강화하세요</span>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 40px 0; padding: 32px; background: var(--bg-gray-50); border-radius: var(--radius-sm); border: 1px solid var(--border);">
            <h4 style="margin-bottom: 16px; color: var(--text-primary); font-size: 1.2rem;">🔗 추가 지원</h4>
            <p style="margin-bottom: 16px; color: var(--text-secondary);">
                로그인에 문제가 있으시면 비밀번호 재설정을 이용해 주세요.
            </p>
            <p style="margin-bottom: 20px; color: var(--text-secondary);">
                추가 도움이 필요하시면 <a href="mailto:support@blackcowsdairy.com" style="color: var(--primary); text-decoration: none; font-weight: 600;">support@blackcowsdairy.com</a>으로 문의해 주세요.
            </p>
            <p style="font-size: 1.2rem; font-weight: 600; color: var(--primary);">
                안전한 낙농 관리를 위해 계정 보안에 주의해 주세요! 🔒
            </p>
        </div>
        """
        
        from datetime import datetime
        return EmailTemplate.get_base_template().format(
            title="소담소담 아이디 찾기",
            brand_name="소담소담",
            header_title="아이디 찾기 결과 📧",
            content=content,
            year="2025",
            footer_info=f"발신시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')} | 문의: support@blackcowsdairy.com"
        )

    @staticmethod
    def get_temp_password_template(user_data, temp_password, expire_time):
        """임시 비밀번호 템플릿"""
        expire_minutes = 60
        content = f"""
        <div class="greeting">
            🔐 안녕하세요, <span class="highlight">{user_data['username']}</span>님!
        </div>
        
        <p style="margin-bottom: 32px; font-size: 1.15rem; color: var(--text-secondary); line-height: 1.7;">
            요청하신 <strong>소담소담</strong> 계정의 비밀번호 재설정을 위한 임시 비밀번호를 발급해드립니다.
        </p>
        
        <div class="danger-card" style="text-align: center;">
            <h4 style="margin-bottom: 24px; color: var(--danger); font-size: 1.3rem; display: flex; align-items: center; justify-content: center; gap: 8px;">
                🔑 임시 비밀번호
            </h4>
            <div class="large-text" style="color: var(--danger);">
                {temp_password}
            </div>
        </div>
        
        <div class="danger-card">
            <h4 style="margin-bottom: 20px; color: var(--danger); font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
                ⏰ 중요: 만료 시간
            </h4>
            <div style="text-align: center; background: var(--bg-white); padding: 20px; border-radius: var(--radius-sm); margin: 16px 0; border: 2px dashed var(--danger);">
                <div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 8px; color: var(--danger);">
                    만료 시간: {expire_time.strftime('%Y년 %m월 %d일 %H시 %M분')}
                </div>
                <div style="font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 4px;">
                    남은 시간: <span style="color: var(--danger); font-weight: 600;">{expire_minutes}분</span>
                </div>
                <div style="font-size: 0.95rem; color: var(--text-muted);">
                    시간 내에 반드시 비밀번호를 변경해주세요!
                </div>
            </div>
        </div>
        
        <div class="steps-container">
            <h4 style="margin-bottom: 24px; color: var(--text-primary); font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
                📝 비밀번호 변경 순서
            </h4>
            <ol class="steps-list">
                <li><strong>앱에 로그인</strong> - 아이디와 위 임시 비밀번호로 로그인하세요</li>
                <li><strong>비밀번호 변경</strong> - 로그인 즉시 새로운 비밀번호로 변경하세요</li>
                <li><strong>변경 완료</strong> - 임시 비밀번호는 자동으로 무효화됩니다</li>
            </ol>
        </div>
        
        <div class="warning-card">
            <h4 style="margin-bottom: 20px; color: var(--warning); font-size: 1.2rem;">⚠️ 보안 주의사항</h4>
            <div style="display: grid; gap: 12px; font-size: 1.05rem;">
                <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0;">
                    <span style="color: var(--warning); font-size: 1.2rem;">🔒</span>
                    <span>임시 비밀번호는 타인에게 절대 공유하지 마세요</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0;">
                    <span style="color: var(--warning); font-size: 1.2rem;">⏰</span>
                    <span>만료 시간이 지나면 다시 요청해야 합니다</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0;">
                    <span style="color: var(--warning); font-size: 1.2rem;">👤</span>
                    <span>본인이 요청하지 않았다면 즉시 <a href="mailto:support@blackcowsdairy.com" style="color: var(--warning); text-decoration: none; font-weight: 600;">support@blackcowsdairy.com</a>으로 문의해 주세요</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0;">
                    <span style="color: var(--warning); font-size: 1.2rem;">🔐</span>
                    <span>새 비밀번호는 8자 이상, 영문+숫자+특수문자 조합으로 설정하세요</span>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 40px 0; padding: 32px; background: var(--bg-gray-50); border-radius: var(--radius-sm); border: 1px solid var(--border);">
            <h4 style="margin-bottom: 16px; color: var(--danger); font-size: 1.2rem;">🚨 긴급 조치 필요</h4>
            <p style="font-size: 1.2rem; font-weight: 700; color: var(--danger); margin-bottom: 16px;">
                안전한 계정 관리를 위해 즉시 비밀번호를 변경해 주세요! 🔒
            </p>
            <p style="font-size: 1rem; color: var(--text-secondary);">
                문제가 지속되면 <a href="mailto:support@blackcowsdairy.com" style="color: var(--primary); text-decoration: none; font-weight: 600;">support@blackcowsdairy.com</a>으로 문의해 주세요.
            </p>
        </div>
        """
        
        from datetime import datetime
        return EmailTemplate.get_base_template().format(
            title="소담소담 임시 비밀번호",
            brand_name="소담소담",
            header_title="임시 비밀번호 발급 🔐",
            content=content,
            year="2025",
            footer_info=f"발신시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')} | 문의: support@blackcowsdairy.com"
        )