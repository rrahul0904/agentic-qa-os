from uuid import uuid4

from app.models import AgentRunResponse, Evidence, TestCase, TestCaseRunRequest, TestStep


def _evidence(req: TestCaseRunRequest) -> list[Evidence]:
    return [
        Evidence(
            source_id=req.source_id or "inline-requirement",
            excerpt=req.requirement[:500],
            relation="direct requirement basis",
        )
    ]


def run(req: TestCaseRunRequest) -> AgentRunResponse:
    evidence = _evidence(req)
    requirement = req.requirement.strip()

    cases = [
        TestCase(
            id="TIME-YEAR-001",
            title="Verify behavior across a year rollover",
            kind="boundary",
            priority="P0",
            preconditions=["A controlled test environment can set or simulate application time"],
            steps=[
                TestStep(
                    action=f"Exercise the flow described by: {requirement} immediately before year end",
                    expected="Behavior matches the requirement before the calendar boundary.",
                ),
                TestStep(
                    action="Repeat immediately after the year changes",
                    expected="The boundary does not create an off-by-one year, expiry, or rollover defect.",
                ),
            ],
            evidence=evidence,
        ),
        TestCase(
            id="TIME-MONTH-002",
            title="Verify month-end and next-month transition",
            kind="boundary",
            priority="P0",
            preconditions=["The flow has date-sensitive state or persistence"],
            steps=[
                TestStep(
                    action="Run at the final valid instant of a month, including a short month where applicable",
                    expected="Month-end behavior completes without truncation or invalid date construction.",
                ),
                TestStep(
                    action="Advance into the first instant of the next month and repeat",
                    expected="State transitions once and remains consistent after the boundary.",
                ),
            ],
            evidence=evidence,
        ),
        TestCase(
            id="TIME-LEAP-003",
            title="Verify leap-day and non-leap-year handling",
            kind="boundary",
            priority="P1",
            preconditions=["The feature can encounter February calendar arithmetic"],
            steps=[
                TestStep(
                    action="Exercise the requirement on February 29 in a leap year",
                    expected="Leap-day input is accepted and computed consistently.",
                ),
                TestStep(
                    action="Exercise the equivalent path in a non-leap year",
                    expected="The application does not manufacture an invalid February 29 date.",
                ),
            ],
            evidence=evidence,
        ),
        TestCase(
            id="TIME-2038-004",
            title="Verify the 2038 boundary and large future timestamps",
            kind="boundary",
            priority="P1",
            preconditions=["The application or one of its dependencies may use Unix-style timestamps"],
            steps=[
                TestStep(
                    action="Exercise the requirement immediately before and after 2038-01-19T03:14:07Z",
                    expected="Timestamp conversion, persistence, sorting, and expiry logic remain valid.",
                ),
            ],
            evidence=evidence,
        ),
        TestCase(
            id="TIME-ROLLBACK-005",
            title="Verify a backward clock jump is handled safely",
            kind="negative",
            priority="P0",
            preconditions=["The feature measures elapsed time or compares timestamps"],
            steps=[
                TestStep(
                    action="Begin the requirement flow, then move the application-visible wall clock backward",
                    expected="The application does not produce negative durations, duplicate work, or corrupt state.",
                ),
            ],
            evidence=evidence,
        ),
        TestCase(
            id="TIME-RATE-006",
            title="Verify accelerated and frozen time semantics",
            kind="boundary",
            priority="P1",
            preconditions=["A future execution adapter can independently control wall-clock rate"],
            steps=[
                TestStep(
                    action="Run the flow with time accelerated, then with the application-visible wall clock frozen",
                    expected="Date-based behavior follows the controlled clock while duration-sensitive behavior is explicitly classified.",
                ),
            ],
            evidence=evidence,
        ),
    ]

    return AgentRunResponse(
        run_id=str(uuid4()),
        agent_id="temporal-test-designer",
        status="completed",
        confidence=0.86,
        test_cases=cases,
        warnings=[
            "This agent designs temporal scenarios only; it does not yet alter a target process clock.",
            "A future execution adapter must prove which clock channels were actually controlled before a run can count as execution evidence.",
        ],
    )
