from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from .types import DairyChatState, get_chat_memory, append_chat_memory

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def generate_general_response(state: DairyChatState) -> DairyChatState:
    """일반적인 대화 답변을 생성하는 노드"""
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