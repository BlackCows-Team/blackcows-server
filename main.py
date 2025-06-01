from fastapi import FastAPI
from routers import cow
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (Flutter 연결을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# cow 라우터 연결
app.include_router(cow.router, prefix="/cows", tags=["Cows"])

@app.get("/")
def health_check():
    return {"status": "Server is running"}

from routers import test
app.include_router(test.router, prefix="/test", tags=["Test"])
