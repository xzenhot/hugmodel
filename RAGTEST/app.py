import os
from re import search
from typing import Annotated, TypedDict
from typing import TypedDict
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma

import secret

import tools.fetch as fetch
import tools.llm   as llm
import tools.search as search
import tools.db as db
import tools.flight as flight
import operator

import psycopg

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    iteration: int


def task_test():
    template = """Answer the question based ONLY on the following context. 
    If the answer is not in the context, say "I don't know".

    Context: {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    rag_chain = (
        {"context": fetch.get_retriver() | fetch.format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm.LLM
        | StrOutputParser()
    )

    queries = [
    "Explain how K8s handles the heavy lifting",
    "What programming language emphasizes code readability?",
    "Who invented the telephone?", # This should trigger the "I don't know" fallback
    "Explain the difference between Snowflake's traditional warehouse and its Lakehouse capabilities"
    ]

    for query in queries:
        print(f"Q: {query}")
        response = rag_chain.invoke(query)
        print(f"A: {response}\n" + "-"*50)


# Flight Agent
def flight_agent(state: AgentState):
    query = state["user_query"]
    flight_data = search.tavily_search(query)
    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content=f"Flight results fetched")
        ],
        "iteration": state.get("iteration", 0) + 1
    }

# Hotel Agent
def hotel_agent(state: AgentState):
    query = f"Best hotels for {state['user_query']}"
    hotel_results = search.tavily_search(query)


    return {    
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched")
        ],
        "iteration": state.get("iteration", 0) + 1
    }

# Itinerary Agent
def itinerary_agent(state: AgentState):

    prompt = f"""
    Create a travel itinerary.
    User Query:
    {state['user_query']}

    Flight Results:
    {state['flight_results']}

    Hotel Results:
    {state['hotel_results']}
    """

    response = llm.LLM.invoke([
        SystemMessage(
            content="You are an expert travel planner"
        ),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "iteration": state.get("iteration", 0) + 1
    }

# Final Response Agent
def final_agent(state: AgentState):

    final_prompt = f"""
    Generate final travel response.

    Flights:
    {state['flight_results']}

    Hotels:
    {state['hotel_results']}

    Itinerary:
    {state['itinerary']}
    """

    response = llm.LLM.invoke([
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "iteration": state.get("iteration", 0) + 1
    }

graph = StateGraph(AgentState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

import tools.db as db

_conn = psycopg.connect(db.DATABASE_URL)
_conn.autocommit = True
checkpointer = PostgresSaver(_conn)
checkpointer.setup()

app = graph.compile(checkpointer=checkpointer)



if __name__ == "__main__":
    #task_test()
    print("Starting the RAG Travel Agent...")
    config = {
        "configurable": {
            "thread_id": "23_JUNE_2024"
        }
    }

    user_input = input("Enter travel request: ")

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "iteration": 0
        },
        config=config
    )

    print("\nFINAL RESPONSE:\n")

    for msg in result["messages"]:
        print(msg.content)