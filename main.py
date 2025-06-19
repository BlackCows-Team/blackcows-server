import os
from fastapi import FastAPI
from routers import cow, test, record, detailed_record
from routers import auth_firebase, test
from fastapi.middleware.cors import CORSMiddleware

# from routes.livestock_trace import router as livestock_trace_router

# JWT 시크릿 키 검증
if not os.getenv("JWT_SECRET_KEY"):
    raise ValueError("JWT_SECRET_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인하세요.")

# 환경변수를 통해 개발 모드/배포 모드 구분
ENV = os.getenv("ENVIRONMENT", "development")

# 개발 모드일 때만 Swagger UI 활성화
if ENV == "production":
    app = FastAPI(
    title="낙농 관리 서버 API",
    version="2.3.0",
    description="낙농 관리 시스템",
    docs_url=None,          # Swagger UI 비활성화
    redoc_url=None,
    openapi_url=None
    )
    
else:
    app = FastAPI(
    title="낙농 관리 서버 API",
    version="2.3.0",
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

# # cow 라우터 연결
# app.include_router(cow.router, prefix="/cows", tags=["Cows"])

# 라우터 연결
app.include_router(auth_firebase.router, prefix="/auth", tags=["인증"])
app.include_router(cow.router, prefix="/cows", tags=["소 관리"])
app.include_router(record.router, prefix="/records", tags=["기록 관리"])
app.include_router(detailed_record.router, prefix="/detailed-records", tags=["상세 기록 관리"])

# app.include_router(livestock_trace_router, prefix="/api/livestock-trace", tags=["축산물이력조회"])

@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "낙농 관리 서버가 정상 작동 중입니다!!!",
        "version": "2.3.0",
        "features": [
            "젖소 기본 관리",
            "기록 관리",
            "상세 기록 관리 (착유, 발정, 인공수정, 임신감정, 분만, 사료급여, 건강검진, 백신접종, 체중측정, 치료)",
            "통계 및 분석"
        ]
    }

@app.get("/health")
def health_status():
    return {"status": "healthy", "version": "2.3.0"}
