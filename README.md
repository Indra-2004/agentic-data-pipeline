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

