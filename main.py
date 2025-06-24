import os
import warnings
from fastapi import FastAPI
from routers import cow, record, detailed_record, livestock_trace, chatbot
from routers import auth_firebase
from fastapi.middleware.cors import CORSMiddleware

# Firestore positional arguments 경고 무시
warnings.filterwarnings("ignore", message="Detected filter using positional arguments*")

# .env 파일 로드
from dotenv import load_dotenv
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
    version="2.7.0",
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
app.include_router(livestock_trace.router, prefix="/api/livestock-trace", tags=["축산물이력조회"])
app.include_router(chatbot.router, tags=["Chatbot"])


@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "낙농 관리 서버가 정상 작동 중입니다!!!",
        "version": "2.7.0",
        "features": [
            "젖소 기본 관리",
            "축산물이력제 연동 젖소 등록",
            "3단계 젖소 등록 플로우 (축산물이력제 우선, 수동 등록 대안)",
            "기록 관리",
            "상세 기록 관리 (착유, 발정, 인공수정, 임신감정, 분만, 사료급여, 건강검진, 백신접종, 체중측정, 치료)",
            "축산물 이력정보 조회 (축산물품질평가원 API)",
            "통계 및 분석"
        ],
        "new_endpoints": [
            "GET /cows/registration-status/{ear_tag_number} - 젖소 등록 상태 확인",
            "POST /cows/register-from-livestock-trace - 축산물이력제 정보 기반 젖소 등록",
            "POST /cows/manual - 젖소 수동 등록 (기존 POST /cows/ 경로 변경)",
            "GET /cows/{cow_id}/livestock-trace-info - 젖소의 축산물이력제 정보 조회"
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
        "registration_flow": [
            "1단계: 이표번호 입력 → GET /cows/registration-status/{ear_tag_number}",
            "2단계A: 축산물이력제 조회 성공 → POST /cows/register-from-livestock-trace",
            "2단계B: 축산물이력제 조회 실패 → POST /cows/manual (수동 등록)",
            "3단계: 등록 완료 후 젖소 목록 조회 → GET /cows/"
        ]
    }
@app.get("/health")
def health_status():
    return {"status": "healthy", "version": "2.7.0"}
