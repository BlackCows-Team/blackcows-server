from typing import TypedDict, Literal, Dict, List, Tuple

# === 상태 정의 ===
class DairyChatState(TypedDict):
    user_id: str
    chat_id: str
    current_question: str
    current_answer: str
    answer_route: Literal["rag", "cow_info", "general", "irrelevant"]

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