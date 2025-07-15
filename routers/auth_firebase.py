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
from services.email_service import EmailService  # 이메일 서비스 추가
from datetime import timedelta, datetime, timezone
from config.firebase_config import get_firestore_client
from pydantic import BaseModel
from typing import Optional
import traceback


router = APIRouter()
security = HTTPBearer()

# Firestore 클라이언트
db = get_firestore_client()

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
    
    # 회원가입 축하 이메일 발송 (비동기로 처리, 실패해도 회원가입은 성공)
    try:
        EmailService.send_welcome_email(user)
        print(f"[INFO] {user['username']}님께 환영 이메일 발송 완료")
    except Exception as e:
        print(f"[WARNING] 환영 이메일 발송 실패: {str(e)}")
        # 이메일 발송 실패는 회원가입 성공에 영향주지 않음
    
    
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
        
        # 신규 사용자인 경우 환영 이메일 발송
        if is_new_user:
            try:
                EmailService.send_welcome_email(user_data)
                print(f"[INFO] SNS 신규 사용자 {user_data['username']}님께 환영 이메일 발송 완료")
            except Exception as e:
                print(f"[WARNING] SNS 환영 이메일 발송 실패: {str(e)}")
        
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
            summary="통합 로그인",
            description="아이디와 비밀번호(또는 임시 비밀번호)로 로그인합니다. 일반 로그인 또는 임시 비밀번호 로그인 모두 지원합니다.")
def login_user(user_data: UserLogin):
    """통합 로그인 - 일반/임시 비밀번호 모두 지원"""
    print(f"[DEBUG] 로그인 요청 데이터: {user_data.dict()}")
    print(f"[DEBUG] user_id: '{user_data.user_id}', password: '{user_data.password}'")
    print(f"[DEBUG] user_id 타입: {type(user_data.user_id)}, password 타입: {type(user_data.password)}")

    # 1. 일반 비밀번호 검증
    user = FirebaseUserService.authenticate_user(user_data.user_id, user_data.password)
    if user:
        # 일반 로그인 성공
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = FirebaseUserService.create_access_token(
            data={"sub": user["user_id"], "user_uuid": user["id"]},
            expires_delta=access_token_expires
        )
        refresh_token = FirebaseUserService.create_refresh_token(user["id"])
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],
            user_id=user["user_id"],
            email=user["email"],
            farm_nickname=user["farm_nickname"],
            farm_id=user["farm_id"],
            created_at=user["created_at"],
            last_login=user["last_login"],
            is_active=user["is_active"],
            auth_type=AuthType(user.get("auth_type", "email")),
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

    # 2. 임시 비밀번호 검증
    # user_id(별칭)로 UUID 조회 후, UUID로 임시 비밀번호 검증
    user_for_temp = FirebaseUserService.get_user_by_user_id(user_data.user_id)
    temp_id = None
    if user_for_temp:
        temp_id = EmailService.verify_temporary_password(user_for_temp["id"], user_data.password)
    if temp_id:
        # 임시 비밀번호 로그인 성공 - 사용자 정보 조회
        user = user_for_temp
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # 비밀번호 변경 전용 액세스 토큰 생성 (30분 유효)
        access_token = FirebaseUserService.create_password_reset_access_token(user)
        refresh_token = FirebaseUserService.create_refresh_token(user["id"])
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],
            user_id=user["user_id"],
            email=user["email"],
            farm_nickname=user["farm_nickname"],
            farm_id=user["farm_id"],
            created_at=user["created_at"],
            last_login=user["last_login"],
            is_active=user["is_active"],
            auth_type=AuthType(user.get("auth_type", "email")),
            sns_provider=user.get("sns_provider"),
            sns_user_id=user.get("sns_user_id")
        )
        # 임시 비밀번호 로그인 응답(비밀번호 변경 안내)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30분
            user=user_response,
            is_new_user=False,
            temp_login=True,
            notice="임시 비밀번호로 로그인되었습니다. 반드시 새 비밀번호로 변경해주세요."
        )

    # 3. 모두 실패
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="잘못된 아이디 또는 비밀번호입니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

# 기존 임시 비밀번호 로그인 엔드포인트는 deprecated 안내만 남김
@router.post("/login-with-temporary-password",
            summary="[DEPRECATED] 임시 비밀번호 로그인",
            description="더 이상 사용하지 마세요. /login 엔드포인트를 사용하세요.")
def login_with_temporary_password(request: UserLogin):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="이 API는 더 이상 지원하지 않습니다. /login 엔드포인트를 사용하세요."
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
            description="사용자 이름과 이메일을 통해 아이디를 찾고 이메일로 발송합니다.")
