from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agent.services.multi_agents import (
    map_agent,
    reduce_agent,
    rank_agent,
    marketing_content_agent,
    distributor_agent,
)
from agent.services.schemas import DistributorInput
from agent.services.tools import google_search
from agent.services.rag import build_retriever_chroma

    
class State(TypedDict, total=False):
    company: str
    year: str
    period: str
    retriever: Any
    map_result: Any
    reduce_result: Any
    ranked_insights: Dict[str, Any]
    rank_obj: Any
    marketing_content: Dict[str, Any]
    fb_post: Dict[str, Any]
    page_id: str
    fb_access_token: str
    steps: List[str]


def research_node(state: State):
    search_query = "automotive industry 2025 full year report site:mckinsey.com OR site:deloitte.com OR site:gartner.com"
    raw_docs = google_search(search_query)
    sim_query = f"Please retrieve comprehensive professional industry reports for the {state['period']} {state['year']} based on the specified company {state['company']} set."
    retriever = build_retriever_chroma(raw_docs, sim_query)

    return {
        "retriever": retriever,
        "steps": state.get("steps", []) + ["cache", "rag"],
    }



def map_node(state: State):
    retriever = state["retriever"]
    raw = map_agent(retriever, state["company"])

    return {
        "map_result": raw,
        "steps": state.get("steps", []) + ["map"],
    }

def reduce_node(state: State):
    strategic = reduce_agent(state["map_result"])

    return {
        "reduce_result": strategic,
        "steps": state.get("steps", []) + ["reduce"],
    }

def rank_node(state: State):
    ranked = rank_agent(state["reduce_result"])

    return {
        "ranked_insights": ranked.model_dump(),
        "rank_obj": ranked,
        "steps": state.get("steps", []) + ["rank"],
    }

def marketing_node(state: State):
    marketing = marketing_content_agent(state["rank_obj"])

    return {
        "marketing_content": marketing.model_dump(),
        "steps": state.get("steps", []) + ["generate"],
    }


def distributor_node(state: State):
    page_id = state.get("page_id")
    access_token = state.get("fb_access_token")

    result = distributor_agent(
        DistributorInput(
            marketing_content=state["marketing_content"],
            page_id=page_id,
            access_token=access_token
        )
    )
    return {
        "fb_post": result.model_dump(),
        "steps": state.get("steps", []) + ["distribute"],
    }


def build_graph():
    checkpointer = MemorySaver()
    graph = StateGraph(State)

    graph.add_node("research", research_node)
    graph.add_node("map", map_node)
    graph.add_node("reduce", reduce_node)
    graph.add_node("rank", rank_node)
    graph.add_node("content_generator", marketing_node)
    graph.add_node("distributor", distributor_node)

    graph.set_entry_point("research")

    graph.add_edge("research", "map")
    graph.add_edge("map", "reduce")
    graph.add_edge("reduce", "rank")
    graph.add_edge("rank", "content_generator")
    graph.add_edge("content_generator", "distributor")
    graph.add_edge("distributor", END)

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["distributor"],
    )


graph = build_graph()


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "123"}}

    initial_state = {
        "company": "OpenAI",
        "year": "2025",
        "period": "full year",
        "steps": [],
    }

    for chunk in graph.stream(initial_state, config):
        print(chunk)
        print(">>>" * 10)

    current_state = graph.get_state(config)
    print(
        f">>> pls check the contents before automated distribution: {current_state.values['marketing_content']}"
    )

    user_input = input("Are you sure to post the content in public (yes/no/update): ")

    if user_input.lower() == "yes":
        print("\n>>> Start publishing: ...")
        for event in graph.stream(None, config):
            print(event)
    elif user_input.lower() == "update":
        new_analysis = "(revised) new content"
        graph.update_state(config, {"analysis": new_analysis})
        print("\n>>> State has been updated, start publishing the revised content...")
        for event in graph.stream(None, config):
            print(event)
    else:
        print(">>> Publishing has been cancelled by user.")
