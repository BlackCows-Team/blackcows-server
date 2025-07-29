from langgraph.graph import StateGraph, START, END
from .classifier import classify_question_route
from .general_response import generate_general_response
from .rag_response import generate_rag_response
from .irrelevant_response import handle_irrelevant_question
from .types import DairyChatState
from .cow_info_graph import create_cow_info_graph

# === 라우팅 조건 함수
def route_by_answer_type(state: DairyChatState) -> str:
    return state["answer_route"]

# === LangGraph 정의 ===
def create_chatbot_graph():
    """챗봇 그래프를 생성하는 함수"""
    builder = StateGraph(DairyChatState)
    
    cow_info_subgraph = create_cow_info_graph().as_runnable()

    # 노드 추가
    builder.add_node("classifier", classify_question_route)
    builder.add_node("general_response", generate_general_response)
    builder.add_node("rag_response", generate_rag_response)
    builder.add_node("cow_info_graph", cow_info_subgraph)
    builder.add_node("irrelevant_response", handle_irrelevant_question)

    # 엣지 추가
    builder.add_edge(START, "classifier")
    builder.add_conditional_edges("classifier", route_by_answer_type, {
        "general": "general_response",
        "rag": "rag_response",
        "cow_info": "cow_info_graph",
        "irrelevant": "irrelevant_response",
    })
    builder.add_edge("general_response", END)
    builder.add_edge("rag_response", END)
    builder.add_edge("cow_info_graph", END)
    builder.add_edge("irrelevant_response", END)

    return builder.compile()

# 그래프 인스턴스 생성
sodamsodam_graph = create_chatbot_graph()

# === 외부에서 호출되는 비동기 메인 함수 ===
async def run_chatbot_graph(user_id: str, chat_id: str, farm_id: str, question: str) -> str:
    """챗봇 그래프를 실행하는 메인 함수"""
    state = DairyChatState(
        user_id=user_id,
        chat_id=chat_id,
        farm_id=farm_id,
        current_question=question,
        current_answer="",
        answer_route=""
    )
    result = await sodamsodam_graph.ainvoke(state)
    return result["current_answer"] 