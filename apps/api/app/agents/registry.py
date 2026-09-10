from app.models import AgentSummary


AGENTS = [
    AgentSummary(id="test-case-generator", name="Test Case Generator", description="Creates evidence-linked positive, negative and boundary tests from a requirement.", status="ready", capabilities=["test-design", "evidence-linking", "edge-cases"]),
    AgentSummary(id="requirement-clarifier", name="Requirement Clarifier", description="Finds ambiguity, missing acceptance criteria and testability gaps.", status="planned", capabilities=["requirements", "ambiguity-detection"]),
    AgentSummary(id="openapi-test-generator", name="OpenAPI Test Generator", description="Builds executable API scenarios from OpenAPI documents.", status="planned", capabilities=["api-testing", "openapi"]),
    AgentSummary(id="release-readiness", name="Release Readiness", description="Aggregates quality evidence into release risk and recommendation.", status="planned", capabilities=["quality-gate", "risk"]),
]
