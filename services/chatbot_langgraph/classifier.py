from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from .types import DairyChatState

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def classify_question_route(state: DairyChatState) -> DairyChatState:
    """질문을 분류하여 적절한 답변 경로를 결정하는 노드"""
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