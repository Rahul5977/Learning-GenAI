from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from dotenv import load_dotenv
import os

load_dotenv()

# Define your agent's state schema
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the LLM
llm = init_chat_model(model_provider="openai", model="gpt-4.1")

# Chat function to handle messages
def chat_model(state: State) -> State:
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}  # Correct: append response

# Graph definition
graph_builder = StateGraph(State)
graph_builder.add_node("chat_model", chat_model)
graph_builder.set_entry_point("chat_model")  # ✅ cleaner alternative to add_edge(START, ..)
graph_builder.add_edge("chat_model", END)

# Compile once here for default execution
graph = graph_builder.compile()

# Function to compile with a checkpointer
def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

# Main app logic
def main():
    MONGO_URI = "mongodb://admin:admin123@localhost:27017"
    config = {"configurable": {"thread_id": "1"}}

    with MongoDBSaver.from_conn_string(MONGO_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

        
        query = input("> ")
        

        result = graph_with_mongo.invoke(
            {"messages": [{"role": "user", "content": query}]}, config)

        print(result)

main()
