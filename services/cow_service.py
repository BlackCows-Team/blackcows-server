# 기존 호환성을 위한 레거시 서비스
# 새로운 기능은 cow_firebase_service.py를 사용하세요

def get_cow_list():
    """기존 하드코딩된 젖소 목록 (레거시 지원용)"""
    return [
        {
            "name": "꽃분이 젖소", 
            "id": "12345", 
            "number": "123", 
            "sensor": "221108", 
            "date": "2024-01-25", 
            "status": "양호", 
            "milk": "34L", 
            "birthdate": "2024-05-24", 
            "breed": "BlackCow"
        },
        {
            "name": "보균이", 
            "id": "cow2", 
            "number": "1014", 
            "sensor": "221105", 
            "date": "2021-01-05", 
            "status": "양호", 
            "milk": "20L", 
            "birthdate": "2000-10-14", 
            "breed": "Holstein"
        },
        {
            "name": "민지", 
            "id": "cow3", 
            "number": "0102", 
            "sensor": "221106", 
            "date": "2022-01-02", 
            "status": "양호", 
            "milk": "10L", 
            "birthdate": "2002-01-02", 
            "breed": "Hanwoo"
        },
        {
            "name": "슬기", 
            "id": "cow4", 
            "number": "0117", 
            "sensor": "221107", 
            "date": "2023-01-06", 
            "status": "양호", 
            "milk": "6L", 
            "birthdate": "2002-01-17", 
            "breed": "Dairy"
        },
        {
            "name": "두리", 
            "id": "cow5", 
            "number": "0825", 
            "sensor": "221109", 
            "date": "2025-06-02", 
            "status": "양호", 
            "milk": "0L", 
            "birthdate": "2019-08-25", 
            "breed": "Bichon Frise"
        },        
    ]