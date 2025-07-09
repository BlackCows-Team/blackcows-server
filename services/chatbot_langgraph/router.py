from .types import DairyChatState

def route_by_answer_type(state: DairyChatState) -> str:
    """답변 유형에 따라 다음 노드를 결정하는 라우팅 함수"""
    return state["answer_route"] 