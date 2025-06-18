import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    """Firebase 초기화"""
    json_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not json_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS 환경변수가 설정되지 않았습니다.")
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Firebase service account key not found: {json_path}")
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(json_path)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

db = initialize_firebase()

def get_firestore_client():
    return db
