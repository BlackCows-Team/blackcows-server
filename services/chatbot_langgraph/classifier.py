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
사용자의 질문을 다음 네 가지 유형 중 하나로 정확히 분류하세요:

---

1. "rag"  
- 낙농업 및 젖소와 관련된 일반 지식, 현상, 원인, 질병, 관리법 등  
- 특정 소를 직접 지칭하지 않고, 소의 상태나 행동에 대한 설명이거나 일반적인 궁금증일 때 포함  
- 예: "소가 침을 흘려요", "젖소가 잘 안 먹어요", "발정 시기 언제야?"

2. "cow_info"  
- 사용자의 농장에 등록된 **특정 젖소**의 정보를 묻는 질문  
- **12자리 이표번호가 포함된 경우**, 또는 **"123번 소", "그 소", "그 아이"**처럼 특정 개체를 직접 가리킬 때만 해당  
- 예: "103번 소 상태 알려줘", "123456789012 소의 건강 알려줘", "어제 분만한 소들 누구야?", "123456789012"

3. "general"  
- 챗봇 자체에 대한 질문, 인사, UX 흐름, 잡담, 감정 표현 등  
- 예: "안녕", "소담이 귀엽다", "이전 질문 뭐였지?", "고마워", "너 누구야?"

4. "irrelevant"  
- 낙농업 및 젖소와 무관한 질문  
- 예: "로또 번호 알려줘", "오늘 날씨 어때?", "주식 뭐 살까?", "점심 뭐 먹지?"

---

[사용자 질문]
{question}

[분류 결과]
다음 중 하나만 출력하세요: rag / cow_info / general / irrelevant
그 외 말은 절대 하지 마세요.
"""
    )

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": state["current_question"]})
    result = result.replace('"', '').replace("'", '').strip().lower()
    print('🤖 답변 분류 결과:', result)

    if result not in {"rag", "cow_info", "general", "irrelevant"}:
        result = "irrelevant"

    return {
        **state,
        "answer_route": result,
    }