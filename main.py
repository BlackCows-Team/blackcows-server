import os
import warnings
import time
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException
from routers import chatbot_router, cow, record, detailed_record, livestock_trace
from routers import auth_firebase
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from dotenv import load_dotenv
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

# 로깅 설정
# Windows 환경에 맞는 로그 경로 설정
log_dir = os.path.join(os.getcwd(), "logs", "uvicorn")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "access.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Firestore positional arguments 경고 무시
warnings.filterwarnings("ignore", message="Detected filter using positional arguments*")

# .env 파일 로드
load_dotenv()

# JWT 시크릿 키 검증
if not os.getenv("JWT_SECRET_KEY"):
    raise ValueError("JWT_SECRET_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인하세요.")

# 축산물이력제 API 키 검증 (경고만 출력)
if not os.getenv("LIVESTOCK_TRACE_API_DECODING_KEY"):
    print("[WARNING] LIVESTOCK_TRACE_API_DECODING_KEY 환경변수가 설정되지 않았습니다.")
    print("축산물이력제 연동 기능이 제한될 수 있습니다.")



app = FastAPI(
    title="낙농 관리 서버 API",
    version="2.9.0",
    description="낙농 관리 시스템",
)

# CORS 설정 (Flutter 연결을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting을 위한 전역 변수
request_counts = defaultdict(list)
BLOCKED_IPS = set()

# Rate Limiting 및 보안 미들웨어
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    client_ip = request.client.host
    path = request.url.path.lower()
    
    # 차단된 IP 체크
    if client_ip in BLOCKED_IPS:
        logger.warning(f"🚨 Blocked IP access attempt: {client_ip} -> {path}")
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Access denied",
                "message": "현재 귀하의 IP는 과도한 요청으로 인해 일시적으로 제한되었습니다. 서비스 정상 이용을 원하신다면 잠시 후 다시 시도하거나 support@blackcowsdairy.com 으로 문의 주세요."
            }
        )
    
    # Rate Limiting (1분에 50개 요청 제한)
    current_time = time.time()
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < 60]
    
    if len(request_counts[client_ip]) >= 50:
        logger.warning(f"🚨 Rate limit exceeded for IP: {client_ip} -> {path}")
        BLOCKED_IPS.add(client_ip)
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests",
                "message": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
            }
        )
    
    request_counts[client_ip].append(current_time)
    
    # 의심스러운 요청 패턴 감지 (더 강화)
    suspicious_patterns = [
        '.env', 'phpinfo', 'config', 'admin', 'wp-', 
        'laravel', 'debug', 'info.php', 'test', 'backup',
        'sql', 'database', 'mysql', 'phpmyadmin', 'cpanel',
        'wp-admin', 'wp-content', 'wp-includes', 'wordpress'
    ]
    
    if any(pattern in path for pattern in suspicious_patterns):
        logger.warning(f"🚨 Suspicious request from {client_ip}: {path}")
        request_counts[client_ip].append(current_time)  # 추가 카운트
        request_counts[client_ip].append(current_time)  # 더 강한 제재
    
    # 로그 기록 (fail2ban용)
    logger.info(f'{client_ip} - "{request.method} {path} HTTP/{request.scope.get("http_version", "1.1")}" {200 if client_ip not in BLOCKED_IPS else 403}')
    
    return await call_next(request)

