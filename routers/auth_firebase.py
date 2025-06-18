# routers/auth_firebase.py

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas.user import (
    UserCreate, UserLogin, TokenResponse, RefreshTokenRequest, UserResponse,
    FindUserIdRequest, PasswordResetRequest, PasswordResetConfirm
)
from services.firebase_user_service import FirebaseUserService, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=dict)
def register_user(user_data: UserCreate):
    """회원가입 - 목장 별명 포함"""
    user = FirebaseUserService.create_user(
        username=user_data.username,            # 사용자 이름/실명
        user_id=user_data.user_id,              # 로그인용 아이디
        email=user_data.email,                  # 이메일
        password=user_data.password,            # 비밀번호
        farm_nickname=user_data.farm_nickname   # 목장 별명 (선택)
    )
    
    return {
        "success": True,
        "message": "회원가입이 완료되었습니다",
        "user": {
            "id": user["id"],
            "username": user["username"],       # 사용자 이름/실명
            "user_id": user["user_id"],         # 로그인용 아이디
            "email": user["email"],             # 이메일
            "farm_nickname": user["farm_nickname"], # 목장 별명
            "farm_id": user["farm_id"]          # 농장 ID
        }
    }

@router.post("/login", response_model=TokenResponse)
def login_user(user_data: UserLogin):
    """로그인 - user_id로 로그인"""
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
        is_active=user["is_active"]             # 활성 상태
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
        username=user["username"],              # 사용자 이름/실명
        user_id=user["user_id"],                # 로그인용 아이디
        email=user["email"],                    # 이메일
        farm_nickname=user["farm_nickname"],    # 목장 별명
        farm_id=user["farm_id"],                # 농장 ID
        created_at=user["created_at"],          # 가입일
        is_active=user["is_active"]             # 활성 상태
    )

# ============= 아이디/비밀번호 찾기 API =============

@router.post("/find-user-id")
def find_user_id_by_name_and_email(request: FindUserIdRequest):
    """이름과 이메일로 아이디 찾기 - Flutter 앱에서 바로 표시"""
    try:
        # Firebase에서 이름과 이메일로 사용자 검색
        user = FirebaseUserService.find_user_id_by_name_and_email(request.username, request.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="입력하신 이름과 이메일에 일치하는 계정을 찾을 수 없습니다"
            )
        
        # 찾은 아이디를 Flutter 앱에서 바로 표시
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

@router.post("/request-password-reset")
def request_password_reset(request: PasswordResetRequest):
    """비밀번호 재설정 요청 - 이름, 아이디, 이메일 모두 확인"""
    try:
        # 이름, user_id, 이메일이 모두 일치하는 사용자 확인
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
        
        # 비밀번호 재설정 토큰 생성 (실제 환경에서는 JWT 토큰 사용)
        reset_token = f"reset_token_for_{user['id']}"  # 임시 토큰
        
        # TODO: 여기서 실제 이메일 발송 (나중에 구현)
        # success = FirebaseUserService.send_password_reset_email(request.email, request.username, reset_token)
        
        return {
            "success": True,
            "message": f"{user['username']}님의 이메일({request.email})로 비밀번호 재설정 링크를 전송했습니다",
            "username": user["username"],               # 사용자 이름/실명
            "user_id": request.user_id,                 # 로그인용 아이디
            "email": request.email,                     # 이메일
            "reset_token": reset_token,                 # 임시 토큰 (개발용)
            "expires_in": "1시간"
        }
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비밀번호 재설정 요청 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/verify-reset-token")
def verify_reset_token(request: dict):
    """비밀번호 재설정 토큰 확인 (간단 버전)"""
    token = request.get("token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="재설정 토큰을 입력해주세요"
        )
    
    try:
        # 간단한 토큰 검증 (실제로는 JWT 토큰 사용)
        if not token.startswith("reset_token_for_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 재설정 토큰입니다"
            )
        
        # 토큰에서 사용자 ID 추출 (임시 방법)
        user_uuid = token.replace("reset_token_for_", "")
        
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
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="토큰 확인 중 오류가 발생했습니다"
        )

@router.post("/reset-password")
def reset_password(request: PasswordResetConfirm):
    """비밀번호 재설정 (간단 버전)"""
    try:
        # 간단한 토큰 검증 (실제로는 JWT 토큰 사용)
        if not request.token.startswith("reset_token_for_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 재설정 토큰입니다"
            )
        
        # 토큰에서 사용자 ID 추출 (임시 방법)
        user_uuid = request.token.replace("reset_token_for_", "")
        
        # 사용자 존재 확인
        user = FirebaseUserService.get_user_by_id(user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
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
@router.post("/login-debug")
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