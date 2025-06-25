# services/chatbot_service.py

from datetime import datetime, timedelta
from config.firebase_config import get_firestore_client
from firebase_admin import firestore
from langchain_core.runnables import RunnableConfig
from services.chatbot_runner import run_chatbot_graph
from schemas.chatbot_schema import AskRequest, ChatMessage, ChatRoom
import uuid


db = get_firestore_client()


# 1. LangGraph 실행 + 응답 저장
async def handle_user_question(data: AskRequest) -> str:
    answer = await run_chatbot_graph(
        user_id=data.user_id,
        chat_id=data.chat_id,
        question=data.question
    )

    chat_ref = db.collection("chat_rooms").document(data.chat_id)
    messages_ref = chat_ref.collection("messages")

    now = datetime.utcnow()
    messages_ref.add({
        "role": "user",
        "content": data.question,
        "timestamp": now
    })
    messages_ref.add({
        "role": "assistant",
        "content": answer,
        "timestamp": now
    })

    return answer


# 2. 채팅방 목록 조회
def get_user_chat_rooms(user_id: str) -> list[ChatRoom]:
    rooms = db.collection("chat_rooms") \
        .where("user_id", "==", user_id) \
        .order_by("created_at", direction=firestore.Query.DESCENDING) \
        .stream()

    return [
        ChatRoom(chat_id=room.id, created_at=room.to_dict()["created_at"])
        for room in rooms
    ]


# 3. 새 채팅방 생성
def create_chat_room(user_id: str) -> ChatRoom:
    chat_id = str(uuid.uuid4())
    created_at = datetime.utcnow()

    db.collection("chat_rooms").document(chat_id).set({
        "user_id": user_id,
        "created_at": created_at
    })

    return ChatRoom(chat_id=chat_id, created_at=created_at)


# 4. 특정 채팅방의 메시지 불러오기
def get_chat_history(chat_id: str) -> list[ChatMessage]:
    messages = db.collection("chat_rooms") \
        .document(chat_id) \
        .collection("messages") \
        .order_by("timestamp") \
        .stream()

    return [
        ChatMessage(
            role=msg.to_dict()["role"],
            content=msg.to_dict()["content"],
            timestamp=msg.to_dict()["timestamp"]
        )
        for msg in messages
    ]


# 5. 채팅방 및 메시지 삭제
def delete_chat_room(chat_id: str) -> bool:
    chat_ref = db.collection("chat_rooms").document(chat_id)

    # 메시지 삭제
    messages = chat_ref.collection("messages").stream()
    for msg in messages:
        msg.reference.delete()

    # 채팅방 문서 삭제
    chat_ref.delete()

    return True


# 6. 14일 지난 채팅방 자동 삭제
def delete_old_chat_rooms():
    limit_date = datetime.utcnow() - timedelta(days=14)
    old_chats = db.collection("chat_rooms") \
        .where("created_at", "<", limit_date) \
        .stream()

    for chat in old_chats:
        delete_chat_room(chat.id)