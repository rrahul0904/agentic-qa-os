# ChronoMock reverse-engineering map

Source: https://github.com/donislawdev/ChronoMock  
Pinned upstream head reviewed: `cc7035a6ce609fac85334cff2261d3163bc58a0a` (2026-09-22)  
License observed upstream: GPL-3.0-only

## Decision

ChronoMock is a **capability donor** for Agentic QA OS, not a code donor and not a standalone product in this portfolio.

The clean-room target is an evidence-aware temporal testing capability that can plan date/time scenarios now and later execute them through an authorized Windows worker. No GPL implementation is copied into this repository.

## Donor capability map

1. **Process-scoped time control**: alter what one target process sees without changing the machine clock.
2. **Multiple clock modes**: shifted/flowing time, frozen time, accelerated time, and mid-session forward/backward jumps.
3. **Per-session time zone**: independent fixed offset for the target session.
4. **Child-process coverage**: follow launchers/installers into spawned children rather than testing only the parent.
5. **Measured time-source audit**: report which time channels were actually used, call counts, uncovered paths, warnings, and an explicit verdict.
6. **Native and web-runtime paths**: native Windows interception plus a separate Chromium/DevTools-style mechanism for sandboxed renderers and embedded web engines.
7. **QA date calculator**: deterministic boundary scenarios, date arithmetic, output formats, business-day and holiday calendars.
8. **GUI + CLI parity**: one engine surfaced interactively and through automation/CI.
9. **Portable/non-admin operating model**: avoid changing the system clock, avoid elevation as a requirement, and leave bounded artifacts.
10. **Release assurance**: x86/x64 coverage, dependency/licence gates, security checks, package smoke tests, checksums/SBOM/attestation/signing discipline.

## Clean-room product contract

### Phase A — scenario design (implemented in this branch)

- Add `temporal-test-designer` to the common agent registry.
- Generate evidence-linked scenarios for:
  - year rollover,
  - month-end,
  - leap-day/non-leap behavior,
  - the 2038 boundary,
  - backward clock movement,
  - accelerated/frozen time.
- State plainly that this is planning evidence only, not proof of clock substitution.

### Phase B — execution contract

Create an explicit execution request containing:

- target executable and arguments,
- working directory,
- absolute or relative target time,
- rate: normal / frozen / accelerated,
- optional wall-clock jump sequence,
- optional fixed UTC offset,
- child-process policy,
- native vs browser/embedded adapter selection,
- maximum run duration,
- expected evidence channels.

The worker must accept only explicitly authorized targets and keep execution evidence separate from the planner output.

### Phase C — Windows worker

Build a Windows-only worker behind the control plane with a narrow responsibility:

- start the selected target,
- apply the configured process-scoped time mechanism,
- propagate only to the selected target family,
- enforce timeout/cleanup,
- return machine-readable evidence.

The control plane should not contain Windows injection details. That keeps privilege, packaging, antivirus, bitness, and low-level failure modes isolated.

### Phase D — browser and embedded web coverage

Provide a separate adapter for Chromium/Electron and embedded engines where native process control is insufficient. Treat the browser-side channel as a distinct evidence source and never merge it into a native verdict without preserving provenance.

### Phase E — measured audit

A temporal execution result is not complete merely because the target launched. Evidence must record:

- requested scenario,
- effective target instant/rate,
- process family covered,
- clock channels observed,
- per-channel call/read counts when measurable,
- channels explicitly not covered,
- browser/native evidence separately,
- warnings and consequences,
- final verdict,
- whether the application ever read a controlled clock at all.

A "works" mechanism verdict must not be interpreted as "the application exercised the fake clock" unless read evidence supports that stronger statement.

### Phase F — product surfaces

- Operator UI: scenario builder, target selection, live session state, evidence view, stop control.
- CLI/CI: deterministic JSON contract and stable exit status categories.
- History: immutable session evidence suitable for release-readiness aggregation.
- Presets/calendars: source-cited data files with tests.
- Admin: worker inventory, policy, session ownership, diagnostics, and failure distribution.

## Security and product boundaries

- Do not change the host system clock.
- Do not require or auto-acquire administrator rights.
- Do not turn this into a licensing bypass feature; the product use case is authorized QA of software the operator is responsible for.
- Do not report silent success when the controlled channel was bypassed.
- Treat process injection / debug-port mechanics as high-risk implementation surfaces with explicit authorization, process scoping, cleanup, and audit logs.
- Keep target-created future-dated data outside the worker's cleanup guarantee; the operator must know it can persist.
- Preserve a strict distinction between repository implementation, local Windows certification, and hosted worker certification.

## Repository status after this slice

Implemented:
- clean-room donor map,
- Temporal Test Designer registry entry,
- executable deterministic scenario planner,
- evidence-linked API response,
- API tests,
- architecture boundary.

Not implemented:
- Windows process-time control,
- native hook/injection runtime,
- x86/x64 worker packaging,
- child-process propagation,
- Chromium/WebView clock adapter,
- time-channel measurement,
- session verdict engine,
- Windows end-to-end certification,
- operator UI for temporal sessions,
- hosted worker/admin surfaces.

## Smallest next implementation

Define the **execution/evidence schemas and worker interface** before building any low-level Windows mechanism. The first executable worker milestone should be a harmless Windows probe that launches a test fixture, records real clock channels, and returns signed/hashed session evidence without modifying time. That validates authorization, process scoping, child tracking, evidence ingestion, cleanup, and CI contracts before adding time substitution.
