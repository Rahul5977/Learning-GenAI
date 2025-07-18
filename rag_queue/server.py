from fastapi import FastAPI, Query
from src.connection import queue 
from src.worker import proecess_query
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Server is running"}


@app.post("/chat")
def chat(query: str = Query(..., description="User query")):
    # query ko queue me dalo
    job=queue.enqueue(proecess_query,query)
    # job ko process karne ke liye worker ko bhej do
    return {"status": "queued", "job_id": job.id}
    # job id return karo taaki user ko pata chale ki job queue me hai
