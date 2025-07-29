from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, Optional, Dict, Any, List
from .cow_info_service import extract_ear_tag_number, get_basic_info_by_ear_tag_number, get_cow_details_by_ear_tag_number, build_relevant_cow_info_by_category
from .types import DairyChatState, get_chat_memory, append_chat_memory
from services.cow_firebase_service import CowFirebaseService
from .types import CowInfoState

# 노드 1: check_ear_tag_node

def check_ear_tag_node(state: CowInfoState) -> CowInfoState:
    question = state["current_question"]
    ear_tag_number = extract_ear_tag_number(question)

    if ear_tag_number:
        basic_info = get_basic_info_by_ear_tag_number(ear_tag_number)
        if basic_info:
            msg = (
                f"{basic_info['name']} (이표번호: {ear_tag_number}, 출생일: {basic_info.get('birthdate', '미등록')})\n"
                f"이 소가 맞나요? 이름이나 정보를 말씀해 주세요."
            )
            append_chat_memory(state["user_id"], state["chat_id"], question, msg)
            return {
                **state,
                "selected_cow_info": basic_info,
                "awaiting_confirmation": True,
                "current_answer": msg
            }

    return show_cow_list_node(state)


# 노드 2: show_cow_list_node

def show_cow_list_node(state: CowInfoState) -> CowInfoState:
    question = state["current_question"]
    farm_id = state["farm_id"]

    cows = CowFirebaseService.get_cows_by_farm(farm_id)
    cow_dict_list = [cow.model_dump() for cow in cows]

    if not cow_dict_list:
        msg = "등록된 소가 없어요. 먼저 소를 등록해주세요!"
    else:
        summary = [
            f"- {cow['name']} (이표번호: {cow['ear_tag_number']}, 출생일: {cow.get('birthdate', '미등록')})"
            for cow in cow_dict_list[:10]
        ]
        msg = (
            "요청하신 소를 찾지 못했어요.\n"
            "대신 아래 목록에서 궁금한 소의 이름이나 이표번호를 말씀해 주세요:\n"
            + "\n".join(summary)
        )

    append_chat_memory(state["user_id"], state["chat_id"], question, msg)

    return {
        **state,
        "selected_cow_info": None,
        "cow_list": cow_dict_list,
        "awaiting_confirmation": False,
        "current_answer": msg
    }


# 노드 3: select_cow_node

def select_cow_node(state: CowInfoState) -> CowInfoState:
    question = state["current_question"]
    cow_list = state.get("cow_list", [])

    ear_tag_number = extract_ear_tag_number(question)
    selected_cow = None

    if ear_tag_number:
        selected_cow = next((cow for cow in cow_list if cow["ear_tag_number"] == ear_tag_number), None)
    else:
        selected_cow = next((cow for cow in cow_list if cow["name"] in question), None)

    if selected_cow:
        msg = f"'{selected_cow['name']}' (이표번호: {selected_cow['ear_tag_number']}, 출생일: {selected_cow.get('birthdate', '미등록')})\n이 소가 맞나요?"
        append_chat_memory(state["user_id"], state["chat_id"], question, msg)
        return {
            **state,
            "selected_cow_info": selected_cow,
            "awaiting_confirmation": True,
            "current_answer": msg
        }

    return show_cow_list_node(state)


# 노드 4: ask_info_detail_node

def ask_info_detail_node(state: CowInfoState) -> CowInfoState:
    question = state["current_question"]
    cow = state.get("selected_cow_info")

    msg = (
        f"'{cow['name']}'에 대해 어떤 정보가 궁금하신가요?\n"
        "아래 분류 중 하나를 입력해 주세요:\n\n"
        "- 체형 정보 (body_info)\n"
        "- 산유 정보 (production_info)\n"
        "- 번식 정보 (breeding_info)\n"
        "- 건강 정보 (health_info)\n"
        "- 관리 정보 (management_info)\n"
        "- 혈통 정보 (pedigree_info)\n"
        "- 사료 정보 (feed_info)\n"
        "- 위치 정보 (location_info)\n"
        "- 행동 특성 (behavioral_info)"
    )

    append_chat_memory(state["user_id"], state["chat_id"], question, msg)
    return {
        **state,
        "current_answer": msg
    }


# 노드 5: ask_info_detail_response_node

def ask_info_detail_response_node(state: CowInfoState) -> CowInfoState:
    question = state["current_question"]
    category = question.strip()

    valid_categories = [
        "body_info", "production_info", "breeding_info", "health_info",
        "management_info", "pedigree_info", "feed_info", "location_info", "behavioral_info"
    ]

    if category not in valid_categories:
        msg = "입력하신 분류를 이해하지 못했어요. 위에 제시된 9개 중 하나를 다시 입력해 주세요."
        append_chat_memory(state["user_id"], state["chat_id"], question, msg)
        return {
            **state,
            "current_answer": msg
        }

    cow = state.get("selected_cow_info")
    cow_detail = get_cow_details_by_ear_tag_number(cow["ear_tag_number"])

    info = build_relevant_cow_info_by_category(category, cow, cow_detail)

    if "오류" in info:
        msg = info["오류"]
    else:
        msg_lines = [f"{k}: {v}" for k, v in info.items() if v]
        msg = f"[{cow['name']} - {category} 정보 요약]\n" + "\n".join(msg_lines)

    append_chat_memory(state["user_id"], state["chat_id"], question, msg)
    return {
        **state,
        "current_answer": msg
    }
