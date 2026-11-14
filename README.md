# Self-Healing Data Pipeline Agent

A production-minded autonomous agent that detects failures and schema drift in
ETL/ELT pipelines, investigates the root cause, proposes a safe transformation
fix, validates it against shadow data, executes it through a controlled rollout,
and automatically rolls back when validation or post-deployment health checks
fail.

> **Core principle:** the agent never blindly mutates production data.
> It observes → diagnoses → proposes → validates → stages → gets approval →
> executes a canary → monitors → rolls back on any health degradation.

This is not a chatbot that explains pipeline errors. It is an autonomous system
with a bounded state machine, a policy engine that gates every action, and an
evaluation framework whose headline metric — **data loss rate** — is held at
**zero** across all benchmark and adversarial scenarios.

---

## The problem it solves

A source system quietly changes a column type:

```json
{"user_id": 123, "amount": 49.99, "currency": "USD"}   // yesterday
{"user_id": 123, "amount": "49.99", "currency": "USD"} // today
```

The pipeline expects `amount: DOUBLE` and now receives `VARCHAR`. The agent:

1. **Detects** the drift deterministically (schema comparison, quality checks,
   statistical anomaly detection — no LLM needed for measurement).
2. **Diagnoses** the root cause and inspects downstream lineage to compute the
   blast radius (`amount` → `clean.orders` → `daily_revenue`).
3. **Proposes** a declarative, constrained fix: `cast_type(amount, DOUBLE)`.
4. **Shadow-validates** the candidate against the input baseline: schema,
   row preservation, null rates, business metrics (`revenue <- amount`).
5. **Asks the policy engine** — never itself — whether it may proceed
   (LOW risk auto-stages; HIGH risk is rejected without an explicit gate).
6. **Stages** a new pipeline version and runs a **95/5 canary**.
7. **Monitors** health and **rolls back** deterministically if anything degrades.

---

