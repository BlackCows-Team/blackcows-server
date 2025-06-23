from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END, START
from langchain_core.runnables import RunnableConfig
from typing import TypedDict
import os

# 환경 변수에서 OpenAI 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === 챗봇 상태 정의 ===
class DairyChatState(TypedDict):
    user_id: str
    chat_id: str
    current_question: str
    current_answer: str
    answer_route: str

# === 질문 분류 노드 ===
def classify_question_route(state: DairyChatState) -> DairyChatState:
    prompt = PromptTemplate(
        input_variables=["question"],
        template="""
당신은 낙농업 분야에 특화된 AI 챗봇 '소담이'입니다. 사용자 질문을 다음 네 가지로 분류하세요:

1. rag - 낙농 지식
2. cow_info - 사용자 목장 데이터
3. general - 인사/잡담
4. irrelevant - 무관한 질문

[질문]
{question}

[응답] (rag / cow_info / general / irrelevant 중 하나만)
"""
    )
    chain = ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY
    ) | prompt

    classification = chain.invoke({"question": state["current_question"]})
    classification = classification.strip().lower()
    if classification not in {"rag", "cow_info", "general", "irrelevant"}:
        classification = "irrelevant"
    return {
        **state,
        "answer_route": classification,
    }

# === 각 응답 노드 ===
def generate_general_response(state: DairyChatState) -> DairyChatState:
    return {
        **state,
        "current_answer": "소담이에게 인사해 주셔서 고마워요! 낙농에 대해 궁금한 걸 물어보세요!"
    }

def generate_rag_response(state: DairyChatState) -> DairyChatState:
    return {
        **state,
        "current_answer": f"'{state['current_question']}' 에 대한 낙농 정보를 준비 중이에요! (예시 응답)"
    }

def generate_farmdata_response(state: DairyChatState) -> DairyChatState:
    return {
        **state,
        "current_answer": f"'{state['current_question']}' 는 농장 DB와 연결해서 처리할 예정입니다. (예시 응답)"
    }

def handle_irrelevant_question(state: DairyChatState) -> DairyChatState:
    return {
        **state,
        "current_answer": "죄송해요, 낙농과 관련된 질문을 해주세요!"
    }

# === 조건 분기 함수 ===
def route_by_answer_type(state: DairyChatState) -> str:
    return state["answer_route"]

# === LangGraph 정의 ===
builder = StateGraph(DairyChatState)
builder.add_node("classify_question_route", classify_question_route)
builder.add_node("generate_general_answer", generate_general_response)
builder.add_node("generate_rag_answer", generate_rag_response)
builder.add_node("generate_cow_info_answer", generate_farmdata_response)
builder.add_node("handle_irrelevant_question", handle_irrelevant_question)

builder.add_edge(START, "classify_question_route")
builder.add_conditional_edges(
    "classify_question_route",
    route_by_answer_type,
    {
        "general": "generate_general_answer",
        "rag": "generate_rag_answer",
        "cow_info": "generate_cow_info_answer",
        "irrelevant": "handle_irrelevant_question",
    }
)
builder.add_edge("generate_general_answer", END)
builder.add_edge("generate_rag_answer", END)
builder.add_edge("generate_cow_info_answer", END)
builder.add_edge("handle_irrelevant_question", END)

sodamsodam_graph = builder.compile()

# === 외부에서 호출할 메인 함수 ===
async def run_chatbot_graph(user_id: str, chat_id: str, question: str) -> str:
    state = DairyChatState(
        user_id=user_id,
        chat_id=chat_id,
        current_question=question,
        current_answer="",
        answer_route=""
    )
    result = await sodamsodam_graph.ainvoke(state, config=RunnableConfig())
    return result["current_answer"]
