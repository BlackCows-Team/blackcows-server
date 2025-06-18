import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    """Firebase 초기화 - 환경변수 기반"""
    
    # 방법 1: JSON 파일 경로를 사용하는 경우
    json_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if json_path and os.path.exists(json_path):
        if not firebase_admin._apps:
            cred = credentials.Certificate(json_path)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    
    # 방법 2: 환경변수에서 직접 Firebase 설정 읽기
    project_id = os.getenv('FIREBASE_PROJECT_ID')
    private_key_id = os.getenv('FIREBASE_PRIVATE_KEY_ID')
    private_key = os.getenv('FIREBASE_PRIVATE_KEY')
    client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
    client_id = os.getenv('FIREBASE_CLIENT_ID')
    
    if all([project_id, private_key_id, private_key, client_email, client_id]):
        # 환경변수에서 JSON 형태로 구성
        firebase_config = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key.replace('\\n', '\n'),  # 개행 문자 처리
            "client_email": client_email,
            "client_id": client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}"
        }
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    
    # 둘 다 없으면 에러
    raise ValueError(
        "Firebase 설정이 없습니다. 다음 중 하나를 설정하세요:\n"
        "1. GOOGLE_APPLICATION_CREDENTIALS 환경변수 (JSON 파일 경로)\n"
        "2. Firebase 개별 환경변수들 (FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY 등)"
    )

# 전역 변수로 설정
try:
    db = initialize_firebase()
except Exception as e:
    print(f"Firebase 초기화 실패: {e}")
    db = None

def get_firestore_client():
    if db is None:
        raise ValueError("Firebase가 초기화되지 않았습니다.")
    return db