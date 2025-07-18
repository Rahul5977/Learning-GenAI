from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.connection import queue
from src.worker import process_query
from rq.job import Job
class ChatRequest(BaseModel):
    query: str

app = FastAPI(
    title="RAG API Server",
    description="An API to submit queries to a RAG pipeline via a background worker.",
)

@app.get("/", tags=["Status"])
def read_root():
    """A simple health check endpoint to confirm the server is running."""
    return {"status": "Server is running"}


@app.post("/chat", tags=["Chat"])
def chat(request: ChatRequest):
    """
    Receives a query, enqueues it for processing by a worker,
    and returns the job ID.
    """
    print(f"Received query: '{request.query}'. Enqueuing job...")
    job = queue.enqueue(process_query, request.query)
    return {"status": "queued", "job_id": job.id}


    """
    Fetches the result of a job using its ID.
    """
    try:
        # Fetch the job instance from the queue connection.
        job = Job.fetch(job_id, connection=queue.connection)

        if job.is_finished:
            return {"status": "completed", "job_id": job.id, "result": job.result}
        elif job.is_queued:
            return {"status": "queued", "job_id": job.id}
        elif job.is_started:
            return {"status": "running", "job_id": job.id}
        elif job.is_failed:
            return {"status": "failed", "job_id": job.id, "error": job.exc_info}
            
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found or invalid job ID: {e}")

    return {"status": "unknown", "job_id": job_id}

