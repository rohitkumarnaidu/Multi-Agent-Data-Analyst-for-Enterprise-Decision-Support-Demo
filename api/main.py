from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.crew import create_crew

app = FastAPI(title="Multi-Agent Data Analyst API")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        crew = create_crew(request.query)
        # kickoff() returns a string or object depending on crewai version; cast to string
        result = str(crew.kickoff())
        return ChatResponse(answer=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
