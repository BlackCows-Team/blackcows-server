from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas.user import UserCreate, UserLogin, TokenResponse, RefreshTokenRequest, UserResponse
from services.firebase_user_service import FirebaseUserService, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=dict)
def register_user(user_data: UserCreate):
    """회원가입"""
    user = FirebaseUserService.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        farm_name=user_data.farm_name
    )
    
    return {
        "message": "회원가입이 완료되었습니다",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "farm_name": user["farm_name"],
            "farm_id": user["farm_id"]
        }
    }

@router.post("/login", response_model=TokenResponse)
def login_user(user_data: UserLogin):
    """로그인"""
    user = FirebaseUserService.authenticate_user(user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 액세스 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = FirebaseUserService.create_access_token(
        data={"sub": user["username"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    # 리프레시 토큰 생성
    refresh_token = FirebaseUserService.create_refresh_token(user["id"])
    
    # 사용자 정보 (비밀번호 제외)
    user_response = UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        farm_name=user["farm_name"],
        farm_id=user["farm_id"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@router.post("/refresh")
def refresh_token(token_data: RefreshTokenRequest):
    """토큰 갱신"""
    return FirebaseUserService.refresh_access_token(token_data.refresh_token)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 사용자 정보 조회"""
    token = credentials.credentials
    user = FirebaseUserService.verify_access_token(token)
    
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        farm_name=user["farm_name"],
        farm_id=user["farm_id"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )

# 다른 라우터에서 사용할 인증 의존성
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """인증된 사용자 정보 반환"""
    token = credentials.credentials
    return FirebaseUserService.verify_access_token(token)