# services/social_auth_service.py

import httpx
import json
from typing import Optional, Dict, List
from fastapi import HTTPException, status
from schemas.user import AuthType, SocialUserInfo
import os

class SocialAuthService:
    """SNS 플랫폼별 인증 처리 서비스 (Google, Kakao, Naver 지원)"""
    
    @staticmethod
    async def get_google_user_info(access_token: str, id_token: Optional[str] = None) -> SocialUserInfo:
        """구글 사용자 정보 조회"""
        try:
            # Google People API 사용
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    print(f"[ERROR] 구글 API 응답 오류: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="구글 액세스 토큰이 유효하지 않습니다"
                    )
                
                user_data = response.json()
                
                print(f"[INFO] 구글 사용자 정보 조회 성공: {user_data.get('email')}")
                
                return SocialUserInfo(
                    social_id=user_data.get("id"),
                    email=user_data.get("email"),
                    name=user_data.get("name")
                )
                
        except httpx.TimeoutException:
            print("[ERROR] 구글 API 호출 타임아웃")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="구글 서버 응답 시간 초과"
            )
        except Exception as e:
            print(f"[ERROR] 구글 사용자 정보 조회 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="구글 사용자 정보를 가져올 수 없습니다"
            )
    
    @staticmethod
    async def get_kakao_user_info(access_token: str) -> SocialUserInfo:
        """카카오 사용자 정보 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    print(f"[ERROR] 카카오 API 응답 오류: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="카카오 액세스 토큰이 유효하지 않습니다"
                    )
                
                user_data = response.json()
                
                # 카카오 응답 구조 파싱
                kakao_account = user_data.get("kakao_account", {})
                profile = kakao_account.get("profile", {})
                
                print(f"[INFO] 카카오 사용자 정보 조회 성공: {kakao_account.get('email')}")
                
                return SocialUserInfo(
                    social_id=str(user_data.get("id")),
                    email=kakao_account.get("email"),
                    name=profile.get("nickname")
                )
                
        except httpx.TimeoutException:
            print("[ERROR] 카카오 API 호출 타임아웃")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="카카오 서버 응답 시간 초과"
            )
        except Exception as e:
            print(f"[ERROR] 카카오 사용자 정보 조회 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카카오 사용자 정보를 가져올 수 없습니다"
            )
    
    @staticmethod
    async def get_naver_user_info(access_token: str) -> SocialUserInfo:
        """네이버 사용자 정보 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://openapi.naver.com/v1/nid/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    print(f"[ERROR] 네이버 API 응답 오류: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="네이버 액세스 토큰이 유효하지 않습니다"
                    )
                
                user_data = response.json()
                
                # 네이버 응답 구조 파싱
                response_data = user_data.get("response", {})
                
                print(f"[INFO] 네이버 사용자 정보 조회 성공: {response_data.get('email')}")
                
                return SocialUserInfo(
                    social_id=response_data.get("id"),
                    email=response_data.get("email"),
                    name=response_data.get("name")
                )
                
        except httpx.TimeoutException:
            print("[ERROR] 네이버 API 호출 타임아웃")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="네이버 서버 응답 시간 초과"
            )
        except Exception as e:
            print(f"[ERROR] 네이버 사용자 정보 조회 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="네이버 사용자 정보를 가져올 수 없습니다"
            )
    
    @staticmethod
    async def get_social_user_info(auth_type: AuthType, access_token: str, id_token: Optional[str] = None) -> SocialUserInfo:
        """플랫폼별 사용자 정보 조회 통합 메서드 (Google, Kakao, Naver 지원)"""
        
        print(f"[INFO] SNS 사용자 정보 조회 시작: {auth_type.value}")
        
        if auth_type == AuthType.GOOGLE:
            return await SocialAuthService.get_google_user_info(access_token, id_token)
        
        elif auth_type == AuthType.KAKAO:
            return await SocialAuthService.get_kakao_user_info(access_token)
        
        elif auth_type == AuthType.NAVER:
            return await SocialAuthService.get_naver_user_info(access_token)
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 인증 타입입니다: {auth_type.value}. 지원 플랫폼: Google, Kakao, Naver"
            )
    
    @staticmethod
    def generate_unique_user_id(social_info: SocialUserInfo, auth_type: AuthType) -> str:
        """SNS 사용자를 위한 고유 user_id 생성"""
        import uuid
        
        # 기본 전략: 플랫폼명 + 일부 social_id + 랜덤
        social_id_short = social_info.social_id[:8] if social_info.social_id else ""
        random_suffix = str(uuid.uuid4())[:8]
        
        if auth_type == AuthType.GOOGLE:
            prefix = "google"
        elif auth_type == AuthType.KAKAO:
            prefix = "kakao"
        elif auth_type == AuthType.NAVER:
            prefix = "naver"
        else:
            prefix = "social"
        
        user_id = f"{prefix}_{social_id_short}_{random_suffix}"
        
        print(f"[INFO] SNS 사용자 ID 생성: {user_id}")
        return user_id
    
    @staticmethod
    def generate_default_farm_nickname(name: Optional[str], auth_type: AuthType) -> str:
        """기본 목장 별명 생성"""
        platform_names = {
            AuthType.GOOGLE: "구글",
            AuthType.KAKAO: "카카오",
            AuthType.NAVER: "네이버"
        }
        
        platform_name = platform_names.get(auth_type, "소셜")
        
        if name:
            farm_nickname = f"{name}님의 목장 ({platform_name} 로그인)"
        else:
            farm_nickname = f"{platform_name} 사용자의 목장"
        
        print(f"[INFO] 기본 목장 별명 생성: {farm_nickname}")
        return farm_nickname
    
    @staticmethod
    def validate_auth_type(auth_type: str) -> bool:
        """지원하는 인증 타입인지 확인"""
        supported_types = [AuthType.GOOGLE.value, AuthType.KAKAO.value, AuthType.NAVER.value]
        return auth_type in supported_types
    
    @staticmethod
    def get_supported_platforms() -> List[str]:
        """지원하는 플랫폼 목록 반환"""
        return ["google", "kakao", "naver"]
    
    @staticmethod
    def get_platform_display_name(auth_type: AuthType) -> str:
        """플랫폼의 한국어 표시명 반환"""
        platform_names = {
            AuthType.GOOGLE: "구글",
            AuthType.KAKAO: "카카오",
            AuthType.NAVER: "네이버"
        }
        return platform_names.get(auth_type, auth_type.value)