# Flutter 모바일 앱 및 CORS 디버깅 미들웨어
@app.middleware("http")
async def handle_mobile_cors(request: Request, call_next):
    """Flutter 모바일 앱 CORS 처리 및 요청 로깅"""
    origin = request.headers.get("origin")
    user_agent = request.headers.get("user-agent", "")
    
    # Flutter 앱 감지 조건 확장
    is_flutter_app = any([
        "flutter" in user_agent.lower(),
        "dart" in user_agent.lower(), 
        "blackcows" in user_agent.lower(),  # 앱 이름 포함시
        origin is None or origin == "null",  # 모바일 앱 특성
    ])
    
    # CORS 요청 로깅 (디버깅용)
    if request.method == "OPTIONS":
        app_type = "Flutter 모바일 앱" if is_flutter_app else "웹 브라우저"
        print(f"[CORS] {app_type} OPTIONS 요청")
        print(f"[CORS] Origin: {origin}")
        print(f"[CORS] User-Agent: {user_agent[:100]}...")
        print(f"[CORS] 요청 경로: {request.url.path}")
    
    response = await call_next(request)
    
    # Flutter 모바일 앱에 대한 CORS 헤더 처리
    if is_flutter_app:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"  # 24시간 캐시
        
        if request.method == "OPTIONS":
            print(f"[CORS] ✅ Flutter 앱 CORS 헤더 적용 완료")
    
    return response

# # cow 라우터 연결
# app.include_router(cow.router, prefix="/cows", tags=["Cows"])

# 라우터 연결
app.include_router(auth_firebase.router, prefix="/auth", tags=["인증"])
from routers import sns_auth
from routers import task
from routers import notification
app.include_router(sns_auth.router, prefix="/sns", tags=["SNS 로그인"])
app.include_router(cow.router, prefix="/cows", tags=["소 관리"])
app.include_router(record.router, prefix="/basic-records", tags=["기본 기록 관리"])
app.include_router(detailed_record.router, prefix="/records", tags=["기록 관리"])
app.include_router(livestock_trace.router, prefix="/api/livestock-trace", tags=["축산물이력조회"])
app.include_router(chatbot_router.router, tags=["Chatbot"])
app.include_router(task.router, prefix="/api/todos", tags=["할일 관리"])
app.include_router(notification.router, prefix="/api/notifications", tags=["알림 관리"]) 


@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "낙농 관리 서버가 정상 작동 중입니다!!!",
        "version": "2.9.0",
        "features": [
            "젖소 기본 관리",
            "축산물이력제 연동 젖소 등록",
            "3단계 젖소 등록 플로우 (축산물이력제 우선, 수동 등록 대안)",
            "기록 관리",
            "상세 기록 관리 (착유, 발정, 인공수정, 임신감정, 분만, 사료급여, 건강검진, 백신접종, 체중측정, 치료)",
            "축산물 이력정보 조회 (축산물품질평가원 API)",
            "할일 관리 (개인/젖소별/농장 전체 할일, 반복 일정, 캘린더 뷰)",
            "알림 시스템 (할일 마감, 지연, 완료, 일일/주간 요약)",
            "통계 및 분석",
            "SNS 로그인 (Google)",
            "AI 챗봇 '소담이'"
        ],
        "new_endpoints": [
            "GET /cows/registration-status/{ear_tag_number} - 젖소 등록 상태 확인",
            "POST /cows/register-from-livestock-trace - 축산물이력제 정보 기반 젖소 등록",
            "POST /cows/manual - 젖소 수동 등록 (기존 POST /cows/ 경로 변경)",
            "GET /cows/{cow_id}/livestock-trace-info - 젖소의 축산물이력제 정보 조회",
            "POST /sns/google/login - 구글 로그인",
            "DELETE /sns/delete-account - SNS 계정 삭제",
            "POST /api/todos - 할일 생성",
            "GET /api/todos - 할일 목록 조회 (필터링 지원)",
            "GET /api/todos/statistics - 할일 통계 조회",
            "GET /api/todos/calendar - 캘린더 뷰 할일 조회",
            "GET /api/todos/today - 오늘 할일 조회",
            "GET /api/todos/overdue - 지연된 할일 조회",
            "PATCH /api/todos/{todo_id}/complete - 할일 완료 처리",
            "POST /api/notifications/create - 알림 생성",
            "GET /api/notifications/ - 알림 목록 조회",
            "GET /api/notifications/unread - 읽지 않은 알림 조회",
            "PATCH /api/notifications/{id}/read - 알림 읽음 처리",
            "PATCH /api/notifications/read-all - 모든 알림 읽음 처리",
            "GET /api/notifications/statistics - 알림 통계 조회",
            "GET /api/notifications/settings - 알림 설정 조회",
            "PUT /api/notifications/settings - 알림 설정 업데이트"
        ],
        "livestock_trace_features": [
            "소 기본 개체정보 (이표번호, 출생일, 품종, 성별, 개월령 자동계산)",
            "농장 등록 이력 (여러 농장 이동 이력 추적)",
            "도축 및 포장 처리 정보",
            "구제역 백신 접종 정보 (최종접종일, 접종차수)",
            "럼피스킨 백신 접종 정보",
            "브루셀라 검사 정보 (검사일, 결과, 경과일 자동계산)",
            "결핵 검사 정보",
            "질병 정보",
            "수입축 정보 (수입국가, 수입경과월)"
        ],
        "task_management_features": [
            "개인/젖소별/농장 전체 할일 분류",
            "우선순위 설정 (낮음/보통/높음/긴급)",
            "카테고리별 관리 (착유, 치료, 백신, 검진, 번식, 사료, 시설관리 등)",
            "반복 일정 설정 (매일/주/월/년)",
            "마감일/시간 설정",
            "할일 상태 관리 (대기중, 진행중, 완료, 취소, 지연)",
            "젖소별 할일 연결",
            "통계 및 완료율 추적",
            "캘린더 뷰 지원",
            "자동 반복 할일 생성"
        ],
        "registration_flow": [
            "1단계: 이표번호 입력 → GET /cows/registration-status/{ear_tag_number}",
            "2단계A: 축산물이력제 조회 성공 → POST /cows/register-from-livestock-trace",
            "2단계B: 축산물이력제 조회 실패 → POST /cows/manual (수동 등록)",
            "3단계: 등록 완료 후 젖소 목록 조회 → GET /cows/"
        ]
    }
