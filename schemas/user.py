# schemas/user.py

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# ===== 열거형 정의 =====

class AuthType(str, Enum):
    """인증 타입 열거형"""
    EMAIL = "email"          # 일반 이메일 회원가입
    GOOGLE = "google"        # 구글 로그인

# LoginType은 AuthType과 동일하지만 호환성을 위해 별칭으로 추가
LoginType = AuthType

class SNSProvider(str, Enum):
    """SNS 제공자 열거형"""
    GOOGLE = "google"

# ===== 회원가입 관련 스키마 =====

class UserCreate(BaseModel):
    """일반 회원가입 요청 스키마"""
    username: str = Field(..., description="사용자 이름/실명", min_length=2, max_length=20)
    user_id: str = Field(..., description="로그인용 아이디", min_length=3, max_length=20)
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호", min_length=6, max_length=20)
    password_confirm: str = Field(..., description="비밀번호 확인")
    farm_nickname: Optional[str] = Field(None, description="목장 별명 (선택)", max_length=50)
    
    @validator('username')
    def username_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('이름은 필수입니다')
        if len(v.strip()) < 2:
            raise ValueError('이름은 2자 이상이어야 합니다')
        if len(v.strip()) > 20:
            raise ValueError('이름은 20자 이하여야 합니다')
        # 한글, 영문, 공백만 허용 (숫자 제외)
        import re
        if not re.match(r'^[가-힣a-zA-Z\s]+$', v.strip()):
            raise ValueError('이름은 한글, 영문만 입력 가능합니다')
        return v.strip()
    
    @validator('user_id')
    def user_id_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('아이디는 필수입니다')
        if len(v.strip()) < 3:
            raise ValueError('아이디는 3자 이상이어야 합니다')
        if len(v.strip()) > 20:
            raise ValueError('아이디는 20자 이하여야 합니다')
        # 영문, 숫자, 언더스코어만 허용 (첫 글자는 영문으로 시작)
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v.strip()):
            raise ValueError('아이디는 영문으로 시작하고 영문, 숫자, 언더스코어(_)만 사용 가능합니다')
        return v.strip()
    
    @validator('password')
    def password_validation(cls, v):
        if len(v) < 6:
            raise ValueError('비밀번호는 6자 이상이어야 합니다')
        if len(v) > 20:
            raise ValueError('비밀번호는 20자 이하여야 합니다')
        return v
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v
    
    @validator('farm_nickname')
    def farm_nickname_validation(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                return None  # 빈 문자열은 None으로 처리
            if len(v.strip()) > 50:
                raise ValueError('목장 별명은 50자 이하여야 합니다')
            # 특수문자 제한 (기본적인 특수문자만 허용)
            import re
            if not re.match(r'^[가-힣a-zA-Z0-9\s\-_()]+$', v.strip()):
                raise ValueError('목장 별명에는 특수문자를 사용할 수 없습니다 (-, _, () 제외)')
            return v.strip()
        return v

# ===== SNS 로그인 관련 스키마 =====

class SocialLoginRequest(BaseModel):
    """SNS 로그인/회원가입 요청 스키마"""
    auth_type: AuthType = Field(..., description="인증 타입 (google, kakao, naver)")
    access_token: str = Field(..., description="SNS 플랫폼에서 받은 액세스 토큰")
    id_token: Optional[str] = Field(None, description="ID 토큰 (Google 로그인에서 사용)")
    farm_nickname: Optional[str] = Field(None, description="목장 별명 (회원가입시 선택)", max_length=50)
    
    @validator('auth_type')
    def validate_auth_type(cls, v):
        if v == AuthType.EMAIL:
            raise ValueError('이메일 인증은 일반 회원가입을 사용해주세요')
        return v
    
    @validator('access_token')
    def validate_access_token(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('액세스 토큰은 필수입니다')
        return v.strip()
    
    @validator('farm_nickname')
    def farm_nickname_validation(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                return None
            if len(v.strip()) > 50:
                raise ValueError('목장 별명은 50자 이하여야 합니다')
            import re
            if not re.match(r'^[가-힣a-zA-Z0-9\s\-_()]+$', v.strip()):
                raise ValueError('목장 별명에는 특수문자를 사용할 수 없습니다 (-, _, () 제외)')
            return v.strip()
        return v

class SocialUserInfo(BaseModel):
    """SNS에서 가져온 사용자 정보 (내부 사용)"""
    social_id: str = Field(..., description="SNS 플랫폼의 고유 ID")
    email: Optional[str] = Field(None, description="이메일 (제공되는 경우)")
    name: Optional[str] = Field(None, description="이름 (제공되는 경우)")
    # profile_image 필드 제거 (요청사항)

# ===== 로그인 관련 스키마 =====

class UserLogin(BaseModel):
    """일반 로그인 요청 스키마"""
    user_id: str = Field(..., description="로그인용 아이디")
    password: str = Field(..., description="비밀번호")
    
    @validator('user_id')
    def user_id_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('아이디를 입력해주세요')
        return v.strip()
    
    @validator('password')
    def password_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('비밀번호를 입력해주세요')
        return v

# ===== 응답 스키마 =====

class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    id: str = Field(..., description="사용자 UUID")
    username: str = Field(..., description="사용자 이름/실명")
    user_id: str = Field(..., description="로그인용 아이디")
    email: str = Field(..., description="이메일 주소")
    farm_nickname: Optional[str] = Field(None, description="목장 별명")
    farm_id: str = Field(..., description="농장 ID")
    auth_type: AuthType = Field(AuthType.EMAIL, description="인증 타입 (기본값: email)")
    created_at: datetime = Field(..., description="계정 생성일")
    last_login: datetime = Field(..., description="최근 로그인 시간")
    is_active: bool = Field(..., description="계정 활성 상태")
    # SNS 로그인 관련 필드들 (옵셔널)
    sns_provider: Optional[str] = Field(None, description="SNS 제공자")
    sns_user_id: Optional[str] = Field(None, description="SNS 사용자 ID")

class TokenResponse(BaseModel):
    """로그인 성공시 토큰 응답 스키마"""
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="토큰 만료 시간(초)")
    user: UserResponse = Field(..., description="사용자 정보")
    is_new_user: Optional[bool] = Field(False, description="신규 사용자 여부 (SNS 로그인시)")

# ===== 토큰 관련 스키마 =====

class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청 스키마"""
    refresh_token: str = Field(..., description="리프레시 토큰")
    
    @validator('refresh_token')
    def validate_refresh_token(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('리프레시 토큰은 필수입니다')
        return v.strip()

# ===== 아이디/비밀번호 찾기 스키마 =====

class FindUserIdRequest(BaseModel):
    """아이디 찾기 요청 스키마"""
    username: str = Field(..., description="사용자 이름/실명")
    email: EmailStr = Field(..., description="이메일 주소")
    
    @validator('username')
    def username_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('이름을 입력해주세요')
        return v.strip()

class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청 스키마"""
    username: str = Field(..., description="사용자 이름/실명")
    user_id: str = Field(..., description="로그인용 아이디")
    email: EmailStr = Field(..., description="이메일 주소")
    
    @validator('username')
    def username_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('이름을 입력해주세요')
        return v.strip()
    
    @validator('user_id')
    def user_id_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('아이디를 입력해주세요')
        return v.strip()

class PasswordResetConfirm(BaseModel):
    """비밀번호 재설정 확인 스키마"""
    token: str = Field(..., description="재설정 토큰")
    new_password: str = Field(..., description="새로운 비밀번호", min_length=6, max_length=20)
    confirm_password: str = Field(..., description="비밀번호 확인")
    
    @validator('token')
    def token_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('재설정 토큰이 없습니다')
        return v.strip()
    
    @validator('new_password')
    def password_validation(cls, v):
        if len(v) < 6:
            raise ValueError('비밀번호는 6자 이상이어야 합니다')
        if len(v) > 20:
            raise ValueError('비밀번호는 20자 이하여야 합니다')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v

# ===== 임시 토큰 로그인 스키마 =====

class TemporaryTokenLogin(BaseModel):
    """임시 토큰 로그인 스키마"""
    user_id: str = Field(..., description="로그인용 아이디")
    reset_token: str = Field(..., description="비밀번호 재설정 토큰")
    
    @validator('user_id')
    def user_id_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('아이디를 입력해주세요')
        return v.strip()
    
    @validator('reset_token')
    def token_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('재설정 토큰을 입력해주세요')
        return v.strip()

class ChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청 스키마 (로그인된 상태)"""
    new_password: str = Field(..., description="새로운 비밀번호", min_length=6, max_length=20)
    confirm_password: str = Field(..., description="비밀번호 확인")
    
    @validator('new_password')
    def password_validation(cls, v):
        if len(v) < 6:
            raise ValueError('비밀번호는 6자 이상이어야 합니다')
        if len(v) > 20:
            raise ValueError('비밀번호는 20자 이하여야 합니다')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v

# ===== 계정 관리 스키마 =====

class FarmNicknameUpdate(BaseModel):
    """목장 이름 수정 스키마"""
    farm_nickname: str = Field(..., description="새로운 목장 이름", max_length=50)
    
    @validator('farm_nickname')
    def farm_nickname_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('목장 이름을 입력해주세요')
        if len(v.strip()) > 50:
            raise ValueError('목장 이름은 50자 이하여야 합니다')
        # 특수문자 제한 (기본적인 특수문자만 허용)
        import re
        if not re.match(r'^[가-힣a-zA-Z0-9\s\-_()]+$', v.strip()):
            raise ValueError('목장 이름에는 특수문자를 사용할 수 없습니다 (-, _, () 제외)')
        return v.strip()

class DeleteAccountRequest(BaseModel):
    """회원탈퇴 요청 스키마"""
    password: str = Field(..., description="계정 삭제 확인용 현재 비밀번호")
    confirmation: str = Field(..., description="삭제 확인 문구 ('DELETE' 입력)")
    
    @validator('password')
    def password_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('비밀번호를 입력해주세요')
        return v
    
    @validator('confirmation')
    def confirmation_validation(cls, v):
        if v != "DELETE":
            raise ValueError("삭제 확인을 위해 'DELETE'를 정확히 입력해주세요")
        return v

# ===== 계정 연동 관련 스키마 (향후 확장용) =====

class AccountLinkRequest(BaseModel):
    """계정 연동 요청 스키마 (향후 구현)"""
    auth_type: AuthType = Field(..., description="연동할 인증 타입")
    access_token: str = Field(..., description="SNS 액세스 토큰")
    id_token: Optional[str] = Field(None, description="ID 토큰 (필요시)")
    
    @validator('auth_type')
    def validate_auth_type(cls, v):
        if v == AuthType.EMAIL:
            raise ValueError('이메일 인증은 연동할 수 없습니다')
        return v

class AccountUnlinkRequest(BaseModel):
    """계정 연동 해제 요청 스키마 (향후 구현)"""
    auth_type: AuthType = Field(..., description="연동 해제할 인증 타입")
    
    @validator('auth_type')
    def validate_auth_type(cls, v):
        if v == AuthType.EMAIL:
            raise ValueError('이메일 인증은 연동 해제할 수 없습니다')
        return v

# ===== 사용자 프로필 수정 스키마 =====

class UserProfileUpdate(BaseModel):
    """사용자 프로필 수정 스키마"""
    username: Optional[str] = Field(None, description="사용자 이름/실명", min_length=2, max_length=20)
    farm_nickname: Optional[str] = Field(None, description="목장 별명", max_length=50)
    
    @validator('username')
    def username_validation(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('이름은 비어있을 수 없습니다')
            if len(v.strip()) < 2:
                raise ValueError('이름은 2자 이상이어야 합니다')
            if len(v.strip()) > 20:
                raise ValueError('이름은 20자 이하여야 합니다')
            import re
            if not re.match(r'^[가-힣a-zA-Z\s]+$', v.strip()):
                raise ValueError('이름은 한글, 영문만 입력 가능합니다')
            return v.strip()
        return v
    
    @validator('farm_nickname')
    def farm_nickname_validation(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                return None
            if len(v.strip()) > 50:
                raise ValueError('목장 별명은 50자 이하여야 합니다')
            import re
            if not re.match(r'^[가-힣a-zA-Z0-9\s\-_()]+$', v.strip()):
                raise ValueError('목장 별명에는 특수문자를 사용할 수 없습니다 (-, _, () 제외)')
            return v.strip()
        return v

# ===== 사용자 통계 스키마 =====

class UserStatsResponse(BaseModel):
    """사용자 통계 응답 스키마"""
    total_cows: int = Field(..., description="총 젖소 수")
    total_records: int = Field(..., description="총 기록 수")
    last_activity: Optional[datetime] = Field(None, description="마지막 활동 시간")
    farm_created_at: datetime = Field(..., description="농장 생성일")
    days_since_registration: int = Field(..., description="가입 후 경과일")

# ===== 응답 공통 스키마 =====

class SuccessResponse(BaseModel):
    """성공 응답 공통 스키마"""
    success: bool = Field(True, description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: Optional[dict] = Field(None, description="추가 데이터")

class ErrorResponse(BaseModel):
    """오류 응답 공통 스키마"""
    success: bool = Field(False, description="성공 여부")
    error: str = Field(..., description="오류 메시지")
    error_code: Optional[str] = Field(None, description="오류 코드")
    details: Optional[dict] = Field(None, description="오류 상세 정보")

# ===== 개발/테스트용 스키마 =====

class MockSocialLoginRequest(BaseModel):
    """개발용 모의 SNS 로그인 스키마"""
    auth_type: AuthType = Field(..., description="인증 타입")
    mock_user_info: dict = Field(..., description="모의 사용자 정보")
    farm_nickname: Optional[str] = Field(None, description="목장 별명")
    
    @validator('auth_type')
    def validate_auth_type(cls, v):
        if v == AuthType.EMAIL:
            raise ValueError('이메일 인증은 모의 로그인에서 지원하지 않습니다')
        return v

# ===== SNS 회원탈퇴 관련 스키마 =====

class SNSDeleteAccountRequest(BaseModel):
    """SNS 계정 삭제 요청 스키마"""
    sns_provider: SNSProvider = Field(..., description="SNS 제공자 (google, kakao, naver)")
    sns_token: str = Field(..., description="SNS 액세스 토큰 (계정 연결 해제용)")
    
    @validator('sns_token')
    def validate_sns_token(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('SNS 토큰은 필수입니다')
        return v.strip()