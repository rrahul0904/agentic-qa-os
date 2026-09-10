from typing import Literal
from pydantic import BaseModel, Field


class AgentSummary(BaseModel):
    id: str
    name: str
    description: str
    status: Literal["ready", "planned"]
    capabilities: list[str]


class TestCaseRunRequest(BaseModel):
    requirement: str = Field(min_length=5, max_length=10_000)
    source_id: str | None = Field(default=None, max_length=200)


class Evidence(BaseModel):
    source_id: str
    excerpt: str
    relation: str


class TestStep(BaseModel):
    action: str
    expected: str


class TestCase(BaseModel):
    id: str
    title: str
    kind: Literal["positive", "negative", "boundary"]
    priority: Literal["P0", "P1", "P2", "P3"]
    preconditions: list[str]
    steps: list[TestStep]
    evidence: list[Evidence]


class AgentRunResponse(BaseModel):
    run_id: str
    agent_id: str
    status: Literal["completed", "failed"]
    confidence: float = Field(ge=0, le=1)
    test_cases: list[TestCase]
    warnings: list[str] = []
