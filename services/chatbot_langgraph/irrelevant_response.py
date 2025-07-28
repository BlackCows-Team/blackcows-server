from .types import DairyChatState, append_chat_memory

def handle_irrelevant_question(state: DairyChatState) -> DairyChatState:
    """무관한 질문을 처리하는 노드"""
    answer = "죄송합니다. 저는 낙농업 관련 질문에만 답변할 수 있어요."
    append_chat_memory(state["user_id"], state["chat_id"], state["current_question"], answer)
    return {
        **state,
        "current_answer": answer
    } 