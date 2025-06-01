# 로직분리

def get_cow_list():
    return [
        {"name": "꽃분이 젖소", "id": "12345", "number": "123", "sensor": "221108", "date": "2024-01-25", "status": "양호", "milk": "34L", "birthdate": "2024-05-24", "breed": "BlackCow"},
        {"name": "보균이", "id": "cow2", "number": "1014", "sensor": "221105", "date": "2021-01-05", "status": "양호", "milk": "20L", "birthdate": "2000-10-14", "breed": "Holstein"},
        {"name": "민지", "id": "cow3", "number": "0102", "sensor": "221106", "date": "2022-01-02", "status": "양호", "milk": "10L", "birthdate": "2002-01-02", "breed": "Hanwoo"},
        {"name": "슬기", "id": "cow4", "number": "0117", "sensor": "221107", "date": "2023-01-06", "status": "양호", "milk": "6L", "birthdate": "2002-01-17", "breed": "Dairy"},
        
    ]
# {
#         'name': '이름',
#         'id': '12345', 또는 "cow1"
#         'sensor': '센서번호 - 221105',
#         'date': '등록일자 - 24.1.25',
#         'status': '건강양호 - 양호',
#         'milk': '최근 착유량 - 34L',
#       },