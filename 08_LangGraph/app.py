from typing_extensions import TypedDict
from openai import OpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()
client =OpenAI()
class State(TypedDict):
    query: str
    llm_result:str
    
def chat_bot(state: State):
    #code likh skte h
    #open ai call
    query=state['query']
    #llm call (openai)
    llm_response=client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":query}]
    )
    result=llm_response.choices[0].message.content
    
    state['llm_result']=result
    
    
    #edges banane h ab
    
    return state


graph_builder=StateGraph(State)

graph_builder.add_node("chat-bot",chat_bot)

graph_builder.add_edge(START,"chat-bot")
graph_builder.add_edge("chat-bot",END)

graph=graph_builder.compile()

def main():
    user =input("> ")
    
    #invoke the graph
    _state={
        "query": user, 
        "llm_result":None
    }
    graph_result =graph.invoke(_state)
    
    print("graph result :",graph_result)
    
main()