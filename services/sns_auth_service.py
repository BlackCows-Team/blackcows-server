# services/sns_auth_service.py

import requests
import json
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from datetime import datetime
import firebase_admin
from firebase_admin import auth, credentials
from config.firebase_config import get_firestore_client
import uuid

class SNSAuthService:
    """SNS 로그인 및 회원 탈퇴 서비스"""
    
    @staticmethod
    def verify_google_token(id_token: str) -> Dict[str, Any]:
        """구글 ID 토큰 검증"""
        try:
            # Firebase Admin SDK를 사용하여 구글 토큰 검증
            decoded_token = auth.verify_id_token(id_token)
            
            return {
                "sns_user_id": decoded_token.get("sub"),
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
                "provider": "google"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"구글 토큰 검증 실패: {str(e)}"
            )
    
    @staticmethod
    def verify_kakao_token(access_token: str) -> Dict[str, Any]:
        """카카오 액세스 토큰 검증"""
        try:
            # 카카오 사용자 정보 조회
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="카카오 토큰 검증 실패"
                )
            
            user_data = response.json()
            
            return {
                "sns_user_id": str(user_data.get("id")),
                "email": user_data.get("kakao_account", {}).get("email"),
                "name": user_data.get("properties", {}).get("nickname"),
                "picture": user_data.get("properties", {}).get("profile_image"),
                "provider": "kakao"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"카카오 토큰 검증 실패: {str(e)}"
            )
    
    @staticmethod
    def verify_naver_token(access_token: str) -> Dict[str, Any]:
        """네이버 액세스 토큰 검증"""
        try:
            # 네이버 사용자 정보 조회
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://openapi.naver.com/v1/nid/me", headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="네이버 토큰 검증 실패"
                )
            
            user_data = response.json().get("response", {})
            
            return {
                "sns_user_id": user_data.get("id"),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "picture": user_data.get("profile_image"),
                "provider": "naver"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"네이버 토큰 검증 실패: {str(e)}"
            )
    
    @staticmethod
    def create_or_get_sns_user(sns_data: Dict[str, Any], farm_nickname: Optional[str] = None) -> Dict[str, Any]:
        """SNS 사용자 생성 또는 기존 사용자 조회"""
        try:
            db = get_firestore_client()
            
            # SNS 사용자 ID로 기존 사용자 검색
            existing_user = db.collection('users').where('sns_user_id', '==', sns_data["sns_user_id"]).where('sns_provider', '==', sns_data["provider"]).limit(1).get()
            
            if existing_user:
                # 기존 사용자 반환
                user_data = existing_user[0].to_dict()
                if not user_data.get("is_active", True):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="비활성화된 계정입니다"
                    )
                return user_data
            
            # 새 사용자 생성
            user_uuid = str(uuid.uuid4())
            farm_id = f"farm_{user_uuid[:8]}"
            
            user_data = {
                "id": user_uuid,
                "username": sns_data["name"] or "사용자",
                "user_id": f"{sns_data['provider']}_{sns_data['sns_user_id']}",  # SNS 기반 user_id 생성
                "email": sns_data["email"],
                "farm_nickname": farm_nickname or f"{sns_data['name']}님의 목장",
                "farm_id": farm_id,
                "login_type": sns_data["provider"],
                "sns_provider": sns_data["provider"],
                "sns_user_id": sns_data["sns_user_id"],
                "sns_profile_image": sns_data.get("picture"),
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Firestore에 사용자 저장
            db.collection('users').document(user_uuid).set(user_data)
            
            # 목장 정보도 별도 컬렉션에 저장
            farm_data = {
                "farm_id": farm_id,
                "farm_nickname": farm_nickname or f"{sns_data['name']}님의 목장",
                "owner_id": user_uuid,
                "owner_name": sns_data["name"],
                "owner_user_id": user_data["user_id"],
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            db.collection('farms').document(farm_id).set(farm_data)
            
            return user_data
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SNS 사용자 생성 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def delete_sns_user_account(user: Dict[str, Any], sns_provider: str, sns_token: str) -> Dict[str, Any]:
        """SNS 사용자 계정 삭제"""
        try:
            db = get_firestore_client()
            user_id = user["id"]
            farm_id = user["farm_id"]
            
            # 1. SNS 제공자별 계정 연결 해제
            if sns_provider == "google":
                # 구글 계정 연결 해제 (Firebase Auth에서 삭제)
                try:
                    firebase_user = auth.get_user_by_email(user["email"])
                    auth.delete_user(firebase_user.uid)
                except:
                    pass  # Firebase Auth에 없는 경우 무시
            
            elif sns_provider == "kakao":
                # 카카오 계정 연결 해제
                try:
                    headers = {"Authorization": f"Bearer {sns_token}"}
                    response = requests.post("https://kapi.kakao.com/v1/user/unlink", headers=headers)
                except:
                    pass  # 연결 해제 실패해도 계속 진행
            
            elif sns_provider == "naver":
                # 네이버 계정 연결 해제
                try:
                    import os
                    naver_client_id = os.getenv("NAVER_CLIENT_ID")
                    naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
                    
                    if naver_client_id and naver_client_secret:
                        headers = {"Authorization": f"Bearer {sns_token}"}
                        response = requests.post("https://nid.naver.com/oauth2.0/token", params={
                            "grant_type": "delete",
                            "client_id": naver_client_id,
                            "client_secret": naver_client_secret,
                            "access_token": sns_token
                        })
                except:
                    pass  # 연결 해제 실패해도 계속 진행
            
            # 2. 관련 데이터 삭제
            # 사용자 관련 모든 데이터 삭제
            collections_to_delete = [
                'cow_records', 'cow_detailed_records', 'cows', 'refresh_tokens'
            ]
            
            for collection_name in collections_to_delete:
                docs = db.collection(collection_name).where('farm_id', '==', farm_id).get()
                for doc in docs:
                    doc.reference.delete()
            
            # 사용자 문서 삭제
            db.collection('users').document(user_id).delete()
            
            # 목장 문서 삭제
            db.collection('farms').document(farm_id).delete()
            
            return {
                "success": True,
                "message": f"{user['username']}님의 계정이 성공적으로 삭제되었습니다",
                "deleted_at": datetime.utcnow().isoformat(),
                "deleted_data": {
                    "user_id": user_id,
                    "farm_id": farm_id,
                    "sns_provider": sns_provider
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SNS 사용자 계정 삭제 중 오류가 발생했습니다: {str(e)}"
            ) 