# schemas/user.py

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

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