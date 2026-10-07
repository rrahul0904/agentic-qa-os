# Phonebox cloud Android donor — evidence-first reverse engineering

**Date:** 2026-10-06  
**Target:** Phonebox (`phonebox.dev`)  
**Source thread:** https://www.reddit.com/r/SideProject/comments/1wudnby/i_built_an_android_phone_in_the_cloud_that_ai/  
**Canonical destination:** Agentic QA OS  
**Decision:** capability donor; do not create a duplicate standalone clone

## 1. Source identification

Phonebox is presented as cloud-hosted Android infrastructure for AI agents. The product is not the agent/model itself. It provides a persistent Android execution surface and device-control interfaces that an external agent can call.

### Evidence classes

| Evidence | Class | What it supports |
|---|---|---|
| Reddit SideProject launch post | creator-public | Product positioning, persistence, browser takeover, MCP/CLI/SDK/API, launch pricing |
| Reddit r/mcp launch post | creator-public | Screenshot + numbered UI-element observation model; external model/agent boundary |
| `phonebox.dev` | first-party-public | Product existence/landing page only; public crawler currently exposes little structured content |
| PhoneBase public site/docs | competitor-official | Real Android cloud-phone lifecycle, CLI observation/action model, snapshots/persistence and current pricing |
| Mobilerun public site/docs/GitHub | competitor-official / official-source | Hosted + local Android/iOS control, MCP/API/SDK, real/virtual devices, deterministic core and safety boundary |
| AWS Device Farm docs/pricing | competitor-official | Real-device remote access, session recording/logging, device-minute pricing |

No Phonebox source code was identified. This is therefore black-box / public-evidence reverse engineering. Do not copy proprietary implementation, prompts, UI assets or branding.

## 2. Observed product behavior

Public creator claims establish the following behavior:

1. Provision or access an Android phone in the cloud.
2. Connect an external AI agent through MCP, CLI, SDK or REST API.
3. Observe the phone through a screenshot plus numbered UI elements.
4. Execute small UI actions such as tap, type, swipe and app launch.
5. Keep applications and device data when the phone is parked.
6. Resume the same phone state in a later task/session.
7. Allow a human to open the phone in a browser for sign-in, 2FA or other intervention.
8. Hand control back to the agent after the human step.
9. Charge only while the phone is active; creator launch pricing states $0.06 per phone-minute, billed per second with a one-minute minimum. Parked phones are stated to be free.

## 3. Reconstructed core workflow

```text
agent/model
   |
   | MCP / CLI / SDK / REST
   v
mobile control plane
   |
   +--> acquire device lease
   +--> start/resume persistent Android device
   +--> observe: screenshot + compact/numbered UI representation
   +--> act: tap/type/swipe/launch
   +--> verify resulting state
   |
   +--> AUTH/CAPTCHA/2FA boundary?
          |
          +--> pause agent control
          +--> browser human takeover
          +--> return control to agent
   |
   +--> park device without destroying apps/data
   v
persistent device state
```

The critical product loop is therefore **observe -> decide -> small action -> observe again**, wrapped by lifecycle, persistence, lease ownership and human-handoff controls.

## 4. User problem and product thesis

The user problem is not simply 'run Android in the cloud.' Commodity emulators/device farms already exist. The useful product abstraction is:

> Give an existing agent a governed, resumable mobile body that can reach app-only workflows and safely yield control to a human when authentication or consent requires it.

This matters for workflows where:

- there is no stable public API;
- the business workflow is mobile-app-only;
- app state/login must persist across tasks;
- an agent can perform most steps but a human must occasionally authenticate or approve;
- developers need evidence and deterministic control boundaries rather than a hidden one-shot agent.

## 5. Feedback and failure-mode analysis

The strongest useful feedback in the companion r/mcp thread is that human takeover is valuable specifically around sign-in, 2FA and CAPTCHA, while another commenter points out the commodity alternative: an agent can control a local emulator or physical device over ADB.

That creates the central product challenge: **Phone hosting alone is not defensible.** A stronger implementation must add operational guarantees around persistence, ownership, safety, recovery and evidence.

Expected failure modes:

- stale or ambiguous UI hierarchy;
- screenshot/UI-tree disagreement;
- coordinate drift after orientation or keyboard changes;
- long actions blocking interactive observation;
- device lease collisions between agents;
- agent continuing to act during human takeover;
- lost app/login state after park/resume;
- auth secrets leaking into logs/screenshots;
- privileged actions (install, shell, payment/destructive consent) executing without authorization;
- network/device disconnect while a task is in progress;
- an agent declaring completion without validating the resulting mobile state.

## 6. Competitive comparison

### PhoneBase

Public docs show cloud Android phones controlled by a `pb` CLI, screenshot + UI-layout inspection, persistent/snapshot/stateless session modes, four regions, APK installation and agent skills. Current public pay-as-you-go pricing is listed as $0.10/device/hour, with lower packaged hourly rates.

Implication: competing only on inexpensive Android runtime is a race to commodity infrastructure.

### Mobilerun / DroidRun

