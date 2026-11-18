# Agentic Data Pipeline

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/badge/tests-135_passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

An AI agent that finds and fixes problems in data pipelines, safely.

When incoming data changes (for example, `amount` arrives as text `"49.99"`
instead of the number `49.99`), the agent spots it, works out the cause,
suggests a fix, tests the fix on a copy of the data, and only then rolls it
out. If anything goes wrong, it rolls back automatically.

**It never changes real data without checking first.**

## How it works

1. **Detect** – compare the data with the expected schema and run quality checks.
2. **Diagnose** – find the cause and which downstream tables are affected.
3. **Propose** – suggest a simple, predefined fix (e.g. `cast_type(amount, DOUBLE)`).
4. **Validate** – run the fix on a shadow copy and check rows, nulls and totals.
5. **Approve** – a policy engine decides if the fix is safe enough to apply.
6. **Deploy** – release to 5% of the data first (canary).
7. **Monitor & roll back** – if health checks fail, restore the previous version.

If a step fails or a limit is hit, the agent stops without changing anything.

## Safety

- The agent can only use a fixed set of fix operations, never raw SQL or shell commands.
- Low-risk fixes go ahead automatically. Medium-risk fixes need approval. High-risk fixes (like deleting rows) are rejected.
- Every fix is tested on a shadow copy before release.
- Every change is versioned, so rollback is always possible.
- Instructions hidden inside the data are treated as data, not commands.

## Quick start

Requires Python 3.12+.

```bash
git clone https://github.com/Indra-2004/agentic-data-pipeline.git
cd agentic-data-pipeline
pip install -e ".[dev]"

pytest                                          # run tests
python -m app.evaluation.runner --scenarios all # run evaluation
uvicorn app.api.app:app --port 8000             # start the API
```

Or with Docker:

```bash
docker compose up --build
```

API docs: http://localhost:8000/docs

## API

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/pipelines` | List pipelines |
| POST | `/pipelines/{id}/triage` | Run the agent on a pipeline |
| GET | `/runs/{run_id}` | View a past run |

## Results

The agent is tested on 15 scenarios: 10 common data problems and 5 attack or
failure cases.

| Metric | Result |
|---|---|
| Scenarios handled correctly | **15 / 15** |
| Data lost | **0%** |
| Wrong fixes applied | **0%** |
| Unnecessary changes | **0%** |
| Cost (offline mode) | $0 |

Many scenarios are meant to end with *no change*. In those cases, the right
move is to report the problem, not to fix it.

## Configuration

Settings come from environment variables (see `.env.example`). The main ones:

| Variable | Default | Meaning |
|---|---|---|
| `SHP_LLM_PROVIDER` | `deterministic` | `deterministic` (offline) or `openai` |
| `OPENAI_API_KEY` | – | Needed only for `openai` |
| `SHP_APPROVAL_MODE` | `auto` | `auto`, `manual` or `human_in_loop` |
| `SHP_STORAGE_BACKEND` | `sqlite` | `sqlite` or `memory` |

## Project structure

```text
app/
  agent/          agent loop, policies, diagnosis, LLM providers
  api/            FastAPI app
  data/           profiling, quality checks, anomaly detection, lineage
  evaluation/     test scenarios and reports
  pipeline/       pipeline stages and runner
  rollback/       version restore
  storage/        SQLite and in-memory storage
  tools/          tools the agent is allowed to use
  validation/     shadow validation
datasets/         sample data
pipelines/        pipeline definitions
tests/            unit, integration, agent, safety and evaluation tests
```

## Tech stack

Python · Polars · Pydantic · SQLAlchemy/SQLite · FastAPI · OpenAI (optional) · pytest · Docker

## Author

[Indra-2004](https://github.com/Indra-2004) · [Portfolio](https://indra-2004.github.io/jobportfolio/)

## License

MIT
