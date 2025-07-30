from typing import TypedDict, Literal, Dict, List, Tuple, Optional, Any

# === 챗봇 상태 정의 ===
class DairyChatState(TypedDict):
    user_id: str
    chat_id: str
    farm_id: str 
    current_question: str
    current_answer: str
    answer_route: Literal["rag", "cow_info", "general", "irrelevant"]

# === 소 정보 상태 정의 ===
class CowInfoState(TypedDict):
    user_id: str
    chat_id: str
    farm_id: str
    current_question: str
    current_answer: str
    selected_cow_info: Optional[Dict[str, Any]]
    awaiting_confirmation: bool  # Optional 제거하고 기본값 False로 설정
    cow_list: Optional[List[Dict[str, Any]]]


# === 메모리 저장소 ===
chat_memory_store: Dict[Tuple[str, str], List[str]] = {}

def get_chat_memory(user_id: str, chat_id: str) -> List[str]:
    return chat_memory_store.get((user_id, chat_id), [])

def append_chat_memory(user_id: str, chat_id: str, question: str, answer: str):
    key = (user_id, chat_id)
    memory = chat_memory_store.get(key, [])
    memory.append(f"사용자: {question}")
    memory.append(f"소담이: {answer}")
    chat_memory_store[key] = memory
