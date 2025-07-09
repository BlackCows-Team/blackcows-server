import re
from config.firebase_config import get_firestore_client
from services.detailed_record_service import DetailedRecordService
from .types import DairyChatState, append_chat_memory

def extract_ear_tag_number(question: str) -> str | None:
    """질문에서 12자리 이표번호를 추출하는 함수"""
    match = re.search(r'\b\d{12}\b', question)
    return match.group(0) if match else None

def extract_record_type(question: str) -> str | None:
    """질문에서 기록 유형을 추출하는 함수"""
    if "착유" in question or "우유" in question:
        return "milking"
    if "발정" in question:
        return "estrus"
    if "건강" in question or "질병" in question:
        return "health_check"
    if "백신" in question:
        return "vaccination"
    if "체중" in question or "무게" in question:
        return "weight"
    if "사료" in question:
        return "feed"
    if "임신" in question:
        return "pregnancy_check"
    if "분만" in question:
        return "calving"
    if "치료" in question:
        return "treatment"
    # 필요시 추가
    return None

def get_farm_id_by_user_id(user_id: str) -> str | None:
    """사용자 ID로 농장 ID를 조회하는 함수"""
    db = get_firestore_client()
    users = db.collection('users').where('user_id', '==', user_id).get()
    if not users:
        return None
    return users[0].to_dict().get("farm_id")

def get_cow_by_ear_tag(farm_id: str, ear_tag_number: str) -> dict | None:
    """이표번호로 소 정보를 조회하는 함수"""
    db = get_firestore_client()
    cows = db.collection('cows')\
        .where('farm_id', '==', farm_id)\
        .where('ear_tag_number', '==', ear_tag_number)\
        .where('is_active', '==', True)\
        .get()
    if not cows:
        return None
    return cows[0].to_dict()

def generate_farmdata_response(state: DairyChatState) -> DairyChatState:
    """농장 데이터 기반 답변을 생성하는 노드"""
    question = state["current_question"]
    user_id = state["user_id"]

    ear_tag_number = extract_ear_tag_number(question)
    if not ear_tag_number:
        answer = "어떤 소에 대해 질문하시는지 12자리 이표번호(귀표번호)를 질문에 포함해 주세요."
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    farm_id = get_farm_id_by_user_id(user_id)
    if not farm_id:
        answer = "사용자 정보에서 농장 ID를 찾을 수 없습니다."
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    cow = get_cow_by_ear_tag(farm_id, ear_tag_number)
    if not cow:
        answer = f"이표번호 {ear_tag_number}번 소를 찾을 수 없습니다."
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    cow_id = cow["id"]
    record_type = extract_record_type(question)
    # record_type이 None이면 전체 기록 조회
    try:
        records = DetailedRecordService.get_detailed_records_by_cow(
            cow_id, farm_id, record_type if record_type else None
        )
    except Exception as e:
        answer = f"기록을 조회하는 중 오류가 발생했습니다: {e}"
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    if not records:
        answer = f"{cow['name']}({ear_tag_number}) 소의 해당 기록이 없습니다."
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    # 가장 최근 기록 1건만 사용
    record = records[0]
    # 기록 유형별 주요 정보만 자연스럽게 출력
    info = ", ".join([f"{k}: {v}" for k, v in record.key_values.items()]) if record.key_values else record.title
    answer = f"{cow['name']}({ear_tag_number}) 소의 최근 {record.record_type.value} 기록: {info} (날짜: {record.record_date})"
    append_chat_memory(user_id, state["chat_id"], question, answer)
    return {**state, "current_answer": answer} 