from fastapi import APIRouter
from schemas.cow import Cow
from services.cow_service import get_cow_list

router = APIRouter()

# API 정의
@router.get("/")
def list_cows():
    return get_cow_list()
    # return [
    #     {"name": "보균이", "id": "cow1", "number": "1014", "birthdate": "2000-10-14", "breed": "Holstein"},
    #     {"name": "민지", "id": "cow2", "number": "0102", "birthdate": "2002-01-02", "breed": "Hanwoo"},
    #     {"name": "슬기", "id": "cow3", "number": "0117", "birthdate": "2002-01-17", "breed": "Dairy"},
    #     {"name": "흑우~", "id": "cow4", "number": "123", "birthdate": "2024-05-24", "breed": "BlackCow"},
    # ]

