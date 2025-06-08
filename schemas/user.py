from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirm: str
    farm_name: Optional[str] = None
    
    @validator('username')
    def username_validation(cls, v):
        if len(v) < 3:
            raise ValueError('사용자명은 3자 이상이어야 합니다')
        if len(v) > 20:
            raise ValueError('사용자명은 20자 이하여야 합니다')
        return v
    
    @validator('password')
    def password_validation(cls, v):
        if len(v) < 6:
            raise ValueError('비밀번호는 6자 이상이어야 합니다')
        return v
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    farm_name: Optional[str]
    farm_id: str
    created_at: datetime
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str