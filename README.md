# Agentic QA OS

An evidence-aware Agentic Quality Engineering platform inspired by the product thesis behind TestingBuddy, rebuilt as a cohesive QA operating system rather than a collection of disconnected AI forms.

## Current vertical slice

- Agent registry and execution API
- Deterministic Test Case Generator with requirement evidence links
- Next.js operator workspace
- FastAPI backend
- PostgreSQL + Redis-ready Docker Compose
- API unit tests
- GitHub Actions CI

## Quick start

```bash
docker compose up --build
```

- Web: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

## API example

```bash
curl -X POST http://localhost:8000/api/v1/agents/test-case-generator/run \
  -H 'Content-Type: application/json' \
  -d '{"requirement":"Customer must receive an email receipt after a successful payment."}'
```

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