def find_user_id_by_name_and_email(request: FindUserIdRequest):
    """이름과 이메일로 아이디 찾기 - 이메일로 발송"""
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
                "google": "구글"
            }
            platform_name = auth_type_names.get(user["auth_type"], "소셜")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"해당 이메일은 {platform_name} 로그인으로 가입된 계정입니다. {platform_name} 로그인을 이용해주세요."
            )
        
        # 아이디 찾기 이메일 발송
        try:
            EmailService.send_user_id_email(user)
            print(f"[INFO] {user['username']}님께 아이디 찾기 이메일 발송 완료")
        except Exception as e:
            print(f"[ERROR] 아이디 찾기 이메일 발송 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="아이디 찾기 이메일 발송에 실패했습니다"
            )
        
        return {
            "success": True,
            "message": f"{user['username']}님의 아이디를 이메일로 발송했습니다",
            "email": request.email,
            "username": user["username"]
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
            description="이름, 아이디, 이메일 확인 후 임시 비밀번호를 이메일로 발송합니다.")
async def request_password_reset(request: PasswordResetRequest):
    """비밀번호 재설정 요청 - 임시 비밀번호 이메일 발송"""
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
                "google": "구글"
            }
            platform_name = auth_type_names.get(user["auth_type"], "소셜")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"해당 계정은 {platform_name} 로그인으로 가입된 계정입니다. 비밀번호 재설정이 불가능합니다."
            )
        
        # 임시 비밀번호 생성
        temp_password = EmailService._generate_temporary_password()
        expire_minutes = 60  # 1시간
        
        # 임시 비밀번호를 Firestore에 저장
        temp_id = EmailService.store_temporary_password(
            user["id"], 
            temp_password, 
            expire_minutes
        )
        
        # 만료 시간 계산 (KST로 변환)
        kst = timezone(timedelta(hours=9))
        expire_time = datetime.now(kst) + timedelta(minutes=expire_minutes)
        
        # 임시 비밀번호 이메일 발송
        try:
            EmailService.send_temporary_password_email(user, temp_password, expire_time)
            print(f"[INFO] {user['username']}님께 임시 비밀번호 이메일 발송 완료")
        except Exception as e:
            print(f"[ERROR] 임시 비밀번호 이메일 발송 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="임시 비밀번호 이메일 발송에 실패했습니다"
            )
        
        return {
            "success": True,
            "message": f"{user['username']}님의 임시 비밀번호를 이메일로 발송했습니다",
            "username": user["username"],
            "user_id": request.user_id,
            "email": request.email,
            "temp_id": temp_id,
            "expires_in": f"{expire_minutes}분",
            "notice": "임시 비밀번호로 로그인 후 반드시 새 비밀번호로 변경해주세요"
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비밀번호 재설정 요청 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/change-password",
            summary="비밀번호 변경",
            description="임시 비밀번호로 로그인한 사용자 또는 일반 로그인한 사용자의 비밀번호를 변경합니다.")
def change_password(
    request: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """비밀번호 변경"""
    try:
        token = credentials.credentials
        
        # 토큰 타입 확인 (일반 토큰 또는 비밀번호 재설정 토큰)
        try:
            # 비밀번호 재설정 전용 토큰인지 확인
            user = FirebaseUserService.verify_password_reset_access_token(token)
            is_temp_login = True
        except:
            try:
                # 일반 액세스 토큰인지 확인
                user = FirebaseUserService.verify_access_token(token)
                is_temp_login = False
            except:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 토큰입니다",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
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
        
        # 임시 로그인인 경우 모든 리프레시 토큰 무효화 (보안 강화)
        if is_temp_login:
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
            "username": user["username"],
            "user_id": user["user_id"],
            "password_changed_at": datetime.utcnow().isoformat(),
            "notice": "비밀번호 변경이 완료되었습니다. 새 비밀번호로 다시 로그인해주세요." if is_temp_login else "비밀번호 변경이 완료되었습니다."
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
            username=updated_user_data["username"],
            user_id=updated_user_data["user_id"],
            email=updated_user_data["email"],
            farm_nickname=updated_user_data["farm_nickname"],
            farm_id=updated_user_data["farm_id"],
            created_at=updated_user_data["created_at"],
            is_active=updated_user_data["is_active"],
            auth_type=AuthType(updated_user_data.get("auth_type", "email"))
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

# ============= 관리자용 API =============

@router.post("/admin/cleanup-temporary-passwords",
            summary="만료된 임시 비밀번호 정리",
            description="만료된 임시 비밀번호를 정리합니다. (관리자용)")
def cleanup_temporary_passwords():
    """만료된 임시 비밀번호 정리 (관리자용)"""
    try:
        deleted_count = EmailService.cleanup_expired_temporary_passwords()
        
        return {
            "success": True,
            "message": f"만료된 임시 비밀번호 {deleted_count}개가 정리되었습니다",
            "deleted_count": deleted_count,
            "cleanup_time": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"임시 비밀번호 정리 중 오류가 발생했습니다: {str(e)}"
        )

# 다른 라우터에서 사용할 인증 의존성
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """인증된 사용자 정보 반환"""
    token = credentials.credentials
    return FirebaseUserService.verify_access_token(token)