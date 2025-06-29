# routers/auth_firebase.py

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas.user import (
    UserCreate, UserLogin, TokenResponse, RefreshTokenRequest, UserResponse,
    FindUserIdRequest, PasswordResetRequest, PasswordResetConfirm,
    TemporaryTokenLogin, ChangePasswordRequest, DeleteAccountRequest,
    FarmNicknameUpdate, LoginType, SocialLoginRequest, AuthType
)
from services.firebase_user_service import FirebaseUserService, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta, datetime
from config.firebase_config import get_firestore_client
from pydantic import BaseModel
from typing import Optional
import traceback

router = APIRouter()
security = HTTPBearer()

# Firestore 클라이언트
db = get_firestore_client()

# (개발용)

@router.post("/mock-social-login",
            summary="개발용 모의 SNS 로그인",
            description="실제 SNS 토큰 없이 테스트할 수 있는 모의 엔드포인트")
async def mock_social_login(mock_request: dict):
    """개발용 모의 SNS 로그인"""
    try:
        auth_type = mock_request.get("auth_type")
        mock_user_info = mock_request.get("mock_user_info", {})
        
        # 모의 사용자 정보 생성
        from schemas.user import SocialUserInfo, AuthType
        social_info = SocialUserInfo(
            social_id=mock_user_info.get("social_id", "mock_id_12345"),
            email=mock_user_info.get("email", f"mock@{auth_type}.test"),
            name=mock_user_info.get("name", f"{auth_type.capitalize()} 테스트 사용자"),
            profile_image=None
        )
        
        # 기존 사용자 확인
        existing_user = FirebaseUserService._find_user_by_social_id(
            social_info.social_id, 
            AuthType(auth_type)
        )
        
        current_time = datetime.utcnow()
        
        if existing_user:
            # 기존 사용자 로그인
            db.collection('users').document(existing_user["id"]).update({
                "last_login": current_time,
                "updated_at": current_time
            })
            existing_user["last_login"] = current_time
            user_data = existing_user
            is_new_user = False
        else:
            # 신규 사용자 생성
            from services.social_auth_service import SocialAuthService
            username = social_info.name
            user_id = SocialAuthService.generate_unique_user_id(social_info, AuthType(auth_type))
            farm_nickname = f"{username}의 목장 ({auth_type} 테스트)"
            
            user_data = FirebaseUserService.create_user(
                username=username,
                user_id=user_id,
                email=social_info.email,
                password=None,
                farm_nickname=farm_nickname,
                auth_type=AuthType(auth_type),
                social_id=social_info.social_id
            )
            is_new_user = True
        
        # 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = FirebaseUserService.create_access_token(
            data={"sub": user_data["user_id"], "user_uuid": user_data["id"]},
            expires_delta=access_token_expires
        )
        refresh_token = FirebaseUserService.create_refresh_token(user_data["id"])
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user_data["id"],
                "username": user_data["username"],
                "user_id": user_data["user_id"],
                "email": user_data["email"],
                "farm_nickname": user_data["farm_nickname"],
                "farm_id": user_data["farm_id"],
                "auth_type": user_data["auth_type"],
                "created_at": user_data["created_at"].isoformat(),
                "last_login": user_data["last_login"].isoformat(),
                "is_active": user_data["is_active"]
            },
            "is_new_user": is_new_user,
            "mock_mode": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모의 로그인 처리 중 오류: {str(e)}"
        )
        
        

@router.post("/register", 
            response_model=dict,
            summary="일반 회원가입",
            description="새로운 사용자 계정을 생성합니다. 이메일과 비밀번호로 새로운 사용자 계정을 생성합니다.")

async def register_user(user_data: UserCreate):
    """일반 회원가입 - 이메일 + 비밀번호"""
    user = FirebaseUserService.create_user(
        username=user_data.username,            # 사용자 이름/실명
        user_id=user_data.user_id,              # 로그인용 아이디
        email=user_data.email,                  # 이메일
        password=user_data.password,            # 비밀번호
        farm_nickname=user_data.farm_nickname,  # 목장 별명
        auth_type=AuthType.EMAIL                # 명시적으로 이메일 인증 타입 설정
    )
    
    return {
        "success": True,
        "message": "회원가입이 완료되었습니다",
        "user": {
            "id": user["id"],                       # UUID
            "username": user["username"],           # 사용자 이름/실명
            "user_id": user["user_id"],             # 로그인용 아이디
            "email": user["email"],                 # 이메일
            "farm_nickname": user["farm_nickname"], # 목장 별명
            "farm_id": user["farm_id"],             # 농장 ID
            "auth_type": user["auth_type"]          # 인증 타입
        }
    }

