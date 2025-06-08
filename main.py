import os
from fastapi import FastAPI
from routers import cow, test, record
from routers import auth_firebase
from fastapi.middleware.cors import CORSMiddleware

# JWT 시크릿 키 검증
if not os.getenv("JWT_SECRET_KEY"):
    raise ValueError("JWT_SECRET_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인하세요.")

app = FastAPI(
    title="낙농 관리 서버 API",
    version="1.0.0",
    description="AWS 클라우드 환경에서 실행되는 JWT 인증과 Firebase DB 활용한 낙농 관리 시스템"
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
app.include_router(test.router, prefix="/test", tags=["테스트"])

@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "낙농 관리 서버가 정상 작동 중입니다!!!",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}