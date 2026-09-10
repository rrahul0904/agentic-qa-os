from uuid import uuid4

from app.models import AgentRunResponse, Evidence, TestCase, TestCaseRunRequest, TestStep


def _evidence(req: TestCaseRunRequest) -> list[Evidence]:
    return [Evidence(source_id=req.source_id or "inline-requirement", excerpt=req.requirement[:500], relation="direct requirement basis")]


def run(req: TestCaseRunRequest) -> AgentRunResponse:
    evidence = _evidence(req)
    requirement = req.requirement.strip()
    cases = [
        TestCase(id="TC-POS-001", title="Verify the primary requirement succeeds under valid conditions", kind="positive", priority="P0", preconditions=["System is available", "User has valid prerequisite state"], steps=[TestStep(action=f"Execute the user flow described by: {requirement}", expected="The requested behavior completes successfully."), TestStep(action="Observe the externally visible result", expected="The result matches the requirement with no unexpected error.")], evidence=evidence),
        TestCase(id="TC-NEG-001", title="Verify invalid or missing prerequisite data is handled safely", kind="negative", priority="P1", preconditions=["System is available"], steps=[TestStep(action="Attempt the requirement flow with a required prerequisite missing or invalid", expected="The operation is rejected or safely handled."), TestStep(action="Inspect user-facing and system behavior", expected="A useful error is produced and no corrupt state is created.")], evidence=evidence),
        TestCase(id="TC-BND-001", title="Verify requirement behavior at an input or state boundary", kind="boundary", priority="P2", preconditions=["A boundary value or edge state relevant to the requirement can be constructed"], steps=[TestStep(action="Execute the flow at the smallest or largest valid boundary", expected="The valid boundary is accepted consistently."), TestStep(action="Execute immediately outside that boundary", expected="The invalid boundary is rejected predictably.")], evidence=evidence),
    ]
    return AgentRunResponse(run_id=str(uuid4()), agent_id="test-case-generator", status="completed", confidence=0.78, test_cases=cases, warnings=["Generated from a single inline requirement; connect Jira/ADO and acceptance criteria for stronger traceability."])
