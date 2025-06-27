# schemas/user.py

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class LoginType(str, Enum):
    EMAIL = "email"           # 이메일/비밀번호 로그인
    GOOGLE = "google"         # 구글 로그인
    KAKAO = "kakao"          # 카카오 로그인
    NAVER = "naver"          # 네이버 로그인
    FACEBOOK = "facebook"    # 페이스북 로그인

class UserCreate(BaseModel):
    username: str                            # 사용자 이름/실명
    user_id: str                             # 로그인용 아이디  
    email: EmailStr                          # 이메일
    password: str                            # 비밀번호
    password_confirm: str                    # 비밀번호 확인
    farm_nickname: Optional[str] = None      # 목장 별명 (선택)
    
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
                raise ValueError('목장 별명은 15자 이하여야 합니다')
            # 특수문자 제한 (기본적인 특수문자만 허용)
            import re
            if not re.match(r'^[가-힣a-zA-Z0-9\s\-_()]+$', v.strip()):
                raise ValueError('목장 별명에는 특수문자를 사용할 수 없습니다 (-, _, () 제외)')
            return v.strip()
        return v

class UserLogin(BaseModel):
    user_id: str                             # 로그인용 아이디
    password: str

class UserResponse(BaseModel):
    id: str
    username: str                            # 사용자 이름/실명
    user_id: str                             # 로그인용 아이디
    email: str                               # 이메일
    farm_nickname: Optional[str]             # 목장 별명
    farm_id: str                             # 농장 ID
    created_at: datetime                     # 가입일
    is_active: bool                          # 활성 상태
    login_type: Optional[LoginType] = None   # 로그인 타입 (SNS 로그인 구분용)
    sns_provider: Optional[str] = None       # SNS 제공자 (google, kakao, naver 등)
    sns_user_id: Optional[str] = None        # SNS 사용자 ID

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# 아이디/비밀번호 찾기용 스키마
class FindUserIdRequest(BaseModel):
    username: str                            # 사용자 이름/실명
    email: EmailStr                          # 이메일
    
    @validator('username')
    def username_validation(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('이름을 입력해주세요')
        return v.strip()
    
    @validator('email')
    def email_validation(cls, v):
        if not v:
            raise ValueError('이메일을 입력해주세요')
        return v

class PasswordResetRequest(BaseModel):
    username: str                            # 사용자 이름/실명
    user_id: str                             # 로그인용 아이디
    email: EmailStr                          # 이메일
    
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
    
    @validator('email')
    def email_validation(cls, v):
        if not v:
            raise ValueError('이메일을 입력해주세요')
        return v

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    
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

# 임시 토큰으로 로그인하기 위한 스키마
class TemporaryTokenLogin(BaseModel):
    user_id: str                             # 로그인용 아이디
    reset_token: str                         # 비밀번호 재설정 토큰
    
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

# 비밀번호 변경용 스키마 (로그인된 상태에서 사용)
class ChangePasswordRequest(BaseModel):
    new_password: str
    confirm_password: str
    
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

class DeleteAccountRequest(BaseModel):
    password: Optional[str] = Field(None, description="이메일 로그인 사용자의 경우 현재 비밀번호")
    confirmation: str = Field(..., description="삭제 확인 문구 ('DELETE' 입력)")
    sns_token: Optional[str] = Field(None, description="SNS 로그인 사용자의 경우 SNS 액세스 토큰")

class SNSDeleteAccountRequest(BaseModel):
    confirmation: str = Field(..., description="삭제 확인 문구 ('DELETE' 입력)")
    sns_provider: LoginType = Field(..., description="SNS 제공자 (google, kakao, naver 등)")
    sns_token: str = Field(..., description="SNS 액세스 토큰")

class FarmNicknameUpdate(BaseModel):
    farm_nickname: str = Field(..., description="새로운 목장 이름")
    
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