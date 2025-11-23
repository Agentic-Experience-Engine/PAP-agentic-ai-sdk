# agentic_ai_sdk/agents.py
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool

from .tools import (
    get_user_previous_product_views,
    get_user_orders,
    search_products_by_filters,
    product_rag_search,
)


def build_llm() -> ChatOpenAI:
    import os
    return ChatOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4.1-mini",
        temperature=0.2,
        base_url=os.getenv("OPENAI_BASE_URL"),
    )


# ---------- UserAgent ----------

def build_user_agent() -> Any:
    llm = build_llm()
    tools = [get_user_previous_product_views]

    # UserAgent knows how to talk about user history and preferences.
    user_agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
    )
    return user_agent


# ---------- OrdersAgent ----------

def build_orders_agent() -> Any:
    llm = build_llm()
    tools = [get_user_orders]

    orders_agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
    )
    return orders_agent


# ---------- SearchAgent (top-level orchestrator) ----------

def build_search_agent() -> Any:
    llm = build_llm()

    user_agent = build_user_agent()
    orders_agent = build_orders_agent()

    # Wrap sub-agents as tools so SearchAgent can call them.
    user_agent_tool = Tool.from_function(
        name="user_agent_delegate",
        func=lambda query: user_agent.run(query),
        description=(
            "Delegate queries about user's past activity, previously viewed products, "
            "search history, and preferences to the UserAgent."
        ),
    )

    orders_agent_tool = Tool.from_function(
        name="orders_agent_delegate",
        func=lambda query: orders_agent.run(query),
        description=(
            "Delegate queries about user's orders, returns, refunds, and order history "
            "to the OrdersAgent."
        ),
    )

    # SearchAgent's own tools:
    tools = [
        product_rag_search,
        search_products_by_filters,
        user_agent_tool,
        orders_agent_tool,
    ]

    search_agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
    )
    return search_agent
