from langgraph.graph import StateGraph, START, END
from .classifier import classify_question_route
from .general_response import generate_general_response
from .rag_response import generate_rag_response
from .cow_info_response import generate_farmdata_response
from .irrelevant_response import handle_irrelevant_question
from .router import route_by_answer_type
from .types import DairyChatState
from typing import TypedDict, Literal, Dict, List, Tuple
import os


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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

# === 라우팅 조건 함수
def route_by_answer_type(state: DairyChatState) -> str:
    return state["answer_route"]

# === LangGraph 정의 ===
def create_chatbot_graph():
    """챗봇 그래프를 생성하는 함수"""
    builder = StateGraph(DairyChatState)
    
    # 노드 추가
    builder.add_node("classify_question_route", classify_question_route)
    builder.add_node("generate_general_answer", generate_general_response)
    builder.add_node("generate_rag_answer", generate_rag_response)
    builder.add_node("generate_cow_info_answer", generate_farmdata_response)
    builder.add_node("handle_irrelevant_question", handle_irrelevant_question)

    # 엣지 추가
    builder.add_edge(START, "classify_question_route")
    builder.add_conditional_edges("classify_question_route", route_by_answer_type, {
        "general": "generate_general_answer",
        "rag": "generate_rag_answer",
        "cow_info": "generate_cow_info_answer",
        "irrelevant": "handle_irrelevant_question",
    })
    builder.add_edge("generate_general_answer", END)
    builder.add_edge("generate_rag_answer", END)
    builder.add_edge("generate_cow_info_answer", END)
    builder.add_edge("handle_irrelevant_question", END)

    return builder.compile()

# 그래프 인스턴스 생성
sodamsodam_graph = create_chatbot_graph()

# === 외부에서 호출되는 비동기 메인 함수 ===
async def run_chatbot_graph(user_id: str, chat_id: str, question: str) -> str:
    """챗봇 그래프를 실행하는 메인 함수"""
    state = DairyChatState(
        user_id=user_id,
        chat_id=chat_id,
        current_question=question,
        current_answer="",
        answer_route=""
    )
    result = await sodamsodam_graph.ainvoke(state)
    return result["current_answer"] 