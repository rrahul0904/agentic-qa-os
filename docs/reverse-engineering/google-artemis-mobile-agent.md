# Google ARTEMIS → Agentic QA OS mobile execution capability

Tracker: **RE-228**

Source:
- Reddit: https://www.reddit.com/r/OpenSourceAI/s/1u41DiNd0I
- Upstream: https://github.com/google/artemis
- MCP overview: https://github.com/google/artemis/tree/main/mcp_server
- AndroidWorld: https://github.com/google-research/android_world

## Why this belongs in Agentic QA OS

ARTEMIS is best treated as a **mobile/device-execution capability donor**, not as a separate generic agent platform.

Agentic QA OS already has a control plane, agent registry/runtime, evidence model, and the beginning of execution-worker patterns. The missing capability is a governed mobile target runtime that can observe, act, verify, collect evidence, and expose that execution boundary to test-design agents.

The clean-room target is therefore:

```text
Agentic QA control plane
        |
        v
Mobile Test Agent / Planner
        |
        v
Mobile Execution Runtime
  + device inventory + selection
  + per-device lease / FIFO lock
  + observation pipeline
  + action dispatcher
  + verification / assertion layer
  + trace + artifact capture
        |
        +--> Android adapter (ADB + UI hierarchy + screenshot)
        |
        +--> future iOS adapter
        |
        v
Evidence Layer / release-readiness consumers
```

## Public behavior verified from ARTEMIS

The public project describes:

- natural-language Android task execution across apps;
- use of accessibility/UI hierarchy, screenshots, OCR/vision, and coordinate fallbacks;
- ADB-based device connectivity;
- screenshot, Logcat, trace, and replay artifacts;
- MCP tools for external coding assistants;
- multiple-device support with per-device mutual exclusion;
- a fast reactive execution profile and a slower planning/verification profile;
- pre-execution target checks in the deeper profile;
- diagnostic readiness checks for credentials, ADB, devices, and emulator state;
- web console, CLI, MCP, and SDK surfaces;
- an AndroidWorld benchmark claim of 99%+ task completion.

This document records the observable product/runtime concepts only. It does **not** reproduce upstream source, prompts, tests, or implementation details.

## Clean-room architecture contract

### 1. Device inventory

Introduce a provider-neutral device model:

```text
MobileDevice
- device_id
- provider            # android_adb | android_emulator | ios_future
- serial
- display_name
- os_name
- os_version
- model
- state               # ready | busy | unauthorized | offline | blocked
- capabilities[]
- last_seen_at
```

Rules:
- explicit device selection wins;
- when multiple devices are ready and no target is specified, do not silently choose one in interactive workflows;
- one active execution lease per device;
- separate devices may run concurrently.

### 2. Observation contract

```text
MobileObservation
- observation_id
- device_id
- captured_at
- screenshot_artifact_id
- hierarchy_artifact_id
- visible_text[]
- focused_element
- orientation
- screen_width
- screen_height
- candidate_targets[]
```

Target candidates should preserve provenance:

```text
MobileTargetCandidate
- target_id
- source              # resource_id | accessibility | text | ocr | vision | coordinate
- selector
- bounds
- confidence
- evidence_refs[]
```

The runtime should prefer structural selectors first, then OCR/vision-derived targets, and use raw coordinates only as an explicit fallback.

### 3. Action contract

```text
MobileAction
- action_id
- kind                # tap | long_press | type | swipe | back | home | launch | wait
- target
- text
- vector
- timeout_ms
- destructive_risk
- requires_approval
```

Phase A intentionally excludes arbitrary shell commands. A future diagnostic ADB command surface should be separately allowlisted and approval-gated.

### 4. Task + trace model

```text
MobileTask
- task_id
- run_id
- device_id
- goal
- profile
- status
- created_at
- started_at
- finished_at

MobileTraceStep
- step_id
- task_id
- ordinal
- observation_before
- proposed_action
- safety_decision
- execution_result
- observation_after
- assertion_results[]
- artifact_refs[]
- latency_ms
```

Every claim that the UI changed should be backed by a post-action observation or another measured artifact.

### 5. Profiles

Do not copy ARTEMIS profile internals. Recreate the product distinction through our own contracts.

**Reactive**
- observe → decide → act → observe;
- bounded step/time budget;
- no persistent planning graph required;
- optimized for short deterministic flows.

**Verified**
- explicit plan + checkpoints;
- pre-action target validation;
- assertion/checkpoint evaluation;
- blocked-action incident state;
- final verification against the original goal.

Both profiles use the same trace ledger and evidence schema.

### 6. Safety and governance boundary

The mobile runtime should fail closed by default.

