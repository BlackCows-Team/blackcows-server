from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from .types import DairyChatState, get_chat_memory, append_chat_memory
from config.firebase_config import get_firestore_client
from schemas.cow import HealthStatus, BreedingStatus, Temperament, MilkingBehavior
import re

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
db = get_firestore_client()


def get_cow_by_ear_tag_number(ear_tag_number: str):
    """특정 젖소 - 기본 정보 조회"""
    try:
        cow_doc = db.collection('cows').document(ear_tag_number).get()
        
        if not cow_doc.exists:
            return None
        
        cow_data = cow_doc.to_dict()
        
        # HealthStatus와 BreedingStatus 안전하게 변환
        health_status = None
        if cow_data.get("health_status"):
            try:
                health_status = HealthStatus(cow_data["health_status"])
            except ValueError:
                print(f"[WARNING] 잘못된 health_status 값: {cow_data['health_status']} (젖소 ID: {cow_data['id']})")
                health_status = HealthStatus.NORMAL
        
        breeding_status = None
        if cow_data.get("breeding_status"):
            try:
                breeding_status = BreedingStatus(cow_data["breeding_status"])
            except ValueError:
                print(f"[WARNING] 잘못된 breeding_status 값: {cow_data['breeding_status']} (젖소 ID: {cow_data['id']})")
                breeding_status = None
        
        return {
            # 기본 정보
            "id": cow_data["id"],
            "ear_tag_number": cow_data["ear_tag_number"],
            "name": cow_data["name"],
            "birthdate": cow_data.get("birthdate"),
            "sensor_number": cow_data.get("sensor_number"),
            "health_status": health_status,
            "breeding_status": breeding_status,
            "breed": cow_data.get("breed"),
            "notes": cow_data.get("notes"),
            "is_favorite": cow_data.get("is_favorite", False),
            "farm_id": cow_data["farm_id"],
            "owner_id": cow_data["owner_id"],
            "created_at": cow_data["created_at"],
            "updated_at": cow_data["updated_at"],
            "is_active": cow_data["is_active"]
        }
        
    except Exception as e:
        # 실패 시에도 500 오류 방지
        print(f"[ERROR] 특정 젖소 *기본 정보* 조회 전체 실패 (ear_tag_number: {ear_tag_number}): {str(e)}")
        return None

