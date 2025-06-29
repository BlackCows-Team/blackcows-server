# schemas/chatbot.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 질문 요청
class AskRequest(BaseModel):
    user_id: str
    chat_id: str
    question: str

# 질문 응답
class AskResponse(BaseModel):
    answer: str

# 채팅방 생성 요청
class CreateChatRoomRequest(BaseModel):
    user_id: str
    name: Optional[str] = None  # 채팅방 이름 (선택사항)

# 채팅방 이름 변경 요청
class UpdateChatRoomNameRequest(BaseModel):
    name: str

# 채팅방 정보
class ChatRoom(BaseModel):
    chat_id: str
    name: Optional[str] = None  # 채팅방 이름
    created_at: datetime

# 채팅방 목록 응답
class ChatRoomList(BaseModel):
    chats: List[ChatRoom]

# 채팅 메시지
class ChatMessage(BaseModel):
    role: str  # "user" 또는 "assistant"
    content: str
    timestamp: datetime

# 특정 채팅방의 대화 이력
class ChatHistoryResponse(BaseModel):
    chat_id: str
    messages: List[ChatMessage]
