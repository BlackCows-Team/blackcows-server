# migrations/migrate_farm_nickname.py

from datetime import datetime
from config.firebase_config import get_firestore_client

def migrate_database():
    """
    데이터베이스 마이그레이션: farm_name → farm_nickname
    개발 단계에서 필드명 변경 적용
    """
    try:
        db = get_firestore_client()
        
        print("🚀 데이터베이스 마이그레이션 시작...")
        print("=" * 50)
        
        # 1. 기존 사용자 데이터 확인
        print("📋 기존 사용자 데이터 확인 중...")
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        user_count = 0
        updated_count = 0
        
        for user_doc in users:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            user_count += 1
            
            print(f"  📄 사용자 {user_id} 처리 중...")
            
            # farm_name이 있고 farm_nickname이 없는 경우
            if 'farm_name' in user_data and 'farm_nickname' not in user_data:
                # farm_name → farm_nickname으로 변경
                update_data = {
                    'farm_nickname': user_data['farm_name'],
                    'updated_at': datetime.utcnow()
                }
                
                # farm_name 필드 삭제
                from google.cloud import firestore
                update_data['farm_name'] = firestore.DELETE_FIELD
                
                # 업데이트 실행
                users_ref.document(user_id).update(update_data)
                
                print(f"    ✅ farm_name '{user_data['farm_name']}' → farm_nickname 변경 완료")
                updated_count += 1
                
            elif 'farm_nickname' in user_data:
                print(f"    ✅ 이미 farm_nickname 필드 존재: '{user_data.get('farm_nickname')}'")
            
            else:
                print(f"    ⚠️ farm_name/farm_nickname 필드 없음 - 건너뛰기")
        
        # 2. farms 컬렉션도 동일하게 처리
        print("\n📋 farms 컬렉션 처리 중...")
        farms_ref = db.collection('farms')
        farms = farms_ref.stream()
        
        farm_count = 0
        farm_updated_count = 0
        
        for farm_doc in farms:
            farm_data = farm_doc.to_dict()
            farm_id = farm_doc.id
            farm_count += 1
            
            print(f"  📄 농장 {farm_id} 처리 중...")
            
            if 'farm_name' in farm_data and 'farm_nickname' not in farm_data:
                from google.cloud import firestore
                update_data = {
                    'farm_nickname': farm_data['farm_name'],
                    'updated_at': datetime.utcnow(),
                    'farm_name': firestore.DELETE_FIELD
                }
                
                farms_ref.document(farm_id).update(update_data)
                print(f"    ✅ 농장 farm_name → farm_nickname 변경 완료")
                farm_updated_count += 1
            else:
                print(f"    ✅ 농장 이미 올바른 스키마")
        
        # 3. 결과 요약
        print("\n" + "=" * 50)
        print("📊 마이그레이션 결과:")
        print(f"   👥 사용자: {user_count}명 확인, {updated_count}명 업데이트")
        print(f"   🏡 농장: {farm_count}개 확인, {farm_updated_count}개 업데이트")
        print("✅ 마이그레이션 완료!")
        
        return True
        
    except Exception as e:
        print(f"❌ 마이그레이션 오류: {e}")
        return False

def rollback_migration():
    """마이그레이션 롤백: farm_nickname → farm_name"""
    try:
        db = get_firestore_client()
        
        print("🔄 마이그레이션 롤백 시작...")
        
        # 사용자 데이터 롤백
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        for user_doc in users:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            
            if 'farm_nickname' in user_data:
                from google.cloud import firestore
                update_data = {
                    'farm_name': user_data['farm_nickname'],
                    'updated_at': datetime.utcnow(),
                    'farm_nickname': firestore.DELETE_FIELD
                }
                
                users_ref.document(user_id).update(update_data)
                print(f"🔄 사용자 {user_id} 롤백 완료")
        
        print("✅ 롤백 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 롤백 오류: {e}")
        return False

def verify_migration():
    """마이그레이션 결과 검증"""
    try:
        db = get_firestore_client()
        
        print("🔍 마이그레이션 결과 검증 중...")
        
        # 사용자 데이터 검증
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        farm_name_count = 0
        farm_nickname_count = 0
        
        for user_doc in users:
            user_data = user_doc.to_dict()
            
            if 'farm_name' in user_data:
                farm_name_count += 1
                print(f"⚠️ 아직 farm_name 필드가 있는 사용자: {user_doc.id}")
            
            if 'farm_nickname' in user_data:
                farm_nickname_count += 1
        
        print(f"📊 검증 결과:")
        print(f"   - farm_name 필드 보유: {farm_name_count}명")
        print(f"   - farm_nickname 필드 보유: {farm_nickname_count}명")
        
        if farm_name_count == 0:
            print("✅ 모든 사용자가 새로운 스키마 적용됨")
        else:
            print("⚠️ 일부 사용자에게 아직 구 스키마가 남아있음")
        
        return farm_name_count == 0
        
    except Exception as e:
        print(f"❌ 검증 오류: {e}")
        return False

if __name__ == "__main__":
    print("Firebase 데이터베이스 마이그레이션 도구")
    print("=" * 40)
    print("1. 마이그레이션 실행 (farm_name → farm_nickname)")
    print("2. 마이그레이션 롤백 (farm_nickname → farm_name)")
    print("3. 마이그레이션 결과 검증")
    print()
    
    choice = input("선택하세요 (1/2/3): ").strip()
    
    if choice == "1":
        confirm = input("⚠️ 데이터베이스를 변경합니다. 계속하시겠습니까? (yes/no): ")
        if confirm.lower() == "yes":
            migrate_database()
        else:
            print("❌ 마이그레이션 취소됨")
    
    elif choice == "2":
        confirm = input("⚠️ 롤백을 실행하시겠습니까? (yes/no): ")
        if confirm.lower() == "yes":
            rollback_migration()
        else:
            print("❌ 롤백 취소됨")
    
    elif choice == "3":
        verify_migration()
    
    else:
        print("❌ 잘못된 선택입니다.")