# services/firebase_user_service.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from config.firebase_config import get_firestore_client
from schemas.user import AuthType, SocialLoginRequest, SocialUserInfo
from services.social_auth_service import SocialAuthService
import uuid
import os

# ===== 설정 및 초기화 =====

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY 환경변수가 설정되지 않았습니다")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Firestore 클라이언트
db = get_firestore_client()

class FirebaseUserService:
    """Firebase 기반 사용자 서비스"""
    
    # ===== 비밀번호 관련 메서드 =====
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)
    
    # ===== 사용자 생성 및 관리 =====
    
    @staticmethod
    def create_user(
        username: str, 
        user_id: str, 
        email: str, 
        password: Optional[str] = None, 
        farm_nickname: Optional[str] = None,
        auth_type: AuthType = AuthType.EMAIL,
        social_id: Optional[str] = None
    ) -> Dict:
        """Firestore에 새 사용자 생성"""
        try:
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
            
            # SNS 로그인인 경우 social_id 중복 확인
            if auth_type != AuthType.EMAIL and social_id:
                social_query = db.collection('users')\
                    .where(filter=FieldFilter('social_id', '==', social_id))\
                    .where(filter=FieldFilter('auth_type', '==', auth_type.value))\
                    .get()
                if social_query:
                    auth_type_names = {
                        AuthType.GOOGLE: "구글",
                        AuthType.KAKAO: "카카오", 
                        AuthType.NAVER: "네이버"
                    }
                    platform_name = auth_type_names.get(auth_type, auth_type.value)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"이미 {platform_name} 계정으로 가입된 사용자입니다"
                    )
            
            # 새 사용자 데이터 생성
            user_uuid = str(uuid.uuid4())
            farm_id = f"farm_{user_uuid[:8]}"
            current_time = datetime.utcnow()
            
            # 비밀번호 처리 (SNS 로그인은 비밀번호 없음)
            hashed_password = None
            if auth_type == AuthType.EMAIL and password:
                hashed_password = FirebaseUserService.get_password_hash(password)
            
            # 기본 목장 별명 생성
            if not farm_nickname:
                if auth_type == AuthType.EMAIL:
                    farm_nickname = f"{username}님의 목장"
                else:
                    auth_type_names = {
                        AuthType.GOOGLE: "구글",
                        AuthType.KAKAO: "카카오",
                        AuthType.NAVER: "네이버"
                    }
                    platform_name = auth_type_names.get(auth_type, "소셜")
                    farm_nickname = f"{username}님의 목장 ({platform_name} 로그인)"
            
            user_data = {
                "id": user_uuid,                                        # UUID
                "username": username,                                   # 사용자 이름/실명
                "user_id": user_id,                                    # 로그인용 아이디
                "email": email,                                        # 이메일
                "hashed_password": hashed_password,                    # 해시된 비밀번호 (SNS는 None)
                "farm_nickname": farm_nickname,                        # 목장 별명
                "farm_id": farm_id,                                    # 농장 ID
                "auth_type": auth_type.value,                          # 인증 타입
                "social_id": social_id,                                # SNS 고유 ID (해당시에만)
                "is_active": True,                                     # 활성 상태
                "created_at": current_time,                            # 가입일
                "updated_at": current_time,                            # 수정일
                "last_login": current_time                             # 최근 로그인 시간
            }
            
            # Firestore에 사용자 저장
            db.collection('users').document(user_uuid).set(user_data)
            
            # 목장 정보도 별도 컬렉션에 저장
            farm_data = {
                "farm_id": farm_id,
                "farm_nickname": farm_nickname,
                "owner_id": user_uuid,
                "owner_name": username,
                "owner_user_id": user_id,
                "created_at": current_time,
                "is_active": True
            }
            db.collection('farms').document(farm_id).set(farm_data)
            
            # 비밀번호 제외하고 반환
            user_data.pop('hashed_password', None)
            return user_data
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            print(f"[ERROR] 사용자 생성 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"사용자 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    # ===== 인증 관련 메서드 =====
    
    @staticmethod
    def authenticate_user(user_id: str, password: str) -> Optional[Dict]:
        """일반 사용자 인증 (이메일 가입 사용자만)"""
        try:
            print(f"[DEBUG] 인증 시도 - user_id: '{user_id}', password_length: {len(password)}")
            
            # Firestore에서 사용자 검색
            users_ref = db.collection('users')
            query = users_ref.where('user_id', '==', user_id).limit(1).get()
            
            if not query:
                print(f"[DEBUG] 인증 실패 - 사용자를 찾을 수 없음: '{user_id}'")
                return None
            
            user_doc = query[0]
            user_data = user_doc.to_dict()
            print(f"[DEBUG] 사용자 발견 - auth_type: '{user_data.get('auth_type')}', is_active: {user_data.get('is_active')}")
            
            # 이메일 인증 유형만 비밀번호 확인
            user_auth_type = user_data.get("auth_type")
            
            # 기존 사용자 호환성: auth_type이 없거나 null이면 email로 간주
            if user_auth_type is None or user_auth_type == "":
                print(f"[DEBUG] 기존 사용자 - auth_type이 없음, email로 간주")
                user_auth_type = AuthType.EMAIL.value
                
                # DB에 auth_type 업데이트 (한 번만)
                try:
                    db.collection('users').document(user_data["id"]).update({
                        "auth_type": AuthType.EMAIL.value,
                        "updated_at": datetime.utcnow()
                    })
                    print(f"[DEBUG] 기존 사용자 auth_type 업데이트 완료")
                except Exception as update_error:
                    print(f"[WARNING] auth_type 업데이트 실패: {str(update_error)}")
            
            if user_auth_type != AuthType.EMAIL.value:
                print(f"[DEBUG] 인증 실패 - SNS 로그인 사용자 (auth_type: {user_auth_type})")
                return None  # SNS 로그인 사용자는 일반 로그인 불가
            
            # 비밀번호 확인
            has_password = bool(user_data.get("hashed_password"))
            print(f"[DEBUG] 비밀번호 체크 - has_hashed_password: {has_password}")
            
            if not has_password:
                print(f"[DEBUG] 인증 실패 - 저장된 비밀번호가 없음")
                return None
                
            password_valid = FirebaseUserService.verify_password(password, user_data["hashed_password"])
            print(f"[DEBUG] 비밀번호 검증 결과: {password_valid}")
            
            if not password_valid:
                print(f"[DEBUG] 인증 실패 - 비밀번호 불일치")
                return None

            # 활성 상태 확인
            if not user_data.get("is_active", True):
                print(f"[DEBUG] 인증 실패 - 계정 비활성화됨")
                return None

            print(f"[DEBUG] 인증 성공 - user_id: '{user_id}'")
            
            # 메모리상의 user_data도 auth_type 업데이트 (DB는 이미 위에서 업데이트함)
            if user_auth_type != user_data.get("auth_type"):
                user_data["auth_type"] = user_auth_type
            
            # 최근 로그인 시간 업데이트
            current_time = datetime.utcnow()
            db.collection('users').document(user_data["id"]).update({
                "last_login": current_time,
                "updated_at": current_time
            })

            # 업데이트된 last_login 시간 반영
            user_data["last_login"] = current_time
            user_data["updated_at"] = current_time

            return user_data

        except Exception as e:
            print(f"[ERROR] 사용자 인증 실패: {str(e)}")
            return None
    
    @staticmethod
    async def social_login_or_register(login_request: SocialLoginRequest) -> Tuple[Dict, bool]:
        """
        SNS 로그인 또는 회원가입 통합 처리
        
        Returns:
            Tuple[user_data, is_new_user]
        """
        try:
            # 1. SNS 플랫폼에서 사용자 정보 가져오기
            social_info = await SocialAuthService.get_social_user_info(
                login_request.auth_type,
                login_request.access_token,
                login_request.id_token
            )
            
            if not social_info.social_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SNS 플랫폼에서 사용자 ID를 가져올 수 없습니다"
                )
            
            # 2. 기존 사용자 확인 (social_id + auth_type으로)
            existing_user = FirebaseUserService._find_user_by_social_id(
                social_info.social_id, 
                login_request.auth_type
            )
            
            current_time = datetime.utcnow()
            
            if existing_user:
                # 기존 사용자 - 로그인 처리
                print(f"[INFO] 기존 SNS 사용자 로그인: {existing_user['user_id']}")
                
                # 최근 로그인 시간 업데이트
                db.collection('users').document(existing_user["id"]).update({
                    "last_login": current_time,
                    "updated_at": current_time
                })
                
                existing_user["last_login"] = current_time
                existing_user["updated_at"] = current_time
                return existing_user, False  # 기존 사용자
            
            else:
                # 신규 사용자 - 회원가입 처리
                print(f"[INFO] 신규 SNS 사용자 회원가입: {login_request.auth_type.value}")
                
                # 이메일 중복 확인 (다른 인증 방식으로 가입된 계정)
                if social_info.email:
                    email_user = FirebaseUserService._find_user_by_email(social_info.email)
                    if email_user:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"해당 이메일({social_info.email})은 이미 다른 방식으로 가입된 계정입니다"
                        )
                
                # 사용자 정보 생성
                username = social_info.name or f"{login_request.auth_type.value.capitalize()} 사용자"
                user_id = SocialAuthService.generate_unique_user_id(social_info, login_request.auth_type)
                email = social_info.email or f"{user_id}@{login_request.auth_type.value}.social"
                farm_nickname = login_request.farm_nickname or SocialAuthService.generate_default_farm_nickname(
                    social_info.name, login_request.auth_type
                )
                
                # 회원가입 처리
                new_user = FirebaseUserService.create_user(
                    username=username,
                    user_id=user_id,
                    email=email,
                    password=None,  # SNS 로그인은 비밀번호 없음
                    farm_nickname=farm_nickname,
                    auth_type=login_request.auth_type,
                    social_id=social_info.social_id
                )
                
                print(f"[INFO] 신규 SNS 사용자 생성 완료: {new_user['user_id']}")
                return new_user, True  # 신규 사용자
                
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            print(f"[ERROR] SNS 로그인/회원가입 처리 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"소셜 로그인 처리 중 오류가 발생했습니다: {str(e)}"
            )
    
    # ===== 사용자 조회 메서드 =====
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        """UUID로 사용자 조회"""
        try:
            user_doc = db.collection('users').document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            print(f"[ERROR] 사용자 조회 실패 (ID: {user_id}): {str(e)}")
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
            print(f"[ERROR] 사용자 조회 실패 (user_id: {user_id}): {str(e)}")
            return None
    
    @staticmethod
    def _find_user_by_social_id(social_id: str, auth_type: AuthType) -> Optional[Dict]:
        """social_id와 auth_type으로 사용자 찾기"""
        try:
            users_ref = db.collection('users')
            query = users_ref\
                .where('social_id', '==', social_id)\
                .where('auth_type', '==', auth_type.value)\
                .where('is_active', '==', True)\
                .limit(1)\
                .get()
            
            if query:
                return query[0].to_dict()
            return None
        except Exception as e:
            print(f"[ERROR] SNS 사용자 조회 실패: {str(e)}")
            return None
    
    @staticmethod
    def _find_user_by_email(email: str) -> Optional[Dict]:
        """이메일로 사용자 찾기"""
        try:
            users_ref = db.collection('users')
            query = users_ref\
                .where('email', '==', email)\
                .where('is_active', '==', True)\
                .limit(1)\
                .get()
            
            if query:
                return query[0].to_dict()
            return None
        except Exception as e:
            print(f"[ERROR] 이메일 사용자 조회 실패: {str(e)}")
            return None
    
    @staticmethod
    def find_user_id_by_name_and_email(username: str, email: str) -> Optional[Dict]:
        """이름과 이메일로 사용자 찾기 (아이디 찾기용 - 이메일 계정만)"""
        try:
            users_ref = db.collection('users')
            
            # 이름과 이메일이 모두 일치하는 사용자 검색
            query = users_ref\
                .where('username', '==', username)\
                .where('email', '==', email)\
                .where('is_active', '==', True)\
                .limit(1)\
                .get()
            
            if query:
                return query[0].to_dict()
            
            return None
        except Exception as e:
            print(f"[ERROR] 아이디 찾기 실패: {str(e)}")
            return None
    
    @staticmethod
    def verify_user_for_password_reset(username: str, user_id: str, email: str) -> Optional[Dict]:
        """비밀번호 재설정을 위한 사용자 확인 - 이름, 아이디, 이메일 모두 확인 (이메일 계정만)"""
        try:
            users_ref = db.collection('users')
            
            # 이름, user_id, 이메일이 모두 일치하는 사용자 검색
            query = users_ref\
                .where('username', '==', username)\
                .where('user_id', '==', user_id)\
                .where('email', '==', email)\
                .where('is_active', '==', True)\
                .limit(1)\
                .get()
            
            if query:
                return query[0].to_dict()
            
            return None
        except Exception as e:
            print(f"[ERROR] 비밀번호 재설정 사용자 확인 실패: {str(e)}")
            return None
    
    # ===== JWT 토큰 관련 메서드 =====
    
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
            "iat": datetime.utcnow(),
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
            "iat": datetime.utcnow(),
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
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
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
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="리프레시 토큰이 만료되었습니다"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="리프레시 토큰 검증에 실패했습니다"
            )
    
    # ===== 비밀번호 재설정 관련 메서드 =====
    
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
            print("[INFO] 비밀번호 재설정 토큰 만료")
            return None
        except JWTError as e:
            print(f"[ERROR] 비밀번호 재설정 토큰 검증 실패: {str(e)}")
            return None
        except Exception as e:
            print(f"[ERROR] 비밀번호 재설정 토큰 검증 오류: {str(e)}")
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
            "type": "password_reset_access",
            "permissions": ["change_password"]
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
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰 검증에 실패했습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # ===== 계정 관리 메서드 =====
    
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
            
            # 2. 비밀번호 확인 (이메일 계정만)
            if user.get("auth_type") == AuthType.EMAIL.value:
                if not user.get("hashed_password") or not FirebaseUserService.verify_password(password, user["hashed_password"]):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="비밀번호가 올바르지 않습니다"
                    )
            # SNS 계정의 경우 비밀번호 확인 생략
            
            user_uuid = user["id"]
            farm_id = user["farm_id"]
            
            print(f"[INFO] 계정 삭제 시작: {user['username']} ({user['user_id']})")
            
            # 3. 관련 데이터 삭제 (순서 중요)
            
            # 3-1. 할일(Tasks) 삭제
            tasks = db.collection('tasks').where('farm_id', '==', farm_id).get()
            task_count = len(tasks)
            for task in tasks:
                db.collection('tasks').document(task.id).delete()
            
            # 3-2. 채팅방 삭제
            chat_rooms = db.collection('chat_rooms').where('farm_id', '==', farm_id).get()
            chat_count = len(chat_rooms)
            for chat in chat_rooms:
                db.collection('chat_rooms').document(chat.id).delete()
            
            # 3-3. 상세기록 삭제
            detailed_records = db.collection('cow_detailed_records').where('farm_id', '==', farm_id).get()
            detailed_count = len(detailed_records)
            for record in detailed_records:
                db.collection('cow_detailed_records').document(record.id).delete()
            
            # 3-4. 기록 삭제  
            records = db.collection('cow_records').where('farm_id', '==', farm_id).get()
            record_count = len(records)
            for record in records:
                db.collection('cow_records').document(record.id).delete()
            
            # 3-5. 소 정보 삭제
            cows = db.collection('cows').where('farm_id', '==', farm_id).get()
            cow_count = len(cows)
            for cow in cows:
                db.collection('cows').document(cow.id).delete()
            
            # 3-6. 리프레시 토큰 삭제 (해당 사용자의 모든 토큰)
            refresh_tokens = db.collection('refresh_tokens').where('user_id', '==', user_uuid).get()
            token_count = len(refresh_tokens)
            for token in refresh_tokens:
                db.collection('refresh_tokens').document(token.id).delete()
            
            # 3-7. 농장 정보 삭제
            db.collection('farms').document(farm_id).delete()
            
            # 3-8. 사용자 정보 삭제 (마지막)
            db.collection('users').document(user_uuid).delete()
            
            print(f"[INFO] 계정 삭제 완료: 젖소 {cow_count}마리, 기록 {record_count + detailed_count}개, 할일 {task_count}개, 채팅 {chat_count}개, 토큰 {token_count}개")
            
            return {
                "success": True,
                "message": f"{user['username']}님의 계정이 완전히 삭제되었습니다",
                "deleted_data": {
                    "user": user['username'],
                    "user_id": user['user_id'],
                    "farm_id": farm_id,
                    "auth_type": user['auth_type'],
                    "deleted_cows": cow_count,
                    "deleted_records": record_count + detailed_count,
                    "deleted_tasks": task_count,
                    "deleted_chats": chat_count,
                    "deleted_tokens": token_count,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            print(f"[ERROR] 계정 삭제 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"계정 삭제 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def update_user_profile(user_id: str, username: Optional[str] = None, farm_nickname: Optional[str] = None) -> Dict:
        """사용자 프로필 업데이트"""
        try:
            user = FirebaseUserService.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다"
                )
            
            update_data = {
                "updated_at": datetime.utcnow()
            }
            
            # 사용자 이름 업데이트
            if username is not None:
                update_data["username"] = username
                
                # 농장 정보도 함께 업데이트
                db.collection('farms').document(user["farm_id"]).update({
                    "owner_name": username,
                    "updated_at": datetime.utcnow()
                })
            
            # 목장 별명 업데이트
            if farm_nickname is not None:
                update_data["farm_nickname"] = farm_nickname
                
                # 농장 정보도 함께 업데이트
                db.collection('farms').document(user["farm_id"]).update({
                    "farm_nickname": farm_nickname,
                    "updated_at": datetime.utcnow()
                })
            
            # 사용자 정보 업데이트
            db.collection('users').document(user_id).update(update_data)
            
            # 업데이트된 사용자 정보 반환
            updated_user = FirebaseUserService.get_user_by_id(user_id)
            updated_user.pop('hashed_password', None)  # 비밀번호 제외
            
            return {
                "success": True,
                "message": "프로필이 성공적으로 업데이트되었습니다",
                "user": updated_user
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            print(f"[ERROR] 프로필 업데이트 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"프로필 업데이트 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def get_user_statistics(user_id: str) -> Dict:
        """사용자 통계 정보 조회"""
        try:
            user = FirebaseUserService.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다"
                )
            
            farm_id = user["farm_id"]
            
            # 젖소 수 조회
            cows = db.collection('cows').where('farm_id', '==', farm_id).where('is_active', '==', True).get()
            total_cows = len(cows)
            
            # 기록 수 조회
            records = db.collection('cow_records').where('farm_id', '==', farm_id).where('is_active', '==', True).get()
            detailed_records = db.collection('cow_detailed_records').where('farm_id', '==', farm_id).where('is_active', '==', True).get()
            total_records = len(records) + len(detailed_records)
            
            # 가입 후 경과일 계산
            created_at = user["created_at"]
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            days_since_registration = (datetime.utcnow() - created_at).days
            
            # 마지막 활동 시간 (최근 기록 생성 시간)
            last_activity = None
            if records or detailed_records:
                all_records = []
                for record in records:
                    all_records.append(record.to_dict().get('created_at'))
                for record in detailed_records:
                    all_records.append(record.to_dict().get('created_at'))
                
                if all_records:
                    last_activity = max(filter(None, all_records))
            
            return {
                "total_cows": total_cows,
                "total_records": total_records,
                "last_activity": last_activity,
                "farm_created_at": created_at,
                "days_since_registration": days_since_registration,
                "auth_type": user["auth_type"],
                "last_login": user.get("last_login")
            }
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            print(f"[ERROR] 사용자 통계 조회 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"사용자 통계 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    # ===== 관리자용 메서드 =====
    
    @staticmethod
    def get_all_users(limit: int = 100, auth_type: Optional[AuthType] = None) -> List[Dict]:
        """모든 사용자 조회 (관리자용)"""
        try:
            query = db.collection('users').where('is_active', '==', True)
            
            if auth_type:
                query = query.where('auth_type', '==', auth_type.value)
            
            users = query.order_by('created_at', direction='DESCENDING').limit(limit).get()
            
            result = []
            for user_doc in users:
                user_data = user_doc.to_dict()
                user_data.pop('hashed_password', None)  # 비밀번호 제외
                result.append(user_data)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] 전체 사용자 조회 실패: {str(e)}")
            return []
    
    @staticmethod
    def get_user_count_by_auth_type() -> Dict[str, int]:
        """인증 타입별 사용자 수 조회"""
        try:
            stats = {}
            
            for auth_type in AuthType:
                count = len(db.collection('users')
                           .where('auth_type', '==', auth_type.value)
                           .where('is_active', '==', True)
                           .get())
                stats[auth_type.value] = count
            
            return stats
            
        except Exception as e:
            print(f"[ERROR] 인증 타입별 통계 조회 실패: {str(e)}")
            return {}
    
    # ===== 유틸리티 메서드 =====
    
    @staticmethod
    def cleanup_expired_tokens():
        """만료된 리프레시 토큰 정리"""
        try:
            current_time = datetime.utcnow()
            
            # 만료된 토큰 조회 (단순 쿼리)
            expired_tokens = db.collection('refresh_tokens')\
                .where('expires_at', '<', current_time)\
                .get()
            
            deleted_count = 0
            
            # 배치 삭제 (효율성을 위해)
            for token in expired_tokens:
                try:
                    db.collection('refresh_tokens').document(token.id).delete()
                    deleted_count += 1
                except Exception as e:
                    print(f"[WARNING] 토큰 삭제 실패 (ID: {token.id}): {str(e)}")
            
            print(f"[INFO] 만료된 토큰 {deleted_count}개 정리 완료")
            return deleted_count
            
        except Exception as e:
            print(f"[ERROR] 토큰 정리 실패: {str(e)}")
            return 0
    
    @staticmethod
    def cleanup_old_tokens_by_count():
        """사용자별 오래된 토큰 정리 (각 사용자당 최대 5개만 유지)"""
        try:
            # 모든 활성 사용자 조회
            users = db.collection('users').where('is_active', '==', True).get()
            total_deleted = 0
            
            for user_doc in users:
                user_id = user_doc.id
                
                try:
                    # 사용자의 모든 토큰 조회 (간단한 쿼리)
                    user_tokens = db.collection('refresh_tokens')\
                        .where('user_id', '==', user_id)\
                        .get()
                    
                    # 토큰을 생성일 기준으로 정렬 (메모리에서)
                    token_list = []
                    for token_doc in user_tokens:
                        token_data = token_doc.to_dict()
                        token_data['doc_id'] = token_doc.id
                        if token_data.get('is_active', True):  # 활성 토큰만
                            token_list.append(token_data)
                    
                    # 생성일 기준 내림차순 정렬
                    token_list.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
                    
                    # 5개 이상이면 오래된 것들 삭제
                    if len(token_list) > 5:
                        tokens_to_delete = token_list[5:]  # 6번째부터 끝까지
                        
                        for token in tokens_to_delete:
                            try:
                                db.collection('refresh_tokens').document(token['doc_id']).delete()
                                total_deleted += 1
                            except Exception as e:
                                print(f"[WARNING] 토큰 삭제 실패: {str(e)}")
                                
                except Exception as e:
                    print(f"[WARNING] 사용자 {user_id} 토큰 정리 실패: {str(e)}")
                    continue
            
            print(f"[INFO] 오래된 토큰 {total_deleted}개 정리 완료 (사용자당 최대 5개 유지)")
            return total_deleted
            
        except Exception as e:
            print(f"[ERROR] 오래된 토큰 정리 실패: {str(e)}")
            return 0
    
    @staticmethod
    def auto_cleanup_tokens():
        """자동 토큰 정리 (만료된 것 + 개수 제한)"""
        try:
            expired_deleted = FirebaseUserService.cleanup_expired_tokens()
            old_deleted = FirebaseUserService.cleanup_old_tokens_by_count()
            
            total_deleted = expired_deleted + old_deleted
            print(f"[INFO] 자동 토큰 정리 완료: 총 {total_deleted}개 삭제")
            
            return {
                "total_deleted": total_deleted,
                "expired_deleted": expired_deleted,
                "old_deleted": old_deleted,
                "cleanup_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] 자동 토큰 정리 실패: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def get_token_statistics():
        """토큰 통계 조회"""
        try:
            current_time = datetime.utcnow()
            
            # 전체 토큰 수
            all_tokens = db.collection('refresh_tokens').get()
            total_count = len(all_tokens)
            
            # 활성 토큰 수
            active_tokens = db.collection('refresh_tokens').where('is_active', '==', True).get()
            active_count = len(active_tokens)
            
            # 만료된 토큰 수
            expired_tokens = db.collection('refresh_tokens')\
                .where('expires_at', '<', current_time)\
                .get()
            expired_count = len(expired_tokens)
            
            return {
                "total_tokens": total_count,
                "active_tokens": active_count,
                "expired_tokens": expired_count,
                "inactive_tokens": total_count - active_count,
                "cleanup_needed": expired_count > 0,
                "statistics_time": current_time.isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] 토큰 통계 조회 실패: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def revoke_all_user_tokens(user_id: str):
        """특정 사용자의 모든 토큰 무효화"""
        try:
            tokens = db.collection('refresh_tokens').where('user_id', '==', user_id).get()
            
            revoked_count = 0
            for token in tokens:
                db.collection('refresh_tokens').document(token.id).update({
                    'is_active': False,
                    'revoked_at': datetime.utcnow(),
                    'revoked_reason': 'manual_revoke'
                })
                revoked_count += 1
            
            print(f"[INFO] 사용자 {user_id}의 토큰 {revoked_count}개 무효화 완료")
            return revoked_count
            
        except Exception as e:
            print(f"[ERROR] 토큰 무효화 실패: {str(e)}")
            return 0