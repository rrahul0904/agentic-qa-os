from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agents.registry import AGENTS
from app.agents.test_case_generator import run as run_test_case_generator
from app.core.config import settings
from app.models import AgentRunResponse, AgentSummary, TestCaseRunRequest

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "agentic-qa-api", "version": "0.1.0"}


@app.get("/api/v1/agents", response_model=list[AgentSummary])
def list_agents() -> list[AgentSummary]:
    return AGENTS


@app.post("/api/v1/agents/{agent_id}/run", response_model=AgentRunResponse)
def run_agent(agent_id: str, payload: TestCaseRunRequest) -> AgentRunResponse:
    if agent_id != "test-case-generator":
        raise HTTPException(status_code=409, detail=f"Agent '{agent_id}' is not executable yet")
    return run_test_case_generator(payload)
