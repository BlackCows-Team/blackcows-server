from fastapi import APIRouter, HTTPException
from schemas.chatbot_schema import (
    AskRequest, AskResponse,
    CreateChatRoomRequest, ChatRoomList,
    ChatHistoryResponse
)
from services import chatbot_service

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


# 1. 질문 → LangGraph 실행 & 저장
@router.post("/ask", response_model=AskResponse)
async def ask_question(data: AskRequest):
    try:
        answer = await chatbot_service.handle_user_question(data)
        return AskResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2. 사용자 채팅방 목록 조회
@router.get("/rooms/{user_id}", response_model=ChatRoomList)
def get_chat_rooms(user_id: str):
    try:
        chats = chatbot_service.get_user_chat_rooms(user_id)
        return ChatRoomList(chats=chats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. 새 채팅방 생성
@router.post("/rooms", response_model=ChatRoomList)
def create_chat_room(data: CreateChatRoomRequest):
    try:
        room = chatbot_service.create_chat_room(data.user_id)
        return ChatRoomList(chats=[room])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4. 채팅방 내 대화 이력 조회
@router.get("/history/{chat_id}", response_model=ChatHistoryResponse)
def get_chat_history(chat_id: str):
    try:
        messages = chatbot_service.get_chat_history(chat_id)
        return ChatHistoryResponse(chat_id=chat_id, messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 5. 채팅방 삭제
@router.delete("/rooms/{chat_id}")
def delete_chat_room(chat_id: str):
    try:
        chatbot_service.delete_chat_room(chat_id)
        return {"detail": "채팅방이 성공적으로 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 6. 14일 이상 지난 채팅방 일괄 삭제
@router.delete("/rooms/expired/auto")
def delete_expired_chat_rooms():
    try:
        chatbot_service.delete_old_chat_rooms()
        return {"detail": "14일 이상된 채팅방이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
