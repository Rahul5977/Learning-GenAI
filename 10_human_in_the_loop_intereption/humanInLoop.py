from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import interrupt,Command
import json
load_dotenv()
import requests

@tool()
def human_assistance(query:str)->str:
    """_summary_

    Args:
        query (str): _description_

    Returns:
        str: _description_
    """
    human_response=interrupt({"query":query})# this saves the state in db and kills thr graph
    return human_response["data"]


tools=[human_assistance]
llm = init_chat_model(model_provider="openai", model="gpt-4.1-mini")
llm_with_tools = llm.bind_tools(tools)




class State(TypedDict):
    messages: Annotated[list, add_messages]
    
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}

tool_node=ToolNode(tools=tools)

graph_builder=StateGraph(State)
graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("tools",tool_node)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_conditional_edges("chatbot",tools_condition)

graph_builder.add_edge("tools","chatbot")

def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)


def user_side():
    MONGO_URI = "mongodb://admin:admin123@localhost:27017"
    config = {"configurable": {"thread_id": "21"}}
    with MongoDBSaver.from_conn_string(MONGO_URI) as mongo_checkpointer:
        graph_with_cp = create_chat_graph(mongo_checkpointer)
        while True:
            user_input=input("> ")
            state=State(
            messages=[{"role":"user","content":user_input}]
            )
            for event in graph_with_cp.stream(state,config,stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()

    
user_side()
def admin_side():
    DB_URI = "mongodb://admin:admin@mongodb:27017"
    config = {"configurable": {"thread_id": "21"}}

    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_cp = create_chat_graph(mongo_checkpointer)

        state = graph_with_cp.get_state(config=config)
        last_message = state.values['messages'][-1]

        tool_calls = last_message.additional_kwargs.get("tool_calls", [])

        user_query = None

        for call in tool_calls:
            if call.get("function", {}).get("name") == "human_assistance":
                args = call["function"].get("arguments", "{}")
                try:
                    args_dict = json.loads(args)
                    user_query = args_dict.get("query")
                except json.JSONDecodeError:
                    print("Failed to decode function arguments.")

        print("User Has a Query", user_query)
        solution = input("> ")

        resume_command = Command(resume={"data": solution})

        for event in graph_with_cp.stream(resume_command, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()
                