@app.get("/health")
def health_status():
    return {"status": "healthy", "version": "2.9.0"}

# 환경변수 확인 함수들

# 토큰 관리 API 엔드포인트들
@app.get("/admin/token-stats", summary="토큰 통계 조회")
def get_token_statistics():
    """리프레시 토큰 통계 조회 (관리자용)"""
    from services.firebase_user_service import FirebaseUserService
    return FirebaseUserService.get_token_statistics()

@app.post("/admin/cleanup-tokens", summary="토큰 정리 실행")
def cleanup_tokens():
    """만료된/오래된 토큰 정리 실행 (관리자용)"""
    from services.firebase_user_service import FirebaseUserService
    return FirebaseUserService.auto_cleanup_tokens()

@app.delete("/admin/revoke-user-tokens/{user_id}", summary="사용자 토큰 무효화")
def revoke_user_tokens(user_id: str):
    """특정 사용자의 모든 토큰 무효화 (관리자용)"""
    from services.firebase_user_service import FirebaseUserService
    revoked_count = FirebaseUserService.revoke_all_user_tokens(user_id)
    return {
        "success": True,
        "message": f"사용자 {user_id}의 토큰 {revoked_count}개가 무효화되었습니다",
        "revoked_count": revoked_count
    }

# 자동 토큰 정리를 위한 스케줄러 설정
def auto_cleanup_tokens_scheduled():
    """스케줄러용 자동 토큰 정리 함수"""
    try:
        from services.firebase_user_service import FirebaseUserService
        result = FirebaseUserService.auto_cleanup_tokens()
        print(f"[SCHEDULER] 자동 토큰 정리 완료: {result}")
    except Exception as e:
        print(f"[SCHEDULER ERROR] 자동 토큰 정리 실패: {str(e)}")

