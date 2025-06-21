import os
from fastapi import FastAPI
from routers import cow, test, record, detailed_record, cow_registration, livestock_trace
from routers import auth_firebase
from fastapi.middleware.cors import CORSMiddleware

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv()

# JWT 시크릿 키 검증
if not os.getenv("JWT_SECRET_KEY"):
    raise ValueError("JWT_SECRET_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인하세요.")

app = FastAPI(
    title="낙농 관리 서버 API",
    version="2.5.0",
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
app.include_router(record.router, prefix="/basic-records", tags=["기본 기록 관리"])
app.include_router(detailed_record.router, prefix="/records", tags=["기록 관리"])
app.include_router(cow_registration.router, prefix="/api/cow-registration", tags=["이표번호로 젖소 등록(축산물이력조회사용)"])
app.include_router(livestock_trace.router, prefix="/api/livestock-trace", tags=["축산물 이력정보 전체 조회"])

@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "낙농 관리 서버가 정상 작동 중입니다!!!",
        "version": "2.5.0",
        "features": [
            "젖소 기본 관리",
            "3단계 젖소 등록 플로우 (축산물이력제 연동)",
            "기록 관리",
            "상세 기록 관리 (착유, 발정, 인공수정, 임신감정, 분만, 사료급여, 건강검진, 백신접종, 체중측정, 치료)",
            "축산물 이력정보 조회 (축산물품질평가원 API)",
            "축산물 이력정보 전체 조회 (모든 이력 정보)",
            "통계 및 분석"
        ],
        "new_endpoints": [
            "POST /cows - 수동 젖소 등록 (일반 젖소 추가 버튼)",
            "POST /cow-registration/check-ear-tag - 이표번호 확인 및 축산물이력제 조회",
            "POST /cow-registration/register-with-trace - 축산물이력제 정보로 젖소 등록",
            "GET /cow-registration/api-status - 축산물이력제 API 상태 확인",
            "POST /livestock-trace/get-full-livestock-trace - 축산물 이력정보 전체 조회 (인증 필요)",
            "POST /livestock-trace/simple-trace - 간단 축산물 이력 조회 (개발/테스트용)",
            "GET /livestock-trace/test-single-option/{ear_tag_number}/{option_no} - 단일 옵션 조회 테스트",
            "GET /livestock-trace/api-status - 축산물이력제 API 상태 확인",
            "POST /livestock-trace/test-mtrace-api - mtrace.go.kr API 테스트 (새로 추가)",
            "GET /livestock-trace/test-mtrace-auth - mtrace.go.kr 인증 정보 확인 (새로 추가)"
        ]
    }
@app.get("/health")
def health_status():
    return {"status": "healthy", "version": "2.5.0"}
