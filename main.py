import os
import warnings
import time
import httpx
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from routers import chatbot_router, cow, record, detailed_record, livestock_trace, sns_auth, task, notification, ai_prediction, auth_firebase
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

# AI 서버 헬스체크 함수
async def check_ai_server_health():
    """AI 서버 헬스체크 수행"""
    ai_server_url = "https://feof-implement-finnish-finally.trycloudflare.com/ai/model-health"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info("🔍 AI 서버 헬스체크 시작...")
            response = await client.get(ai_server_url)
            
            if response.status_code == 200:
                logger.info("✅ AI 서버 연결 성공!")
                logger.info(f"✅ AI 서버 상태: {response.json()}")
                return True
            else:
                logger.warning(f"⚠️ AI 서버 응답 이상: {response.status_code}")
                return False
                
    except httpx.TimeoutException:
        logger.error("❌ AI 서버 연결 시간초과 (30초)")
        return False
    except httpx.ConnectTimeout:
        logger.error("❌ AI 서버 연결 시간초과")
        return False
    except httpx.ReadTimeout:
        logger.error("❌ AI 서버 응답 읽기 시간초과")
        return False
    except Exception as e:
        logger.error(f"❌ AI 서버 헬스체크 실패: {str(e)}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 서버 시작 중...")
    
    # AI 서버 헬스체크 수행
    await check_ai_server_health()
    
    # 스케줄러 설정
    setup_scheduler()
    logger.info("✅ 서버 초기화 완료")
    
    yield
    
    logger.info("🛑 서버 종료 중...")

app = FastAPI(
    title="낙농 관리 서버 API",
    version="3.0.0",
    description="낙농 관리 시스템",
    lifespan=lifespan
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

    # Rate Limiting (1분에 50개 요청 제한) - 로깅만, 차단하지 않음
    current_time = time.time()
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < 60]
    
    if len(request_counts[client_ip]) >= 50:
        logger.warning(f"🚨 Rate limit exceeded for IP (로깅만): {client_ip} -> {path}")
        # 차단하지 않고 로깅만 수행
    
    request_counts[client_ip].append(current_time)
    
# 의심스러운 요청 패턴 감지 (로깅만)
    suspicious_patterns = [
        '.env', 'phpinfo', 'config', 'admin', 'wp-', 
        'laravel', 'debug', 'info.php', 'test', 'backup',
        'sql', 'database', 'mysql', 'phpmyadmin', 'cpanel',
        'wp-admin', 'wp-content', 'wp-includes', 'wordpress',
        'shell', 'cmd', 'exec', 'eval', 'system'
    ]
    if any(pattern in path for pattern in suspicious_patterns):
        logger.warning(f"🚨🚨🚨🚨🚨 의심스러운 요청 감지🚨🚨🚨🚨🚨: {client_ip}: {path}")
        # 추가 로깅만 수행, 차단하지 않음
        request_counts[client_ip].extend([current_time] * 3)
    
    # 로그 기록 (fail2ban용)
    logger.info(f'{client_ip} - "{request.method} {path} HTTP/{request.scope.get("http_version", "1.1")}" 200')
    
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
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"  # 24시간 캐시
        
        if request.method == "OPTIONS":
            print(f"[CORS] ✅ Flutter 앱 CORS 헤더 적용 완료")
    
    return response

# 라우터 연결
app.include_router(auth_firebase.router, prefix="/auth", tags=["인증"])
app.include_router(sns_auth.router, prefix="/sns", tags=["SNS 로그인"])
app.include_router(cow.router, prefix="/cows", tags=["소 관리"])
app.include_router(record.router, prefix="/basic-records", tags=["기본 기록 관리"])
app.include_router(detailed_record.router, prefix="/records", tags=["기록 관리"])
app.include_router(livestock_trace.router, prefix="/api/livestock-trace", tags=["축산물이력조회"])
app.include_router(chatbot_router.router, tags=["Chatbot"])
app.include_router(task.router, prefix="/api/todos", tags=["할일 관리"])
app.include_router(notification.router, prefix="/api/notifications", tags=["알림 관리"]) 
app.include_router(ai_prediction.router, prefix="/api/ai-prediction", tags=["AI 예측"])



@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "낙농 관리 서버가 정상 작동 중입니다!!!",
        "version": "3.0.0",
    }
@app.get("/health")
def health_status():
    return {"status": "healthy", "version": "3.0.0"}

# 환경변수 확인 함수들

# # 토큰 관리 API 엔드포인트들
# @app.get("/admin/token-stats", summary="토큰 통계 조회")
# def get_token_statistics():
#     """리프레시 토큰 통계 조회 (관리자용)"""
#     from services.firebase_user_service import FirebaseUserService
#     return FirebaseUserService.get_token_statistics()

# @app.post("/admin/cleanup-tokens", summary="토큰 정리 실행")
# def cleanup_tokens():
#     """만료된/오래된 토큰 정리 실행 (관리자용)"""
#     from services.firebase_user_service import FirebaseUserService
#     return FirebaseUserService.auto_cleanup_tokens()

# @app.delete("/admin/revoke-user-tokens/{user_id}", summary="사용자 토큰 무효화")
# def revoke_user_tokens(user_id: str):
#     """특정 사용자의 모든 토큰 무효화 (관리자용)"""
#     from services.firebase_user_service import FirebaseUserService
#     revoked_count = FirebaseUserService.revoke_all_user_tokens(user_id)
#     return {
#         "success": True,
#         "message": f"사용자 {user_id}의 토큰 {revoked_count}개가 무효화되었습니다",
#         "revoked_count": revoked_count
#     }

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
        CronTrigger(minute=0),
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
    
        # AI 서버 헬스체크 수행
    await check_ai_server_health()
    
    setup_scheduler()
    print("✅ 서버 초기화 완료!")

@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 실행되는 이벤트"""
    print("🛑 BlackCows 백엔드 서버 종료 중...")
