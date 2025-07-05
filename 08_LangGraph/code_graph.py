from typing_extensions import TypedDict
from openai import OpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from typing import Literal

load_dotenv()
client =OpenAI()

class CodeAccuracyResponse(BaseModel):
    accuracy_percentage:str

class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool

class State(TypedDict):
    user_query: str
    llm_result: str | None
    accuracy_percentage: str | None
    is_coding_question: bool | None
    
    
def classify_message(state:State):
    print("⚠️ classify_message")
    query = state["user_query"]

    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if the user's query is
    related to coding question or not.
    Return the response in specified JSON boolean only.
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ClassifyMessageResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )

    is_coding_question = response.choices[0].message.parsed.is_coding_question
    state["is_coding_question"] = is_coding_question

    return state

def route_query(state:State) -> Literal["general_query","coding_query"]:
    print("⚠️ route_query")
    is_coding = state["is_coding_question"]

    if is_coding:
        return "coding_query"

    return "general_query"
    pass

def general_query(state:State):
    print("⚠️ general_query")
    query = state["user_query"]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": query}
        ]
    )

    state["llm_result"] = response.choices[0].message.content

    return state
    pass

def coding_query(state:State):
    print("⚠️ Coding Query")
    query=state["user_query"]
    SYSTEM_PROMPT="""
        You are an Coding expert agent. write code in python unless untill user specifies the coding language.
    """
    response =client.chat.completions.create(
        model="gpt-4.1",
        messages=[{
            "role":"system","content":SYSTEM_PROMPT
        },{"role":"user","content":query}]
    )
    state["llm_result"]=response.choices[0].message.content
    return state
    pass

def coding_validate_query(state:State):
    print("⚠️ Coding validate Query")
    query=state["user_query"]
    llm_code=state["llm_result"]
    SYSTEM_PROMPT=f"""
        you are expert in calculating accuracy of the code according to the question
        userQuery={query}
        code={llm_code}
    """
    # call gemini for validation 
    response = client.beta.chat.completions.parse(
        model="gpt-4.1",
        response_format=CodeAccuracyResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )

    state["accuracy_percentage"] = response.choices[0].message.parsed.accuracy_percentage
    return state

graph_builder=StateGraph(State)



# make nodes
graph_builder.add_node("classify_message",classify_message)
graph_builder.add_node("route_query",route_query)
graph_builder.add_node("general_query",general_query)
graph_builder.add_node("coding_query",coding_query)
graph_builder.add_node("coding_validate_query",coding_validate_query)

# edges 
graph_builder.add_edge(START,"classify_message")
graph_builder.add_conditional_edges("classify_message",route_query)
graph_builder.add_edge("general_query",END)
graph_builder.add_edge("coding_query","coding_validate_query")
graph_builder.add_edge("coding_validate_query",END)

graph=graph_builder.compile()

def main():
    user=input("> ")
    _state={
        "user_query": user,
        "llm_result": None,
        "accuracy_percentage": None ,
        "is_coding_question": False
    }
    # response=graph.invoke(_state)
    # print("Response :",response)
    for event in graph.stream(_state):
        print(event)


main()