Public docs/source show a broader phone layer: Android and iOS, local and hosted devices, MCP, REST/SDK, CLI/Python, screenshot + accessibility-tree control, real/virtual device options, deterministic scripting, agent execution, fleet workflows and explicit human-in-the-loop safety guidance.

Implication: parity requires a modular control plane, not a Phonebox-specific client.

### AWS Device Farm

AWS provides browser remote access to physical devices, videos/logs and automated testing. Public pay-as-you-go pricing is $0.17/device-minute, with slot plans and private devices.

Implication: general-purpose device-farm infrastructure already serves QA/debugging; our wedge should be agent-native governed execution rather than device testing alone.

## 7. Audit of our existing projects

The master tracker already maps Google ARTEMIS into `rrahul0904/agentic-qa-os` as the canonical mobile-execution destination. That donor established planning/perception/operator/verification concepts and a future Android adapter, but the tracker explicitly records that provider-neutral contracts, fake adapter, per-device leases, trace lifecycle and fail-closed action policy were not yet implemented.

Phonebox fills a complementary gap:

- ARTEMIS emphasizes autonomous mobile testing/execution.
- Phonebox emphasizes persistent hosted-device lifecycle and human takeover.
- SessionGrid contains related persistent-session ideas, but splitting mobile execution into another product would duplicate runtime ownership.

Decision: consolidate Phonebox as a capability donor into Agentic QA OS. Future infrastructure may reuse SessionGrid-style streaming/session primitives, but the mobile execution contract remains owned here.

## 8. Target boundary

### P0 — build now

- provider-neutral mobile device/session contracts;
- deterministic fake adapter;
- per-device exclusive lease;
- park/resume state preservation;
- agent/human control-mode state machine;
- agent actions blocked while human takeover is active;
- explicit authorization for privileged install action;
- deterministic observation sequence with screenshot reference + numbered elements;
- unit tests proving lifecycle and safety behavior.

### P1 — next

- real authorized Android adapter over ADB/UIAutomator-compatible primitives;
- screenshot and accessibility-tree observation capture;
- browser/WebRTC or scrcpy-style human live view;
- evidence receipts for every action/observation transition;
- cancellation/timeouts and restart reconciliation;
- MCP facade exposing only governed runtime operations;
- REST/SDK client with idempotent session/action identifiers.

### P2 — after real-device evidence

- hosted Android worker pool;
- persistent disk/device snapshots;
- scheduling and fleet concurrency;
- region/network profiles;
- iOS adapter;
- metering/billing;
- production browser takeover certification.

### Explicitly out of scope for the current slice

- claiming a real hosted Android cloud;
- claiming ADB/physical-device/emulator support;
- bypassing CAPTCHA, MFA, integrity checks or app security controls;
- unattended payments/destructive consent;
- anti-detection or account-farm behavior;
- copying Phonebox branding, UI, proprietary implementation or private APIs.

## 9. Behavior contracts / acceptance tests

1. **Exclusive lease:** a second agent cannot acquire a device already leased by another owner.
2. **Release/reacquire:** once a session is parked/stopped, another owner can lease the device.
3. **Persistence:** app/device state survives park -> resume.
4. **Human takeover:** takeover switches control mode to human and device state to `human_control`.
5. **Fail closed:** observe/act calls from the agent fail while human control is active.
6. **Return control:** ending takeover restores agent control without resetting device state.
7. **Deterministic observations:** fake adapter observation IDs and sequence numbers are stable and monotonic.
8. **Privileged authorization:** install actions fail unless explicit authorization is present.
9. **Truthful capability:** fake adapter must not be represented as ADB, emulator, physical-device or hosted-cloud support.

## 10. Implementation started

This branch now contains the Phase A implementation:

- `apps/api/app/mobile/contracts.py`
- `apps/api/app/mobile/runtime.py`
- `apps/api/tests/test_mobile_runtime.py`

The current slice is deliberately provider-neutral and testable. A real Android adapter must come only after these contracts pass CI and after an authorized test-device boundary is defined.

## 11. Next implementation slice

Build `AndroidAdbAdapter` behind the same contracts with:

- device discovery and explicit allow-list;
- screenshot capture;
- compact UI hierarchy extraction;
- tap/type/swipe/app-launch actions;
- per-action timeout;
- lease enforcement;
- redacted evidence receipts;
- no unrestricted shell exposure;
- no automatic privilege escalation;
- integration tests against an emulator or explicitly authorized physical device.

Do not advance the tracker to implementation-certified until exact-head CI is green and the real adapter is independently exercised.

## 12. Public evidence links

- Phonebox launch: https://www.reddit.com/r/SideProject/comments/1wudnby/i_built_an_android_phone_in_the_cloud_that_ai/
- Phonebox MCP launch: https://www.reddit.com/r/mcp/comments/1wudjab/phonebox_give_your_agent_an_android_phone_through/
- PhoneBase: https://phonebase.cloud/
- PhoneBase docs: https://docs.phonebase.cloud/en/
- Mobilerun: https://mobilerun.ai/
- Mobilerun source: https://github.com/droidrun/mobilerun
- AWS Device Farm pricing: https://aws.amazon.com/device-farm/pricing/
- AWS Device Farm remote access: https://docs.aws.amazon.com/devicefarm/latest/developerguide/remote-access.html
