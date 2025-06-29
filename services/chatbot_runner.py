# services/chatbot_runner.py

from typing import TypedDict, Literal, Dict, List, Tuple
from langgraph.graph import StateGraph, START, END
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import os
from services.detailed_record_service import DetailedRecordService
from config.firebase_config import get_firestore_client
import re
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

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

# === 질문 분류 노드 ===
def classify_question_route(state: DairyChatState) -> DairyChatState:
    prompt = PromptTemplate(
        input_variables=["question"],
        template="""
            당신은 낙농업 분야에 특화된 AI 챗봇 '소담이'입니다.
            사용자의 질문을 다음 네 가지 유형 중 하나로 분류하세요:

            ---

            1. "rag"
            - 낙농업과 관련된 모든 정보 요청 (지식, 원리, 정책, 용어 등)
            - 예시: "젖소의 발정 주기는?", "착유기는 어떻게 작동하나요?", "낙농업 역사 알려줘"

            2. "cow_info"
            - 사용자의 농장에 등록된 소 정보나 상태, 기록 등
            - 예시: "103번 소 상태 알려줘", "어제 분만한 소들 누구야?"

            3. "general"
            - 챗봇 자체에 대한 질문, 인사, 감정 표현, 잡담 등 UX 흐름 질문
            - 예시: "안녕", "이전 질문 뭐였지?", "소담이 귀엽다", "고마워", "너 누구야?"

            4. "irrelevant"
            - 낙농업 또는 사용자의 목장과 완전히 무관한 질문
            - 예시: "로또 번호 알려줘", "요즘 주식 어때요?", "오늘 점심 뭐 먹지?"

            ---

            [사용자 질문]
            {question}

            [분류 결과]
            아래 중 하나만 출력하세요: rag / cow_info / general / irrelevant
            그 외 말은 절대 하지 마세요.
            """
    )

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": state["current_question"]})
    result = result.replace('"', '').replace("'", '').strip().lower()

    if result not in {"rag", "cow_info", "general", "irrelevant"}:
        result = "irrelevant"

    return {
        **state,
        "answer_route": result,
    }

# === 일반 답변 노드 ===
def generate_general_response(state: DairyChatState) -> DairyChatState:
    memory_text = "\n".join(get_chat_memory(state["user_id"], state["chat_id"]))
    prompt = PromptTemplate(
        input_variables=["memory", "question"],
        template="""
            당신은 낙농업 도우미 챗봇 '소담이'입니다.
            사용자와 자연스럽게 대화를 이어가며 친근하고 따뜻하게 답변해주세요.

            [사용자와의 이전 대화 기록]
            {memory}

            [사용자 질문]
            {question}

            [소담이의 답변]
            - 너무 길지 않게 한 문단 이내로 대답
            - 40~70대 사용자도 이해할 수 있도록 어려운 단어나 전문용어 피하기
            - 줄바꿈(\\n), 따옴표, 특수기호 없이 자연스럽게 문장 구성
            """
    )
    llm = ChatOpenAI(temperature=0.5, model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({
        "memory": memory_text,
        "question": state["current_question"]
    })

    append_chat_memory(state["user_id"], state["chat_id"], state["current_question"], result)

    return {
        **state,
        "current_answer": result
    }

# === RAG 기반 답변 노드 ===
_vectordb = None
def build_or_load_vectordb():
    global _vectordb
    if _vectordb:
        return _vectordb

    persist_dir = "./chroma_dairy_knowledge"
    embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    if not os.path.exists(os.path.join(persist_dir, "chroma-collections.parquet")):
        loader = TextLoader("dairy_farming_wiki.txt", encoding="utf-8")
        raw_documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(raw_documents)
        vectordb = Chroma.from_documents(chunks, embedding, persist_directory=persist_dir)
    else:
        vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding)

    _vectordb = vectordb
    return vectordb

def generate_rag_response(state: DairyChatState) -> DairyChatState:
    vectordb = build_or_load_vectordb()
    memory_text = "\n".join(get_chat_memory(state["user_id"], state["chat_id"]))
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(state["current_question"])
    context = "\n".join([doc.page_content for doc in docs]) or "※ 참고 문서 없음"

    prompt = PromptTemplate(
        input_variables=["context", "memory", "question"],
        template="""
            당신은 낙농업에 특화된 챗봇 '소담이'입니다.
            아래 참고 자료를 먼저 사용해서 답변하세요.

            만약 참고 자료에서 답을 찾을 수 없다면,
            당신이 알고 있는 지식이나 상식, 경험을 바탕으로 대신 답해도 괜찮습니다.
            단, 틀리면 안 되고 너무 길게 설명하지 마세요.

            - 특수기호 없이 일반 문장만 사용
            - 짧고 쉬운 단어, 한 문단 이내

            [사용자와의 대화 기록]
            {memory}

            [참고 자료]
            {context}

            [질문]
            {question}

            [답변]
            """
    )

    llm = ChatOpenAI(temperature=0.3, model="gpt-4o-mini", streaming=True, openai_api_key=OPENAI_API_KEY)
    memory_text = "\n".join(get_chat_memory(state["user_id"], state["chat_id"]))

    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(state["current_question"])
    context = "\n\n".join([doc.page_content for doc in docs]) or "※ 참고할 문서가 없습니다."

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "context": context,
        "memory": memory_text,
        "question": state["current_question"]
    })

    append_chat_memory(state["user_id"], state["chat_id"], state["current_question"], answer)

    return {
        **state,
        "current_answer": answer
    }

