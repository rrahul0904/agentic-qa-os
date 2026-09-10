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

## Initial vertical slice

The first agent is `test-case-generator`. It converts a natural-language requirement into positive, negative, and boundary test cases. The deterministic engine keeps local development and CI fully functional without an API key.

## Roadmap

1. Requirement clarifier + test case generator
2. OpenAPI test generator + test-data generator
3. Playwright execution runner + recorder artifacts
4. Flaky test and failure-clustering intelligence
5. Self-healing locator engine
6. Git diff test-impact selection
7. QA knowledge graph + release-readiness agent
8. Learning lab / 100-day curriculum