# 알림 스케줄러 함수들
def check_task_due_notifications_scheduled():
    """스케줄러용 할일 마감 임박 알림 체크"""
    try:
        from services.notification_scheduler import NotificationScheduler
        NotificationScheduler.check_task_due_notifications()
        print(f"[SCHEDULER] 할일 마감 임박 알림 체크 완료")
    except Exception as e:
        print(f"[SCHEDULER ERROR] 할일 마감 임박 알림 체크 실패: {str(e)}")

def check_overdue_task_notifications_scheduled():
    """스케줄러용 지연된 할일 알림 체크"""
    try:
        from services.notification_scheduler import NotificationScheduler
        NotificationScheduler.check_overdue_task_notifications()
        print(f"[SCHEDULER] 지연된 할일 알림 체크 완료")
    except Exception as e:
        print(f"[SCHEDULER ERROR] 지연된 할일 알림 체크 실패: {str(e)}")

def check_daily_summary_notifications_scheduled():
    """스케줄러용 일일 요약 알림 체크"""
    try:
        from services.notification_scheduler import NotificationScheduler
        NotificationScheduler.check_daily_summary_notifications()
        print(f"[SCHEDULER] 일일 요약 알림 체크 완료")
    except Exception as e:
        print(f"[SCHEDULER ERROR] 일일 요약 알림 체크 실패: {str(e)}")

def check_weekly_summary_notifications_scheduled():
    """스케줄러용 주간 요약 알림 체크"""
    try:
        from services.notification_scheduler import NotificationScheduler
        NotificationScheduler.check_weekly_summary_notifications()
        print(f"[SCHEDULER] 주간 요약 알림 체크 완료")
    except Exception as e:
        print(f"[SCHEDULER ERROR] 주간 요약 알림 체크 실패: {str(e)}")

def setup_scheduler():
    """스케줄러 설정"""
    scheduler = BackgroundScheduler()
    
    # 토큰 정리 스케줄러
    scheduler.add_job(
        auto_cleanup_tokens_scheduled, 
        CronTrigger(hour=0, minute=0),
        id='token_cleanup',
        name='자동 토큰 정리'
    )
    
    # 알림 스케줄러들
    # 할일 마감 임박 알림 (매 30분마다)
    scheduler.add_job(
        check_task_due_notifications_scheduled,
        CronTrigger(minute="*/30"),
        id='task_due_notifications',
        name='할일 마감 임박 알림'
    )
    
    # 지연된 할일 알림 (매시간)
    scheduler.add_job(
        check_overdue_task_notifications_scheduled,
        CronTrigger(minute=0),
        id='overdue_task_notifications',
        name='지연된 할일 알림'
    )
    
    # 일일 요약 알림 (매일 오전 9시)
    scheduler.add_job(
        check_daily_summary_notifications_scheduled,
        CronTrigger(hour=9, minute=0),
        id='daily_summary_notifications',
        name='일일 요약 알림'
    )
    
    # 주간 요약 알림 (매주 월요일 오전 9시)
    scheduler.add_job(
        check_weekly_summary_notifications_scheduled,
        CronTrigger(day_of_week='mon', hour=9, minute=0),
        id='weekly_summary_notifications',
        name='주간 요약 알림'
    )
    
    scheduler.start()
    print("🕰️ 스케줄러 시작됨:")
    print("   - 자동 토큰 정리 (매일 자정)")
    print("   - 할일 마감 임박 알림 (매 30분)")
    print("   - 지연된 할일 알림 (매시간)")
    print("   - 일일 요약 알림 (매일 오전 9시)")
    print("   - 주간 요약 알림 (매주 월요일 오전 9시)")
    atexit.register(lambda: scheduler.shutdown())

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 실행되는 이벤트"""
    print("🚀 BlackCows 백엔드 서버 시작 중...")
    setup_scheduler()
    print("✅ 서버 초기화 완료!")

@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 실행되는 이벤트"""
    print("🛑 BlackCows 백엔드 서버 종료 중...")