# === 농장 데이터 노드 (예시)
def extract_ear_tag_number(question: str) -> str | None:
    # 12자리 이표번호 추출
    match = re.search(r'\b\d{12}\b', question)
    return match.group(0) if match else None

def extract_record_type(question: str) -> str | None:
    # 질문에서 기록 유형 추출 (간단 키워드 매칭)
    if "착유" in question or "우유" in question:
        return "milking"
    if "발정" in question:
        return "estrus"
    if "건강" in question or "질병" in question:
        return "health_check"
    if "백신" in question:
        return "vaccination"
    if "체중" in question or "무게" in question:
        return "weight"
    if "사료" in question:
        return "feed"
    if "임신" in question:
        return "pregnancy_check"
    if "분만" in question:
        return "calving"
    if "치료" in question:
        return "treatment"
    # 필요시 추가
    return None

def get_farm_id_by_user_id(user_id: str) -> str | None:
    db = get_firestore_client()
    users = db.collection('users').where('user_id', '==', user_id).get()
    if not users:
        return None
    return users[0].to_dict().get("farm_id")

def get_cow_by_ear_tag(farm_id: str, ear_tag_number: str) -> dict | None:
    db = get_firestore_client()
    cows = db.collection('cows')\
        .where('farm_id', '==', farm_id)\
        .where('ear_tag_number', '==', ear_tag_number)\
        .where('is_active', '==', True)\
        .get()
    if not cows:
        return None
    return cows[0].to_dict()

def generate_farmdata_response(state: DairyChatState) -> DairyChatState:
    question = state["current_question"]
    user_id = state["user_id"]

    ear_tag_number = extract_ear_tag_number(question)
    if not ear_tag_number:
        answer = "어떤 소에 대해 질문하시는지 12자리 이표번호(귀표번호)를 질문에 포함해 주세요."
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    farm_id = get_farm_id_by_user_id(user_id)
    if not farm_id:
        answer = "사용자 정보에서 농장 ID를 찾을 수 없습니다."
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    cow = get_cow_by_ear_tag(farm_id, ear_tag_number)
    if not cow:
        answer = f"이표번호 {ear_tag_number}번 소를 찾을 수 없습니다."
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    cow_id = cow["id"]
    record_type = extract_record_type(question)
    # record_type이 None이면 전체 기록 조회
    try:
        records = DetailedRecordService.get_detailed_records_by_cow(
            cow_id, farm_id, record_type if record_type else None
        )
    except Exception as e:
        answer = f"기록을 조회하는 중 오류가 발생했습니다: {e}"
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    if not records:
        answer = f"{cow['name']}({ear_tag_number}) 소의 해당 기록이 없습니다."
        append_chat_memory(user_id, state["chat_id"], question, answer)
        return {**state, "current_answer": answer}

    # 가장 최근 기록 1건만 사용
    record = records[0]
    # 기록 유형별 주요 정보만 자연스럽게 출력
    info = ", ".join([f"{k}: {v}" for k, v in record.key_values.items()]) if record.key_values else record.title
    answer = f"{cow['name']}({ear_tag_number}) 소의 최근 {record.record_type.value} 기록: {info} (날짜: {record.record_date})"
    append_chat_memory(user_id, state["chat_id"], question, answer)
    return {**state, "current_answer": answer}

# === 무관한 질문 처리 노드
def handle_irrelevant_question(state: DairyChatState) -> DairyChatState:
    answer = "죄송합니다. 이 챗봇은 낙농업 관련 질문에만 답변할 수 있습니다."
    append_chat_memory(state["user_id"], state["chat_id"], state["current_question"], answer)
    return {
        **state,
        "current_answer": answer
    }

# === 라우팅 조건 함수
def route_by_answer_type(state: DairyChatState) -> str:
    return state["answer_route"]

# === LangGraph 정의
builder = StateGraph(DairyChatState)
builder.add_node("classify_question_route", classify_question_route)
builder.add_node("generate_general_answer", generate_general_response)
builder.add_node("generate_rag_answer", generate_rag_response)
builder.add_node("generate_cow_info_answer", generate_farmdata_response)
builder.add_node("handle_irrelevant_question", handle_irrelevant_question)

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

sodamsodam_graph = builder.compile()

# === 외부에서 호출되는 비동기 메인 함수 ===
async def run_chatbot_graph(user_id: str, chat_id: str, question: str) -> str:
    state = DairyChatState(
        user_id=user_id,
        chat_id=chat_id,
        current_question=question,
        current_answer="",
        answer_route=""
    )
    result = await sodamsodam_graph.ainvoke(state)
    return result["current_answer"]