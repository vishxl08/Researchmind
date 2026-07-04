import os
import django
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from agent.runner import run_agent
from research.models import ResearchJob

app = FastAPI(title="ResearchMind Agent Service", version="1.0")

class JobTrigger(BaseModel):
    job_id: int

@app.get("/")
def index():
    return {"status": "ok", "message": "ResearchMind FastAPI Agent Service is running."}

@app.post("/run-agent/")
def trigger_agent(payload: JobTrigger, background_tasks: BackgroundTasks):
    """Triggers the agent runner for a ResearchJob as a background task."""
    try:
        # Check if job exists
        job = ResearchJob.objects.get(id=payload.job_id)
    except ResearchJob.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"ResearchJob with ID {payload.job_id} not found.")

    # Run agent in background thread using FastAPI's background tasks
    background_tasks.add_task(run_agent, payload.job_id)
    
    return {
        "status": "triggered",
        "job_id": payload.job_id,
        "query": job.query
    }