def get_cow_details_by_ear_tag_number(ear_tag_number: str):
    """특정 젖소 - 상세 정보 조회"""
    try:
        cow_doc = db.collection('cows').document(ear_tag_number).get()
        
        if not cow_doc.exists:
            return None
        
        cow_data = cow_doc.to_dict()
        
        # 상세 정보 추출
        detailed_info = cow_data.get("detailed_info", {})

        body_info = detailed_info.get("body_info", {})
        production_info = detailed_info.get("production_info", {})
        breeding_info = detailed_info.get("breeding_info", {})
        health_info = detailed_info.get("health_info", {})
        management_info = detailed_info.get("management_info", {})
        pedigree_info = detailed_info.get("pedigree_info", {})
        feed_info = detailed_info.get("feed_info", {})
        location_info = detailed_info.get("location_info", {})
        behavioral_info = detailed_info.get("behavioral_info", {})
        
                
        return {
            # 상세 정보 메타데이터
            "has_detailed_info": cow_data.get("has_detailed_info", False),
            "detail_updated_at": cow_data.get("detail_updated_at"),
            
            # 신체 정보
            "body_weight": body_info.get("weight"),
            "body_height": body_info.get("height"),
            "body_length": body_info.get("body_length"),
            "chest_girth": body_info.get("chest_girth"),
            "body_condition_score": body_info.get("body_condition_score"),
            
            # 생산 정보
            "lactation_number": production_info.get("lactation_number"),
            "milk_yield_record": production_info.get("milk_yield_record"),
            "lifetime_milk_yield": production_info.get("lifetime_milk_yield"),
            "average_daily_yield": production_info.get("average_daily_yield"),
            
            # 번식 정보
            "first_calving_date": breeding_info.get("first_calving_date"),
            "last_calving_date": breeding_info.get("last_calving_date"),
            "total_calves": breeding_info.get("total_calves"),
            "breeding_efficiency": breeding_info.get("breeding_efficiency"),
            
            # 건강 정보
            "vaccination_status": health_info.get("vaccination_status"),
            "last_health_check": health_info.get("last_health_check"),
            "chronic_conditions": health_info.get("chronic_conditions"),
            "allergy_info": health_info.get("allergy_info"),
            
            # 관리 정보
            "purchase_date": management_info.get("purchase_date"),
            "purchase_price": management_info.get("purchase_price"),
            "current_value": management_info.get("current_value"),
            "insurance_policy": management_info.get("insurance_policy"),
            "special_management": management_info.get("special_management"),
            
            # 혈통 정보
            "mother_id": pedigree_info.get("mother_id"),
            "father_info": pedigree_info.get("father_info"),
            "genetic_info": pedigree_info.get("genetic_info"),
            
            # 사료 정보
            "feed_type": feed_info.get("feed_type"),
            "daily_feed_amount": feed_info.get("daily_feed_amount"),
            "supplement_info": feed_info.get("supplement_info"),
            
            # 위치 정보
            "barn_section": location_info.get("barn_section"),
            "stall_number": location_info.get("stall_number"),
            
            # 행동 특성
            "temperament": Temperament(behavioral_info["temperament"]) if behavioral_info.get("temperament") else None,
            "milking_behavior": MilkingBehavior(behavioral_info["milking_behavior"]) if behavioral_info.get("milking_behavior") else None,
            "retirement_plan": behavioral_info.get("retirement_plan")
        }
        
    except Exception as e:
        # 실패 시에도 500 오류 방지
        print(f"[ERROR] 특정 젖소 *상세 정보* 조회 전체 실패 (ear_tag_number: {ear_tag_number}): {str(e)}")
        return None

def extract_ear_tag_number(text: str) -> str | None:
    """텍스트에서 12자리 이표번호 추출 (한글과 붙어 있어도 추출되게)"""
    match = re.search(r'(\\d{12})', text)
    return match.group(1) if match else None

### LLM 기반 질문 분류 ###
def classify_question_category(question: str) -> str:
    """질문을 9개 상세 정보 카테고리 중 하나로 분류 (LLM 활용)"""
    categories = [
        "body_info", "production_info", "breeding_info", "health_info",
        "management_info", "pedigree_info", "feed_info", "location_info", "behavioral_info"
    ]

    prompt = PromptTemplate(
        input_variables=["question"],
        template="""
당신은 젖소에 대한 질문을 분류하는 시스템입니다.

아래의 사용자 질문이 어떤 정보 분류에 해당하는지 판단하세요.
다음 분류 중 하나만 정확하게 골라주세요.

- body_info: 체중, 신장, 체형 등
- production_info: 우유 생산, 산유량 등
- breeding_info: 임신, 교배, 분만, 산차 등
- health_info: 건강검진, 질병, 백신 접종, 알레르기 등
- management_info: 구매 시기, 구매 가격, 보험, 평가 가치, 관리사항 등
- pedigree_info: 혈통, 유전 정보, 어미/아비 정보 등
- feed_info: 사료 종류, 사료 섭취량, 보충제 등
- location_info: 축사 구역, 칸 번호 등
- behavioral_info: 성격, 행동 습관, 착유시 행동, 퇴축 계획 등

[사용자 질문]
{question}

[분류 결과]
다음 중 하나만 출력하세요: body_info / production_info / breeding_info / health_info / management_info / pedigree_info / feed_info / location_info / behavioral_info
그 외 말은 절대 하지 마세요.
"""
    )
    chain = prompt | ChatOpenAI(temperature=0, model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY) | StrOutputParser()
    result = chain.invoke({"question": question}).strip()

    # 예외 처리
    if result not in categories:
        return "unknown"
    return result



