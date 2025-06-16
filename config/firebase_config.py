import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    # JSON 파일 경로 사용
    json_path = os.path.join(os.path.dirname(__file__), 'blackcows-db-8b26f-firebase-adminsdk-fbsvc-7400a4a090.json')
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Firebase service account key not found: {json_path}")
    
    cred = credentials.Certificate(json_path)
    
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

# Firestore 클라이언트 인스턴스
db = initialize_firebase()

def get_firestore_client():
    return db
