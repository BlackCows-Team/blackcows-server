from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
import uuid
import os

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# Firestore 클라이언트
db = get_firestore_client()

class FirebaseUserService:
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_user(username: str, email: str, password: str, farm_name: str = None) -> Dict:
        """Firestore에 새 사용자 생성"""
        try:
            # 사용자명 중복 확인
            username_query = db.collection('users').where('username', '==', username).get()
            if username_query:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 사용자명입니다"
                )
            
            # 이메일 중복 확인
            email_query = db.collection('users').where('email', '==', email).get()
            if email_query:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 이메일입니다"
                )
            
            # 새 사용자 데이터 생성
            user_id = str(uuid.uuid4())
            farm_id = f"farm_{user_id[:8]}"
            hashed_password = FirebaseUserService.get_password_hash(password)
            
            user_data = {
                "id": user_id,
                "username": username,
                "email": email,
                "hashed_password": hashed_password,
                "farm_name": farm_name or f"{username}의 목장",
                "farm_id": farm_id,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Firestore에 사용자 저장
            db.collection('users').document(user_id).set(user_data)
            
            # 목장 정보도 별도 컬렉션에 저장
            farm_data = {
                "farm_id": farm_id,
                "farm_name": farm_name or f"{username}의 목장",
                "owner_id": user_id,
                "owner_username": username,
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            db.collection('farms').document(farm_id).set(farm_data)
            
            # 비밀번호 제외하고 반환
            user_data.pop('hashed_password')
            return user_data
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"사용자 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict]:
        """사용자 인증"""
        try:
            # Firestore에서 사용자 검색
            users_ref = db.collection('users')
            query = users_ref.where('username', '==', username).limit(1).get()
            
            if not query:
                return None
            
            user_doc = query[0]
            user_data = user_doc.to_dict()
            
            # 비밀번호 확인
            if not FirebaseUserService.verify_password(password, user_data["hashed_password"]):
                return None
            
            # 활성 상태 확인
            if not user_data.get("is_active", True):
                return None
            
            return user_data
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        """ID로 사용자 조회"""
        try:
            user_doc = db.collection('users').document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            print(f"Get user error: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        """사용자명으로 사용자 조회"""
        try:
            users_ref = db.collection('users')
            query = users_ref.where('username', '==', username).limit(1).get()
            
            if query:
                return query[0].to_dict()
            return None
        except Exception as e:
            print(f"Get user by username error: {str(e)}")
            return None
    
    # 로그인 시 토큰 생성
    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """서버에서 JWT액세스 토큰 생성"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """리프레시 토큰 생성"""
        token_id = str(uuid.uuid4())
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        token_data = {
            "user_id": user_id,
            "token_id": token_id,
            "exp": expire,
            "type": "refresh"
        }
        
        # 리프레시 토큰을 Firestore에 저장
        db.collection('refresh_tokens').document(token_id).set({
            "user_id": user_id,
            "token_id": token_id,
            "created_at": datetime.utcnow(),
            "expires_at": expire,
            "is_active": True
        })
        
        encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_access_token(token: str) -> Dict:
        """액세스 토큰 검증"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            token_type = payload.get("type")
            
            if username is None or token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 토큰입니다",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Firestore에서 사용자 정보 조회
            user = FirebaseUserService.get_user_by_username(username)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="사용자를 찾을 수 없습니다",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰 검증에 실패했습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # 토큰 갱신 요청 처리
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict:
        """서버에서 리프레시 토큰으로 새 액세스 토큰 발급"""
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            token_id = payload.get("token_id")
            token_type = payload.get("type")
            user_id = payload.get("user_id")
            
            if token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 리프레시 토큰입니다"
                )
            
            # Firestore에서 리프레시 토큰 확인
            token_doc = db.collection('refresh_tokens').document(token_id).get()
            if not token_doc.exists or not token_doc.to_dict().get("is_active"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="만료되거나 비활성화된 리프레시 토큰입니다"
                )
            
            # 사용자 정보 조회
            user = FirebaseUserService.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="사용자를 찾을 수 없습니다"
                )
            
            # 새 액세스 토큰 생성
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = FirebaseUserService.create_access_token(
                data={"sub": user["username"], "user_id": user["id"]},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="리프레시 토큰 검증에 실패했습니다"
            )