### 관련 소 정보 추출 ###
def build_relevant_cow_info(question: str, basic: dict, detail: dict) -> dict:
    category = classify_question_category(question)
    if category == "unknown":
        return {"오류": "젖소의 어떤 정보를 원하시는지 정확히 파악하지 못했어요. 구체적으로 질문해 주시겠어요?"}

    info = {
        "이름": basic.get("name"),
        "이표번호": basic.get("ear_tag_number"),
        "생년월일": basic.get("birthdate"),
        "건강 상태": basic.get("health_status").name if basic.get("health_status") else None,
        "번식 상태": basic.get("breeding_status").name if basic.get("breeding_status") else None,
    }

    category_fields = {
        "body_info": ["weight", "height", "body_length", "chest_girth", "body_condition_score"],
        "production_info": ["lactation_number", "milk_yield_record", "lifetime_milk_yield", "average_daily_yield"],
        "breeding_info": ["first_calving_date", "last_calving_date", "total_calves", "breeding_efficiency"],
        "health_info": ["vaccination_status", "last_health_check", "chronic_conditions", "allergy_info"],
        "management_info": ["purchase_date", "purchase_price", "current_value", "insurance_policy", "special_management"],
        "pedigree_info": ["mother_id", "father_info", "genetic_info"],
        "feed_info": ["feed_type", "daily_feed_amount", "supplement_info"],
        "location_info": ["barn_section", "stall_number"],
        "behavioral_info": ["temperament", "milking_behavior", "retirement_plan"]
    }

    category_data = detail.get(category.replace("_info", "") + "_info", {})
    for field in category_fields[category]:
        value = category_data.get(field)
        if value:
            info[field] = str(value)

    return info


### 응답 생성 노드 ###
# 일반 함수로 정의
def generate_cow_info_response(state: DairyChatState) -> DairyChatState:
    memory_text = "\n".join(get_chat_memory(state["user_id"], state["chat_id"]))
    question = state["current_question"]
    ear_tag_number = extract_ear_tag_number(question)
    print(f"🏷️ 추출된 이표번호: {ear_tag_number}")

    # 이표번호가 포함되어 있지 않으면 안내
    if not ear_tag_number:
        msg = (
            "어떤 젖소에 대한 정보가 궁금하신가요?\n"
            "12자리 이표번호를 포함해서 질문해 주세요. 예: '123456789012 소의 건강 상태 알려줘.'"
        )
        append_chat_memory(state["user_id"], state["chat_id"], question, msg)
        return {**state, "current_answer": msg}

    # 소 정보 조회
    basic = get_cow_by_ear_tag_number(ear_tag_number)
    detail = get_cow_details_by_ear_tag_number(ear_tag_number)
    cow_info = build_relevant_cow_info(question, basic, detail)

    prompt = PromptTemplate(
        input_variables=["memory", "question", "cow_info"],
        template="""
당신은 낙농업 보조 챗봇 '소담이'입니다.

사용자의 질문에 대해 해당 소의 정보(`cow_info`)를 참고하여 친절하고 정확한 답변을 한 문단 이내로 생성하세요.

[대화 기록]
{memory}

[질문]
{question}

[소 정보]
{cow_info}

[답변 작성 지침]
- 반드시 소 정보를 참고해서만 답변하세요.
- 없는 정보는 "등록되지 않음" 또는 "확인되지 않음"으로 명확히 안내하세요.
- 어려운 용어나 전문 용어는 괄호로 쉽게 설명하세요.
"""
    )

    chain = prompt | ChatOpenAI(temperature=0.5, model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY) | StrOutputParser()
    result = chain.invoke({"memory": memory_text,
                           "question": question,
                           "cow_info": str(cow_info)})
    append_chat_memory(state["user_id"], state["chat_id"], question, result)


    return {**state, "current_answer": result}
