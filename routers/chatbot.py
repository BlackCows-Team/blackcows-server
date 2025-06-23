from fastapi import APIRouter, HTTPException
from services.chatbot_service import run_chatbot_graph
from schemas.chatbot import ChatbotRequest, ChatbotResponse

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@router.post("/ask", response_model=ChatbotResponse)
async def ask_chatbot(request: ChatbotRequest):
    """
    챗봇 응답을 생성합니다.
    """
    try:
        response = await run_chatbot_graph(
            user_id=request.user_id,
            chatroom_id=request.chatroom_id,
            question=request.question
        )
        return ChatbotResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))