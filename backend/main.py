import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from pathlib import Path

# Import the agent
from agent import github_card_agent

app = FastAPI(title="GitHub Dev Card Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InMemoryMemoryService:
    def __init__(self):
        self.history = {}
    def get_history(self, session_id: str):
        return self.history.get(session_id, [])
    def add_to_history(self, session_id: str, message: str):
        if session_id not in self.history:
            self.history[session_id] = []
        self.history[session_id].append(message)

class InMemorySessionService:
    def __init__(self):
        self.sessions = {}
    def get_or_create_session(self, username: str):
        if username not in self.sessions:
            self.sessions[username] = {"username": username}
        return username

memory_service = InMemoryMemoryService()
session_service = InMemorySessionService()

class Runner:
    def __init__(self, agent, memory, sessions):
        self.agent = agent
        self.memory = memory
        self.sessions = sessions
    async def run(self, username: str):
        session_id = self.sessions.get_or_create_session(username)
        result = await self.agent.generate_card(username)
        if result["status"] == "success":
            self.memory.add_to_history(session_id, f"Generated card for {username}")
            return result
        else:
            raise Exception(result.get("message", "Unknown error"))

runner = Runner(github_card_agent, memory_service, session_service)

class GenerateRequest(BaseModel):
    username: str

@app.post("/api/generate")
async def generate(request: GenerateRequest):
    try:
        result = await runner.run(request.username)
        return {
            "status": "success",
            "username": result["username"],
            "card_url": result["card_url"],
            "card_html": result["card_html"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/card/{username}")
async def get_card(username: str):
    # Absolute path fix for reliable serving
    base_dir = Path(__file__).resolve().parent
    card_path = base_dir / "static" / "cards" / f"{username}.html"
    
    if not card_path.exists():
        raise HTTPException(status_code=404, detail="Card not found. Please generate it first.")
    
    return FileResponse(card_path)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "github-card-generator"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