@router.post("/social-login",
            response_model=TokenResponse,
            summary="SNS 로그인/회원가입",
            description="""
            소셜 로그인으로 로그인하거나 회원가입합니다.
            
            **지원 플랫폼:**
            - Google: access_token + id_token (선택)
            - Kakao: access_token
            - Naver: access_token
            
            **처리 과정:**
            1. 액세스 토큰으로 SNS에서 사용자 정보 조회
            2. 기존 사용자면 로그인, 신규면 자동 회원가입
            3. JWT 토큰 발급
            
            **주의사항:**
            - 이메일이 다른 방식으로 이미 가입된 경우 오류 반환
            """)
async def social_login(login_request: SocialLoginRequest):
    """SNS 로그인/회원가입 통합 처리"""
    try:
        # SNS 로그인 또는 회원가입 처리
        user_data, is_new_user = await FirebaseUserService.social_login_or_register(login_request)
        
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = FirebaseUserService.create_access_token(
            data={"sub": user_data["user_id"], "user_uuid": user_data["id"]},
            expires_delta=access_token_expires
        )
        
        # 리프레시 토큰 생성
        refresh_token = FirebaseUserService.create_refresh_token(user_data["id"])
        
        # 사용자 정보 응답 구성
        user_response = UserResponse(
            id=user_data["id"],
            username=user_data["username"],
            user_id=user_data["user_id"],
            email=user_data["email"],
            farm_nickname=user_data["farm_nickname"],
            farm_id=user_data["farm_id"],
            auth_type=AuthType(user_data["auth_type"]),
            created_at=user_data["created_at"],
            last_login=user_data["last_login"],
            is_active=user_data["is_active"]
        )
        
        success_message = "회원가입 완료" if is_new_user else "로그인 성공"
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response,
            is_new_user=is_new_user
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"소셜 로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )
        

@router.post("/login", 
            response_model=TokenResponse,
            summary="일반 로그인",
            description="이메일 회원가입한 사용자의 아이디와 비밀번호로 로그인합니다. 액세스 토큰을 발급받습니다.")
