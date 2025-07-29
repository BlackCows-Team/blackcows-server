# cow_info_graph.py

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from .cow_info_nodes import (
    classify_question_node,
    check_ear_tag_node,
    show_cow_list_node,
    select_cow_node,
    ask_info_detail_node,
    ask_info_detail_response_node,
)
from .types import CowInfoState

def create_cow_info_graph():
    graph = StateGraph(CowInfoState)

    # 노드 등록
    graph.add_node("check_ear_tag_node", RunnableLambda(check_ear_tag_node))
    graph.add_node("show_cow_list_node", RunnableLambda(show_cow_list_node))
    graph.add_node("select_cow_node", RunnableLambda(select_cow_node))
    graph.add_node("ask_info_detail_node", RunnableLambda(ask_info_detail_node))
    graph.add_node("ask_info_detail_response_node", RunnableLambda(ask_info_detail_response_node))

    # 흐름 정의
    graph.set_entry_point("classify_question_node")
    graph.add_edge("classify_question_node", "check_ear_tag_node")

    graph.add_conditional_edges(
        "check_ear_tag_node",
        lambda s: "selected_cow_info" in s and s["selected_cow_info"] is not None,
        {
            True: "ask_info_detail_node",
            False: "show_cow_list_node"
        }
    )
    graph.add_edge("show_cow_list_node", "select_cow_node")
    graph.add_edge("select_cow_node", "ask_info_detail_node")
    graph.add_edge("ask_info_detail_node", "ask_info_detail_response_node")
    graph.add_edge("ask_info_detail_response_node", END)

    return graph.compile()