# routers/sns_auth.py

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas.user import (
    LoginType, SNSDeleteAccountRequest, UserResponse, TokenResponse
)
from services.sns_auth_service import SNSAuthService
from services.firebase_user_service import FirebaseUserService, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
import uuid

router = APIRouter()
security = HTTPBearer()

@router.post("/google/login",
            response_model=TokenResponse,
            summary="구글 로그인",
            description="구글 ID 토큰을 사용하여 로그인합니다.")
async def google_login(id_token: str, farm_nickname: str = None):
    """구글 로그인"""
    try:
        # 구글 토큰 검증
        sns_data = SNSAuthService.verify_google_token(id_token)
        
        # 사용자 생성 또는 조회
        user = SNSAuthService.create_or_get_sns_user(sns_data, farm_nickname)
        
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = FirebaseUserService.create_access_token(
            data={"sub": user["user_id"], "user_uuid": user["id"]},
            expires_delta=access_token_expires
        )
        
        # 리프레시 토큰 생성
        refresh_token = FirebaseUserService.create_refresh_token(user["id"])
        
        # 사용자 정보 응답
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],
            user_id=user["user_id"],
            email=user["email"],
            farm_nickname=user["farm_nickname"],
            farm_id=user["farm_id"],
            created_at=user["created_at"],
            is_active=user["is_active"],
            login_type=LoginType(user.get("auth_type") or user.get("login_type", "google")),
            sns_provider=user.get("sns_provider"),
            sns_user_id=user.get("sns_user_id")
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"구글 로그인 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/kakao/login",
            response_model=TokenResponse,
            summary="카카오 로그인",
            description="카카오 액세스 토큰을 사용하여 로그인합니다.")
async def kakao_login(access_token: str, farm_nickname: str = None):
    """카카오 로그인"""
    try:
        # 카카오 토큰 검증
        sns_data = SNSAuthService.verify_kakao_token(access_token)
        
        # 사용자 생성 또는 조회
        user = SNSAuthService.create_or_get_sns_user(sns_data, farm_nickname)
        
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = FirebaseUserService.create_access_token(
            data={"sub": user["user_id"], "user_uuid": user["id"]},
            expires_delta=access_token_expires
        )
        
        # 리프레시 토큰 생성
        refresh_token = FirebaseUserService.create_refresh_token(user["id"])
        
        # 사용자 정보 응답
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],
            user_id=user["user_id"],
            email=user["email"],
            farm_nickname=user["farm_nickname"],
            farm_id=user["farm_id"],
            created_at=user["created_at"],
            is_active=user["is_active"],
            login_type=LoginType(user.get("auth_type") or user.get("login_type", "kakao")),
            sns_provider=user.get("sns_provider"),
            sns_user_id=user.get("sns_user_id")
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카카오 로그인 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/naver/login",
            response_model=TokenResponse,
            summary="네이버 로그인",
            description="네이버 액세스 토큰을 사용하여 로그인합니다.")
async def naver_login(access_token: str, farm_nickname: str = None):
    """네이버 로그인"""
    try:
        # 네이버 토큰 검증
        sns_data = SNSAuthService.verify_naver_token(access_token)
        
        # 사용자 생성 또는 조회
        user = SNSAuthService.create_or_get_sns_user(sns_data, farm_nickname)
        
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = FirebaseUserService.create_access_token(
            data={"sub": user["user_id"], "user_uuid": user["id"]},
            expires_delta=access_token_expires
        )
        
        # 리프레시 토큰 생성
        refresh_token = FirebaseUserService.create_refresh_token(user["id"])
        
        # 사용자 정보 응답
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],
            user_id=user["user_id"],
            email=user["email"],
            farm_nickname=user["farm_nickname"],
            farm_id=user["farm_id"],
            created_at=user["created_at"],
            is_active=user["is_active"],
            login_type=LoginType(user.get("auth_type") or user.get("login_type", "naver")),
            sns_provider=user.get("sns_provider"),
            sns_user_id=user.get("sns_user_id")
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"네이버 로그인 중 오류가 발생했습니다: {str(e)}"
        )

@router.delete("/delete-account",
              summary="SNS 사용자 회원 탈퇴",
              description="SNS 로그인 사용자의 계정과 모든 관련 데이터를 완전히 삭제합니다.")
async def delete_sns_account(
    request: SNSDeleteAccountRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """SNS 사용자 회원 탈퇴"""
    try:
        token = credentials.credentials
        
        # 액세스 토큰 검증
        user = FirebaseUserService.verify_access_token(token)
        
        # SNS 사용자인지 확인
        if not user.get("login_type") or user.get("login_type") == "email":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SNS 로그인 사용자만 사용할 수 있는 기능입니다"
            )
        
        # SNS 제공자 확인
        if user.get("sns_provider") != request.sns_provider.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"잘못된 SNS 제공자입니다. 현재 계정: {user.get('sns_provider')}"
            )
        
        # 계정 삭제 실행
        result = SNSAuthService.delete_sns_user_account(
            user, 
            request.sns_provider.value, 
            request.sns_token
        )
        
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SNS 회원 탈퇴 처리 중 오류가 발생했습니다: {str(e)}"
        ) 