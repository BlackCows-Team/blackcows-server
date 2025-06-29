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
    def create_user(username: str, user_id: str, email: str, password: str, farm_nickname: str = None) -> Dict:
        """Firestore에 새 사용자 생성 - 목장 별명으로 변경"""
        try:
            # 아이디 중복 확인
            from google.cloud.firestore_v1.base_query import FieldFilter
            user_id_query = db.collection('users').where('user_id', '==', user_id).get()
            if user_id_query:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 아이디입니다"
                )
            
            # 이메일 중복 확인
            email_query = db.collection('users').where('email', '==', email).get()
            if email_query:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 이메일입니다"
                )
            
            # 새 사용자 데이터 생성
            user_uuid = str(uuid.uuid4())
            farm_id = f"farm_{user_uuid[:8]}"
            hashed_password = FirebaseUserService.get_password_hash(password)
            
            user_data = {
                "id": user_uuid,                                        # UUID
                "username": username,                                   # 사용자 이름/실명
                "user_id": user_id,                                    # 로그인용 아이디
                "email": email,                                        # 이메일
                "hashed_password": hashed_password,                    # 해시된 비밀번호
                "farm_nickname": farm_nickname or f"{username}님의 목장", # 목장 별명 (이름 기반 기본값)
                "farm_id": farm_id,                                    # 농장 ID
                "is_active": True,                                     # 활성 상태
                "created_at": datetime.utcnow(),                       # 가입일
                "updated_at": datetime.utcnow()                        # 수정일
            }
            
            # Firestore에 사용자 저장
            db.collection('users').document(user_uuid).set(user_data)
            
            # 목장 정보도 별도 컬렉션에 저장
            farm_data = {
                "farm_id": farm_id,
                "farm_nickname": farm_nickname or f"{username}님의 목장", # 목장 별명
                "owner_id": user_uuid,
                "owner_name": username,                                # 농장주 이름
                "owner_user_id": user_id,                              # 농장주 아이디
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
    def authenticate_user(user_id: str, password: str) -> Optional[Dict]:
        """사용자 인증 - user_id로 로그인"""
        try:
            # Firestore에서 사용자 검색 (user_id로 검색)
            users_ref = db.collection('users')
            query = users_ref.where('user_id', '==', user_id).limit(1).get()
            
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
            
            # 기존 사용자 호환성: auth_type이 없거나 null이면 email로 간주
            if user_data.get("auth_type") is None or user_data.get("auth_type") == "":
                print(f"[DEBUG] 기존 사용자 - auth_type이 없음, email로 간주")
                user_data["auth_type"] = "email"
                
                # DB에 auth_type 업데이트 (한 번만)
                try:
                    db.collection('users').document(user_data["id"]).update({
                        "auth_type": "email",
                        "updated_at": datetime.utcnow()
                    })
                    print(f"[DEBUG] 기존 사용자 auth_type 업데이트 완료")
                    
                except Exception as update_error:
                    print(f"[WARNING] auth_type 업데이트 실패: {str(update_error)}")
                    # 업데이트 실패해도 메모리상에서는 처리
                    user_data["auth_type"] = "email"
            
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
    def get_user_by_user_id(user_id: str) -> Optional[Dict]:
        """user_id로 사용자 조회"""
        try:
            from google.cloud.firestore_v1.base_query import FieldFilter
            users_ref = db.collection('users')
            query = users_ref.where('user_id', '==', user_id).limit(1).get()
            
            if query:
                return query[0].to_dict()
            return None
        except Exception as e:
            print(f"Get user by user_id error: {str(e)}")
            return None
    
    @staticmethod
    def find_user_id_by_name_and_email(username: str, email: str) -> Optional[Dict]:
        """이름과 이메일로 사용자 찾기 (아이디 찾기용)"""
        try:
            users_ref = db.collection('users')
            
            # 이름과 이메일이 모두 일치하는 사용자 검색
            query = (users_ref
                    .where('username', '==', username)
                    .where('email', '==', email)
                    .where('is_active', '==', True)
                    .limit(1)
                    .get())
            
            if query:
                return query[0].to_dict()
            
            return None
        except Exception as e:
            print(f"Find user by name and email error: {str(e)}")
            return None
    
    @staticmethod
    def verify_user_for_password_reset(username: str, user_id: str, email: str) -> Optional[Dict]:
        """비밀번호 재설정을 위한 사용자 확인 - 이름, 아이디, 이메일 모두 확인"""
        try:
            users_ref = db.collection('users')
            
            # 이름, user_id, 이메일이 모두 일치하는 사용자 검색
            query = (users_ref
                    .where('username', '==', username)
                    .where('user_id', '==', user_id)
                    .where('email', '==', email)
                    .where('is_active', '==', True)
                    .limit(1)
                    .get())
            
            if query:
                return query[0].to_dict()
            
            return None
        except Exception as e:
            print(f"Verify user for password reset error: {str(e)}")
            return None
    
    # JWT 토큰 관련 메서드들 (기존과 동일)
    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """액세스 토큰 생성"""
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
            user_id = payload.get("sub")  # user_id를 sub에 저장
            token_type = payload.get("type")
            
            if user_id is None or token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 토큰입니다",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Firestore에서 사용자 정보 조회 (user_id로 검색)
            user = FirebaseUserService.get_user_by_user_id(user_id)
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
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict:
        """리프레시 토큰으로 새 액세스 토큰 발급"""
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
            
            # 새 액세스 토큰 생성 (user_id를 sub에 저장)
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = FirebaseUserService.create_access_token(
                data={"sub": user["user_id"], "user_uuid": user["id"]},
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
    
    @staticmethod
    def verify_reset_token_and_user(user_id: str, reset_token: str) -> Optional[Dict]:
        """임시 토큰과 사용자 ID를 검증하고 사용자 정보 반환"""
        try:
            # 간단한 토큰 검증 (실제로는 JWT 토큰 사용)
            if not reset_token.startswith("reset_token_for_"):
                return None
            
            # 토큰에서 사용자 UUID 추출
            user_uuid = reset_token.replace("reset_token_for_", "")
            
            # 사용자 존재 확인
            user = FirebaseUserService.get_user_by_id(user_uuid)
            if not user:
                return None
            
            # 입력받은 user_id와 DB의 user_id가 일치하는지 확인
            if user.get("user_id") != user_id:
                return None
            
            # 토큰 만료 시간 체크 (실제로는 JWT에서 처리해야 함)
            # 여기서는 간단히 구현하기 위해 생략하고, 실제로는 토큰 생성 시간을 DB에 저장해서 체크
            
            return user
            
        except Exception as e:
            print(f"Reset token verification error: {str(e)}")
            return None
    
    @staticmethod
    def create_password_reset_token(user_data: Dict) -> str:
        """JWT 기반 비밀번호 재설정 토큰 생성 (1시간 유효)"""
        expires_delta = timedelta(hours=1)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": user_data["user_id"],
            "user_uuid": user_data["id"],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "password_reset",
            "purpose": "reset_password"
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_password_reset_token(user_id: str, reset_token: str) -> Optional[Dict]:
        """JWT 기반 비밀번호 재설정 토큰 검증"""
        try:
            # JWT 토큰 검증 (만료 시간 자동 체크)
            payload = jwt.decode(reset_token, SECRET_KEY, algorithms=[ALGORITHM])
            
            token_user_id = payload.get("sub")
            token_type = payload.get("type")
            user_uuid = payload.get("user_uuid")
            purpose = payload.get("purpose")
            
            # 토큰 타입 및 용도 확인
            if token_type != "password_reset" or purpose != "reset_password":
                return None
            
            # 사용자 ID 일치 확인
            if token_user_id != user_id:
                return None
            
            # 사용자 존재 확인
            user = FirebaseUserService.get_user_by_id(user_uuid)
            if not user:
                return None
            
            return user
            
        except jwt.ExpiredSignatureError:
            print("Password reset token expired")
            return None
        except JWTError as e:
            print(f"Password reset token verification error: {str(e)}")
            return None
        except Exception as e:
            print(f"Password reset token verification error: {str(e)}")
            return None
    
    @staticmethod
    def create_password_reset_access_token(user_data: Dict) -> str:
        """비밀번호 재설정 전용 임시 액세스 토큰 생성 (30분 유효)"""
        expires_delta = timedelta(minutes=30)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": user_data["user_id"],
            "user_uuid": user_data["id"],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "password_reset_access",  # 특별한 토큰 타입
            "permissions": ["change_password"]  # 비밀번호 변경 권한만
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_password_reset_access_token(token: str) -> Dict:
        """비밀번호 재설정 전용 액세스 토큰 검증"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            token_type = payload.get("type")
            user_uuid = payload.get("user_uuid")
            permissions = payload.get("permissions", [])
            
            if user_id is None or token_type != "password_reset_access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 토큰입니다",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if "change_password" not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="비밀번호 변경 권한이 없습니다"
                )
            
            # 사용자 정보 조회
            user = FirebaseUserService.get_user_by_user_id(user_id)
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

    @staticmethod
    def delete_user_account(user: Dict, password: str, confirmation: str) -> Dict:
        """사용자 계정 완전 삭제 - 모든 관련 데이터 삭제"""
        try:
            # 1. 삭제 확인 문구 검증
            if confirmation != "DELETE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="삭제 확인 문구가 올바르지 않습니다. 'DELETE'를 정확히 입력해주세요."
                )
            
            # 2. 비밀번호 확인
            if not FirebaseUserService.verify_password(password, user["hashed_password"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="비밀번호가 올바르지 않습니다"
                )
            
            user_uuid = user["id"]
            farm_id = user["farm_id"]
            
            # 3. 관련 데이터 삭제 (순서 중요)
            
            # 3-1. 상세기록 삭제
            detailed_records = db.collection('cow_detailed_records').where('farm_id', '==', farm_id).get()
            for record in detailed_records:
                db.collection('cow_detailed_records').document(record.id).delete()
            
            # 3-2. 기록 삭제  
            records = db.collection('cow_records').where('farm_id', '==', farm_id).get()
            for record in records:
                db.collection('cow_records').document(record.id).delete()
            
            # 3-3. 소 정보 삭제
            cows = db.collection('cows').where('farm_id', '==', farm_id).get()
            for cow in cows:
                db.collection('cows').document(cow.id).delete()
            
            # 3-4. 리프레시 토큰 삭제
            refresh_tokens = db.collection('refresh_tokens').where('user_id', '==', user_uuid).get()
            for token in refresh_tokens:
                db.collection('refresh_tokens').document(token.id).delete()
            
            # 3-5. 농장 정보 삭제
            db.collection('farms').document(farm_id).delete()
            
            # 3-6. 사용자 정보 삭제 (마지막)
            db.collection('users').document(user_uuid).delete()
            
            return {
                "success": True,
                "message": f"{user['username']}님의 계정이 완전히 삭제되었습니다",
                "deleted_data": {
                    "user": user['username'],
                    "farm_id": farm_id,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"계정 삭제 중 오류가 발생했습니다: {str(e)}"
            )