Required controls:
- authorized device inventory only;
- explicit user/CI ownership metadata for physical devices;
- per-device execution lease;
- package allowlist for launch/install in CI;
- approval gate before APK install/upgrade on non-ephemeral devices;
- no arbitrary ADB shell in the first implementation slice;
- no hidden file extraction;
- secrets/log redaction before persistence;
- artifact retention policy;
- immutable trace IDs and evidence references;
- cancellation and dead-worker lease recovery;
- deterministic maximum action/time budgets.

Potentially destructive actions such as account deletion, purchases, security-setting changes, device reset, or permission escalation must never be inferred as routine UI navigation.

## MCP boundary

Expose Agentic QA OS capabilities through a provider-neutral MCP layer later, after the runtime contract is stable.

Proposed tools:

```text
mobile_list_devices
mobile_get_device_state
mobile_run_test
mobile_get_task
mobile_cancel_task
mobile_get_trace
mobile_diagnose
```

The MCP layer should not bypass policy, approval, leases, evidence capture, or audit.

## Proposed implementation phases

### Phase A — repository-certified deterministic contract

Goal: prove the runtime model without touching a real device.

Implement:
- Pydantic/domain models for device, observation, target, action, task, trace, artifact, assertion and safety decision;
- provider-neutral `MobileExecutionAdapter`;
- deterministic fake-device adapter;
- in-memory device lease manager;
- task lifecycle + cancellation;
- trace/evidence capture;
- policy checks for unsupported/destructive actions;
- focused API endpoints;
- unit and integration tests.

Acceptance:
- two different fake devices can run concurrently;
- two tasks cannot hold the same device simultaneously;
- every action has before/after evidence references;
- blocked actions do not execute;
- cancelled tasks release the lease;
- no code path claims Android/ADB execution.

### Phase B — authorized Android adapter

Implement:
- ADB discovery/readiness;
- screenshot capture;
- UI hierarchy capture via an independently designed adapter;
- bounded tap/type/swipe/back/home/launch actions;
- per-device lease;
- Logcat capture scoped to the run;
- emulator and physical-device metadata;
- deterministic failure reasons for offline/unauthorized devices.

Do not add OCR/VLM grounding yet.

### Phase C — MCP + CI/emulator integration

Implement:
- MCP facade over existing API/runtime;
- Android emulator CI lane;
- evidence bundle upload;
- exact-head smoke using a deterministic sample app;
- device wizard/diagnostics API.

### Phase D — resilient grounding

Add:
- OCR adapter;
- vision-model adapter;
- target-candidate fusion;
- structural-first fallback rules;
- target confidence + provenance;
- locator robustness tests across screen sizes/layout changes.

### Phase E — verified long-horizon planner

Add:
- living test plan;
- checkpoint assertions;
- blocked-action incident state;
- final goal verification;
- bounded history summarization/search;
- budgets and cost/latency telemetry.

## Test plan

Repository-level:
- model validation;
- lease/concurrency;
- cancellation;
- safety decisions;
- task state transitions;
- trace completeness;
- artifact linkage;
- MCP contract tests;
- adapter conformance tests.

Hosted/device certification:
- emulator boot/readiness;
- physical-device authorization;
- install/launch/sample workflow;
- screenshot + hierarchy parity;
- rotation handling;
- transient UI;
- cross-app navigation;
- offline/unauthorized recovery;
- Logcat capture;
- Chrome + native app flows;
- repeated-run flake rate.

Benchmark claims must be independently reproduced before being mentioned for our implementation.

## Provenance and legal boundary

The current ARTEMIS README states the project is Apache-2.0 and acknowledges source code developed by Minitap, Inc.

There is also a public attribution dispute in the upstream issue tracker, including:
- https://github.com/google/artemis/issues/40
- https://github.com/google/artemis/issues/61

Those issues contain allegations and counter-context; this repository does not adjudicate them.

Because of that provenance history, this work uses a stricter boundary than the license alone requires:

1. do not copy ARTEMIS/Minitap source files;
2. do not copy prompts, rules files, tests, sample implementations, or internal naming beyond generic interoperability terms;
3. derive contracts from public product behavior and independent engineering requirements;
4. implement adapters and tests from scratch;
5. keep source URLs and provenance notes in this document;
6. preserve third-party licenses for any dependencies we independently choose.

## Explicit non-claims

At this research checkpoint, Agentic QA OS does **not** claim:
- a working ADB/mobile executor;
- physical-device support;
- emulator certification;
- MCP mobile tools;
- OCR or vision grounding;
- iOS automation;
- AndroidWorld benchmark results;
- parity with ARTEMIS;
- production readiness.

## Smallest next executable slice

Implement **Phase A only**: the provider-neutral mobile execution contracts, deterministic fake adapter, per-device lease manager, trace/evidence lifecycle, fail-closed action policy, focused tests, and exact-head CI.

That is enough to establish the architecture truthfully without prematurely depending on ADB, real-device labs, external models, or benchmark infrastructure.
