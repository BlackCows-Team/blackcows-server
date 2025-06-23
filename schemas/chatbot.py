from pydantic import BaseModel

class ChatbotRequest(BaseModel):
    user_id: str
    chatroom_id: str
    question: str

class ChatbotResponse(BaseModel):
    answer: str