def login_user(user_data: UserLogin):
    """일반 로그인 - user_id로 로그인"""
    # 디버깅을 위한 로그 추가
    print(f"[DEBUG] 로그인 요청 데이터: {user_data.dict()}")
    print(f"[DEBUG] user_id: '{user_data.user_id}', password: '{user_data.password}'")
    print(f"[DEBUG] user_id 타입: {type(user_data.user_id)}, password 타입: {type(user_data.password)}")
    
    user = FirebaseUserService.authenticate_user(user_data.user_id, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 아이디 또는 비밀번호입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 액세스 토큰 생성 (user_id를 sub에 저장)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = FirebaseUserService.create_access_token(
        data={"sub": user["user_id"], "user_uuid": user["id"]},
        expires_delta=access_token_expires
    )
    
    # 리프레시 토큰 생성
    refresh_token = FirebaseUserService.create_refresh_token(user["id"])
    
    # 사용자 정보 (비밀번호 제외)
    user_response = UserResponse(
        id=user["id"],
        username=user["username"],              # 사용자 이름/실명
        user_id=user["user_id"],                # 로그인용 아이디
        email=user["email"],                    # 이메일
        farm_nickname=user["farm_nickname"],    # 목장 별명
        farm_id=user["farm_id"],                # 농장 ID
        created_at=user["created_at"],          # 가입일
        last_login=user["last_login"],          # 최근 로그인 시간
        is_active=user["is_active"],            # 활성 상태
        auth_type=AuthType(user.get("auth_type", "email")),  # 기본값 email
        sns_provider=user.get("sns_provider"),   # SNS 제공자
        sns_user_id=user.get("sns_user_id")      # SNS 사용자 ID
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@router.post("/refresh",
            summary="토큰 갱신",
            description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.")
def refresh_token(token_data: RefreshTokenRequest):
    """토큰 갱신"""
    return FirebaseUserService.refresh_access_token(token_data.refresh_token)

@router.get("/me", 
           response_model=UserResponse,
           summary="현재 사용자 정보 조회",
           description="현재 로그인된 사용자의 정보를 조회합니다.")
def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 사용자 정보 조회"""
    token = credentials.credentials
    user = FirebaseUserService.verify_access_token(token)
    
    return UserResponse(
        id=user["id"],
        username=user["username"],              # 사용자 이름/실명
        user_id=user["user_id"],                # 로그인용 아이디
        email=user["email"],                    # 이메일
        farm_nickname=user["farm_nickname"],    # 목장 별명
        farm_id=user["farm_id"],                # 농장 ID
        created_at=user["created_at"],          # 가입일
        last_login=user["last_login"],          # 최근 로그인 시간
        is_active=user["is_active"],            # 활성 상태
        auth_type=AuthType(user.get("auth_type", "email")),  # 기본값 email
        sns_provider=user.get("sns_provider"),   # SNS 제공자
        sns_user_id=user.get("sns_user_id")      # SNS 사용자 ID
    )

# ===== 계정 연동 관련 API =====

@router.post("/link-social-account",
            summary="소셜 계정 연동",
            description="""
            기존 이메일 계정에 소셜 계정을 연동합니다.
            
            **주의사항:**
            - 이메일 계정으로 가입한 사용자만 가능
            - 연동하려는 소셜 계정이 다른 계정에 이미 연동되어 있으면 안됨
            """)
async def link_social_account(
    link_request: SocialLoginRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """소셜 계정 연동 (향후 구현)"""
    # TODO: 계정 연동 로직 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="계정 연동 기능은 향후 구현 예정입니다"
    )

@router.delete("/unlink-social-account",
              summary="소셜 계정 연동 해제",
              description="연동된 소셜 계정을 해제합니다.")
async def unlink_social_account(
    auth_type: AuthType,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """소셜 계정 연동 해제 (향후 구현)"""
    # TODO: 계정 연동 해제 로직 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="계정 연동 해제 기능은 향후 구현 예정입니다"
    )


# ============= 아이디/비밀번호 찾기 API =============

@router.post("/find-user-id",
            summary="아이디 찾기",
            description="사용자 이름과 이메일을 통해 아이디를 찾습니다. (이메일 계정만 가능)")
def find_user_id_by_name_and_email(request: FindUserIdRequest):
    """이름과 이메일로 아이디 찾기 - 이메일 계정만"""
    try:
        user = FirebaseUserService.find_user_id_by_name_and_email(request.username, request.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="입력하신 이름과 이메일에 일치하는 계정을 찾을 수 없습니다"
            )
        
        # SNS 로그인 사용자는 아이디 찾기 불가
        if user.get("auth_type") != AuthType.EMAIL.value:
            auth_type_names = {
                "google": "구글",
                "kakao": "카카오",
                "naver": "네이버"
            }
            platform_name = auth_type_names.get(user["auth_type"], "소셜")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"해당 이메일은 {platform_name} 로그인으로 가입된 계정입니다. {platform_name} 로그인을 이용해주세요."
            )
        
        return {
            "success": True,
            "message": "아이디를 찾았습니다",
            "username": user["username"],               # 사용자 이름/실명
            "user_id": user["user_id"],                 # 로그인용 아이디
            "email": request.email,                     # 입력한 이메일
            "farm_nickname": user.get("farm_nickname", "") # 목장 별명
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이디 찾기 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/request-password-reset",
            summary="비밀번호 재설정 요청",
            description="이름, 아이디, 이메일 확인 후 비밀번호 재설정 토큰을 발급합니다. (이메일 계정만 가능)")
async def request_password_reset(request: PasswordResetRequest):
    """비밀번호 재설정 요청 - 이메일 계정만"""
    try:
        user = FirebaseUserService.verify_user_for_password_reset(
            request.username, 
            request.user_id, 
            request.email
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="입력하신 이름, 아이디, 이메일이 모두 일치하는 계정을 찾을 수 없습니다"
            )
        
        # SNS 로그인 사용자는 비밀번호 재설정 불가
        if user.get("auth_type") != AuthType.EMAIL.value:
            auth_type_names = {
                "google": "구글",
                "kakao": "카카오",
                "naver": "네이버"
            }
            platform_name = auth_type_names.get(user["auth_type"], "소셜")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"해당 계정은 {platform_name} 로그인으로 가입된 계정입니다. 비밀번호 재설정이 불가능합니다."
            )
        
        # JWT 기반 비밀번호 재설정 토큰 생성
        reset_token = FirebaseUserService.create_password_reset_token(user)
        
        return {
            "success": True,
            "message": f"{user['username']}님의 비밀번호 재설정 요청이 완료되었습니다",
            "username": user["username"],
            "user_id": request.user_id,
            "email": request.email,
            "reset_token": reset_token,
            "expires_in": "1시간"
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비밀번호 재설정 요청 중 오류가 발생했습니다: {str(e)}"
        )
        
@router.post("/verify-reset-token",
            summary="재설정 토큰 확인",
            description="비밀번호 재설정 토큰의 유효성을 확인합니다.")
def verify_reset_token(request: dict):
    """비밀번호 재설정 토큰 확인 (간단 버전)"""
    token = request.get("token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="재설정 토큰을 입력해주세요"
        )
    
    try:
        # JWT 토큰 디코딩으로 기본 검증 (만료 시간 포함)
        from jose import jwt, JWTError
        from services.firebase_user_service import SECRET_KEY, ALGORITHM
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_type = payload.get("type")
            user_id = payload.get("sub")
            user_uuid = payload.get("user_uuid")
            
            if token_type != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="유효하지 않은 재설정 토큰입니다"
                )
            
            # 사용자 존재 확인
            user = FirebaseUserService.get_user_by_id(user_uuid)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="유효하지 않은 사용자입니다"
                )
            
            return {
                "valid": True,
                "message": "유효한 토큰입니다",
                "username": user["username"],
                "user_id": user["user_id"]
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="재설정 토큰이 만료되었습니다"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 재설정 토큰입니다"
            )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="토큰 확인 중 오류가 발생했습니다"
        )

@router.post("/reset-password",
            summary="비밀번호 재설정",
            description="재설정 토큰을 사용하여 새로운 비밀번호로 변경합니다.")
def reset_password(request: PasswordResetConfirm):
    """비밀번호 재설정 (간단 버전)"""
    try:
        # JWT 토큰 검증으로 사용자 정보 가져오기
        from jose import jwt, JWTError
        from services.firebase_user_service import SECRET_KEY, ALGORITHM
        
        try:
            payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
            token_type = payload.get("type")
            user_id = payload.get("sub")
            user_uuid = payload.get("user_uuid")
            
            if token_type != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="유효하지 않은 재설정 토큰입니다"
                )
            
            # 사용자 존재 확인
            user = FirebaseUserService.get_user_by_id(user_uuid)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다"
                )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="재설정 토큰이 만료되었습니다"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 재설정 토큰입니다"
            )
        
        # 비밀번호 변경 (Firebase DB 업데이트)
        from config.firebase_config import get_firestore_client
        from datetime import datetime
        db = get_firestore_client()
        
        # 새 비밀번호 해시화
        hashed_password = FirebaseUserService.get_password_hash(request.new_password)
        
        # Firebase DB에서 사용자 비밀번호 업데이트
        db.collection('users').document(user_uuid).update({
            "hashed_password": hashed_password,
            "updated_at": datetime.utcnow(),
            "password_changed_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "message": f"{user['username']}님의 비밀번호가 성공적으로 변경되었습니다",
            "username": user["username"],               # 사용자 이름/실명
            "user_id": user["user_id"]                  # 로그인용 아이디
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비밀번호 재설정 중 오류가 발생했습니다: {str(e)}"
        )

# 다른 라우터에서 사용할 인증 의존성
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """인증된 사용자 정보 반환"""
    token = credentials.credentials
    return FirebaseUserService.verify_access_token(token)

# 추가: 디버그용 로그인 엔드포인트
@router.post("/login-debug",
            summary="로그인 디버그",
            description="로그인 요청 데이터를 디버깅하기 위한 엔드포인트입니다.")
async def login_debug(request: Request):
    """로그인 디버깅용 엔드포인트 - 원시 데이터 확인"""
    try:
        # 원시 바이트 데이터 읽기
        body = await request.body()
        print(f"[DEBUG] 원시 요청 바디: {body}")
        
        # JSON 파싱 시도
        import json
        try:
            json_data = json.loads(body)
            print(f"[DEBUG] 파싱된 JSON: {json_data}")
            print(f"[DEBUG] JSON 키들: {list(json_data.keys()) if isinstance(json_data, dict) else 'dict가 아님'}")
            
            # UserLogin 스키마 검증 시도
            try:
                user_login = UserLogin(**json_data)
                print(f"[DEBUG] UserLogin 스키마 검증 성공: {user_login.dict()}")
                return {"status": "success", "message": "로그인 데이터 검증 성공", "data": user_login.dict()}
            except Exception as schema_error:
                print(f"[DEBUG] UserLogin 스키마 검증 실패: {schema_error}")
                return {"status": "schema_error", "error": str(schema_error), "data": json_data}
                
        except json.JSONDecodeError as json_error:
            print(f"[DEBUG] JSON 파싱 실패: {json_error}")
            return {"status": "json_error", "error": str(json_error), "raw_body": body.decode('utf-8', errors='ignore')}
            
    except Exception as e:
        print(f"[DEBUG] 전체 요청 처리 실패: {e}")
        return {"status": "error", "error": str(e)}

# ============= 임시 토큰 로그인 API =============

@router.post("/login-with-reset-token",
            summary="임시 토큰 로그인",
            description="비밀번호 재설정 토큰을 사용하여 임시 로그인하고 비밀번호 변경 권한을 가진 액세스 토큰을 발급받습니다.")
def login_with_reset_token(request: TemporaryTokenLogin):
    """임시 토큰으로 로그인하여 비밀번호 변경 권한을 가진 특별한 액세스 토큰 발급"""
    try:
        # JWT 기반 임시 토큰과 사용자 ID 검증
        user = FirebaseUserService.verify_password_reset_token(
            request.user_id, 
            request.reset_token
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 아이디 또는 재설정 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 비밀번호 재설정 전용 액세스 토큰 생성 (30분 유효, 비밀번호 변경 권한만)
        access_token = FirebaseUserService.create_password_reset_access_token(user)
        
        # 사용자 정보 (비밀번호 제외)
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],              # 사용자 이름/실명
            user_id=user["user_id"],                # 로그인용 아이디
            email=user["email"],                    # 이메일
            farm_nickname=user["farm_nickname"],    # 목장 별명
            farm_id=user["farm_id"],                # 농장 ID
            created_at=user["created_at"],          # 가입일
            last_login=user["last_login"],          # 최근 로그인 시간
            is_active=user["is_active"],             # 활성 상태
            login_type=LoginType(user.get("auth_type", "email")),  # auth_type을 login_type으로 변환
            sns_provider=user.get("sns_provider"),   # SNS 제공자
            sns_user_id=user.get("sns_user_id")      # SNS 사용자 ID
        )
        
        return {
            "success": True,
            "message": "임시 토큰으로 로그인되었습니다. 비밀번호를 변경해주세요.",
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60,  # 30분
            "permissions": ["change_password"],
            "user": user_response
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"임시 토큰 로그인 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/change-password",
            summary="비밀번호 변경",
            description="비밀번호 재설정 토큰으로 로그인한 사용자의 비밀번호를 변경합니다.")
def change_password(
    request: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """비밀번호 변경 (비밀번호 재설정 토큰으로 로그인한 사용자만 가능)"""
    try:
        token = credentials.credentials
        
        # 비밀번호 재설정 전용 토큰 검증
        user = FirebaseUserService.verify_password_reset_access_token(token)
        
        # 비밀번호 변경
        from config.firebase_config import get_firestore_client
        from datetime import datetime
        db = get_firestore_client()
        
        # 새 비밀번호 해시화
        hashed_password = FirebaseUserService.get_password_hash(request.new_password)
        
        # Firebase DB에서 사용자 비밀번호 업데이트
        db.collection('users').document(user["id"]).update({
            "hashed_password": hashed_password,
            "updated_at": datetime.utcnow(),
            "password_changed_at": datetime.utcnow()
        })
        
        # 기존 리프레시 토큰들 모두 무효화 (보안 강화)
        refresh_tokens_ref = db.collection('refresh_tokens').where('user_id', '==', user["id"])
        refresh_tokens = refresh_tokens_ref.get()
        
        for token_doc in refresh_tokens:
            db.collection('refresh_tokens').document(token_doc.id).update({
                "is_active": False,
                "deactivated_at": datetime.utcnow(),
                "deactivated_reason": "password_changed"
            })
        
        return {
            "success": True,
            "message": f"{user['username']}님의 비밀번호가 성공적으로 변경되었습니다",
            "username": user["username"],               # 사용자 이름/실명
            "user_id": user["user_id"],                 # 로그인용 아이디
            "password_changed_at": datetime.utcnow().isoformat(),
            "notice": "보안을 위해 모든 기기에서 로그아웃되었습니다. 새 비밀번호로 다시 로그인해주세요."
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비밀번호 변경 중 오류가 발생했습니다: {str(e)}"
        )

# ============= 목장 이름 수정 API =============

@router.put("/update-farm-name",
           response_model=dict,
           summary="목장 이름 수정",
           description="현재 로그인된 사용자의 목장 이름을 수정합니다.")
def update_farm_name(
    request: FarmNicknameUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """목장 이름 수정"""
    try:
        token = credentials.credentials
        
        # 일반 액세스 토큰 검증 (로그인된 사용자)
        user = FirebaseUserService.verify_access_token(token)
        
        # Firebase DB에서 사용자 문서의 farm_nickname 필드 업데이트
        from config.firebase_config import get_firestore_client
        from datetime import datetime
        db = get_firestore_client()
        
        # 사용자 문서 업데이트
        update_data = {
            "farm_nickname": request.farm_nickname,
            "updated_at": datetime.utcnow()
        }
        
        db.collection('users').document(user["id"]).update(update_data)
        
        # 업데이트된 사용자 정보 가져오기
        updated_user_doc = db.collection('users').document(user["id"]).get()
        if not updated_user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        updated_user_data = updated_user_doc.to_dict()
        
        # 사용자 정보 응답 (비밀번호 제외)
        user_response = UserResponse(
            id=updated_user_data["id"],
            username=updated_user_data["username"],              # 사용자 이름/실명
            user_id=updated_user_data["user_id"],                # 로그인용 아이디
            email=updated_user_data["email"],                    # 이메일
            farm_nickname=updated_user_data["farm_nickname"],    # 수정된 목장 별명
            farm_id=updated_user_data["farm_id"],                # 농장 ID
            created_at=updated_user_data["created_at"],          # 가입일
            is_active=updated_user_data["is_active"],             # 활성 상태
            login_type=LoginType(updated_user_data.get("auth_type", "email")),  # auth_type을 login_type으로 변환
            sns_provider=updated_user_data.get("sns_provider"),   # SNS 제공자
            sns_user_id=updated_user_data.get("sns_user_id")      # SNS 사용자 ID
        )
        
        return {
            "success": True,
            "message": "목장 이름이 성공적으로 수정되었습니다",
            "user": user_response.dict()
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"목장 이름 수정 중 오류가 발생했습니다: {str(e)}"
        )

# ============= 회원탈퇴 API =============

@router.delete("/delete-account",
              summary="회원탈퇴",
              description="사용자 계정과 모든 관련 데이터를 완전히 삭제합니다.")
def delete_account(
    request: DeleteAccountRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """회원탈퇴 - 모든 관련 데이터 완전 삭제"""
    try:
        token = credentials.credentials
        
        # 일반 액세스 토큰 검증 (로그인된 사용자)
        user = FirebaseUserService.verify_access_token(token)
        
        # 계정 삭제 실행
        result = FirebaseUserService.delete_user_account(
            user, 
            request.password, 
            request.confirmation
        )
        
        return result
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원탈퇴 처리 중 오류가 발생했습니다: {str(e)}"
        )