import os
import warnings
from fastapi import FastAPI
from routers import cow, record, detailed_record, livestock_trace, chatbot_router, ai_prediction
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
    version="2.8.0",
    description="AI 기반 낙농 관리 시스템",
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
app.include_router(chatbot_router.router, tags=["Chatbot"])
app.include_router(ai_prediction.router, prefix="/ai", tags=["AI 예측"]) 


@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "AI기반 낙농 관리 서버가 정상 작동 중입니다!!!",
        "version": "3.0.0",
        "features": [
            "젖소 기본 관리",
            "축산물이력제 연동 젖소 등록",
            "3단계 젖소 등록 플로우 (축산물이력제 우선, 수동 등록 대안)",
            "기록 관리",
            "상세 기록 관리 (착유, 발정, 인공수정, 임신감정, 분만, 사료급여, 건강검진, 백신접종, 체중측정, 치료)",
            "축산물 이력정보 조회 (축산물품질평가원 API)",
            "통계 및 분석",
            "AI 질병 예측 (유방염, 대사성질환, 럼피스킨병, 소화기질환)",
            "AI 번식 성공률 예측 및 최적 수정시기 안내",
            "AI 분만 예정일 예측",
            "AI 사료 효율 분석 및 최적화",
            "AI 유성분 품질 예측",
            "AI 초산우 성장 잠재력 예측",
            "종합 AI 분석 및 맞춤형 관리 권장사항"
        ],
    }
@app.get("/health")
def health_status():
    return {"status": "healthy", "version": "2.8.0"}
