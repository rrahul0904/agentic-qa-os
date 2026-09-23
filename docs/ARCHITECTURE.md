# Architecture

## Product model

Agentic QA OS treats every QA capability as a versioned agent executed through one common runtime.

```text
Web / API clients
      |
      v
FastAPI control plane
      |
      +--> Agent Registry
      +--> Execution Runtime
      +--> Evidence Layer
      +--> LLM Gateway
      |
      +--> PostgreSQL (state, runs, evidence)
      +--> Redis (queues/cache)
      +--> Connectors (future: Jira, GitHub, ADO, Playwright, OpenAPI)
```

## Agent contract

Every agent exposes metadata, accepted input, execution output, evidence, and confidence. The runtime does not allow an agent to silently invent source-backed requirements: generated test cases carry explicit evidence references.

## Current vertical slices

### Test Case Generator

`test-case-generator` converts a natural-language requirement into positive, negative, and boundary test cases. The deterministic engine keeps local development and CI fully functional without an API key.

### Temporal Test Designer

`temporal-test-designer` converts a requirement into evidence-linked temporal scenarios such as year/month boundaries, leap-day behavior, the 2038 boundary, backward clock jumps, and accelerated/frozen-time checks.

This slice is deliberately a **planner**, not a clock-manipulation runtime. It must never claim that a target process observed a simulated time until a future execution adapter returns measured coverage evidence.

The planned execution architecture is:

```text
Agentic QA control plane
      |
      v
Temporal Test Designer
      |
      v
Authorized Windows execution worker
      |
      +--> native process-time adapter
      +--> child-process propagation
      +--> Chromium / embedded-web adapter
      |
      v
Clock-channel audit + session evidence
      |
      v
Evidence Layer / release-readiness consumers
```

The Windows execution worker is not implemented in the current repository slice.

## Roadmap

1. Requirement clarifier + test case generator
2. Temporal test design + authorized Windows execution adapter
3. OpenAPI test generator + test-data generator
4. Playwright execution runner + recorder artifacts
5. Flaky test and failure-clustering intelligence
6. Self-healing locator engine
7. Git diff test-impact selection
8. QA knowledge graph + release-readiness agent
9. Learning lab / 100-day curriculum
