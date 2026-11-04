# Staged Testing

A layered approach to validating software where different types of tests run at different points in the development and deployment lifecycle. Each stage catches a different class of problem, runs at a different speed, and requires a different environment.

Running all tests as one undifferentiated batch would be slow, expensive, and noisy. Staging them means fast feedback for developers, thorough validation before release, and no production surprises.

---

## The Testing Pyramid

```
                         [UAT]
                    ─────────────
                  [E2E / System Tests]
             ──────────────────────────
           [Integration Tests]
      ──────────────────────────────────
    [Unit Tests — fastest, most numerous]
```

The pyramid shape reflects the economics: unit tests are cheap, fast, and run constantly. Tests at the top are expensive, slow, and run infrequently. Inverting the pyramid (more E2E than unit) is a common anti-pattern — the test suite becomes slow and fragile.

---

## The Stages

### Stage 1 — Unit Tests

**What:** Test one function, class, or module in complete isolation. External dependencies are replaced with mocks or stubs.

**Who runs it:** Developer, on every save or commit.

**Speed:** Milliseconds per test. Thousands run in seconds.

**What they catch:** Logic errors in a single component. Off-by-one errors, wrong conditions, missing edge cases.

**What they miss:** How components interact. Real database behavior. Network failures.

```python
# Unit test: the chunker function in isolation
def test_chunker_respects_max_tokens():
    text = "word " * 1000
    chunks = chunk_text(text, max_tokens=100)
    assert all(count_tokens(c) <= 100 for c in chunks)
    # No database, no LLM, no network — pure function
```

---

### Stage 2 — Integration Tests

**What:** Test that two or more components work together correctly. May use real databases, real [message queues](../../distributed-systems/messaging/queues.md), or real external services (or close approximations).

**Who runs it:** Developer locally + CI on every push.

**Speed:** Seconds to minutes.

**What they catch:** Mismatches between components — wrong API contracts, [ORM](../data/orm.md) queries that work differently against a real database than a mock, message format mismatches.

**What they miss:** Full system behavior under realistic load. UI correctness. Business-level requirements.

```python
# Integration test: the RAG pipeline retrieval + prompt construction
def test_rag_retrieval_returns_relevant_chunk(real_pgvector_db):
    # Uses a real database, not a mock
    pipeline = RAGPipeline(db=real_pgvector_db)
    result = pipeline.retrieve("capital expenditure approval threshold")
    assert any("SAR 250,000" in chunk.text for chunk in result.chunks)
```

The critical distinction from unit tests: a mock database may behave differently from a real one (NULL handling, index usage, transaction isolation). Integration tests catch the gap.

---

### Stage 3 — End-to-End (E2E) / System Tests

**What:** Test a complete user journey through the fully assembled system, from the user's entry point to the final output. Uses the actual UI or API as a real user would.

**Who runs it:** CI on merge to main, or before release.

**Speed:** Minutes to tens of minutes.

**What they catch:** Broken user flows, routing errors, auth failures, UI rendering problems, cross-service data corruption.

**What they miss:** Load behavior. Business requirement interpretation. Real-user edge cases.

```python
# E2E test: submit a query through the full RAG API
def test_query_returns_grounded_answer(test_client, seeded_knowledge_base):
    response = test_client.post("/api/query", json={
        "question": "What is the leave policy for annual leave?",
        "tenant_id": "acme-corp",
    })
    assert response.status_code == 200
    assert response.json()["answer"] != ""
    assert len(response.json()["sources"]) > 0
```

---

### Stage 4 — Load / Performance Tests

**What:** Send realistic production-level traffic volume through the system and measure latency, throughput, error rate, and resource consumption under load.

**Who runs it:** Before major releases, or on a scheduled cadence.

**Speed:** Minutes to hours (depending on the scenario duration).

**What they catch:** Bottlenecks that only appear under concurrent load, N+1 query problems at scale, memory leaks that grow over time, thread pool exhaustion, database connection limits.

**What they miss:** Functional correctness. Business logic. UI behavior.

```python
# Load test with Locust (Python)
class RAGUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def query(self):
        self.client.post("/api/query", json={
            "question": random.choice(test_questions),
            "tenant_id": "load-test-tenant",
        })

# Run with: locust -f locustfile.py --users 100 --spawn-rate 10
# Watch: P95 latency, error rate, throughput (req/s)
```

For [LLM](../../ai/generation/llm.md) systems, load testing also reveals GPU saturation and TTFT degradation under concurrent requests — metrics that don't appear with single-request testing.

---

### Stage 5 — UAT (User Acceptance Testing)

**What:** Real business users validate the system against real-world scenarios. Not automated — manual, scenario-driven, and sign-off gated.

**Who runs it:** Business stakeholders, end users, or clients.

**Speed:** Days to a week.

**What they catch:** Requirements mismatches — the system does what the spec says but not what the business actually needs. Edge cases only domain experts would know to test.

**What they miss:** Technical bugs (those were caught earlier). Performance issues at scale.

See [UAT](uat.md) for the full process.

---

## Stage Comparison

| Stage | Speed | Who | Environment | What it catches |
|---|---|---|---|---|
| Unit | ms | Developer | Local, isolated | Logic errors |
| Integration | seconds | Developer / CI | Local with real deps | Component mismatches |
| E2E | minutes | CI | Full system, test env | Broken user flows |
| Load | minutes–hours | CI / release gate | Prod-like scale | Performance bottlenecks |
| [UAT](uat.md) | days | Business users | [UAT](uat.md) environment | Requirements mismatches |

---

## When Each Stage Runs

```
Code change committed
        ↓
Unit tests      ← runs immediately (seconds)
        ↓
Integration tests ← runs on push to CI (minutes)
        ↓
E2E tests       ← runs on merge to main (minutes)
        ↓
Load tests      ← runs before release (hours)
        ↓
UAT             ← runs before go-live (days)
        ↓
Staged rollout  ← canary → production
```

Each stage is a gate. A failure blocks promotion to the next stage.

---

## Staged Testing for AI / RAG Systems

Standard test stages apply, but AI systems add a parallel evaluation track:

```
Unit tests         → test individual functions (chunker, token counter, prompt builder)
Integration tests  → test retrieval pipeline against real vector DB
E2E tests          → test full query → retrieve → generate → respond flow
Load tests         → measure TTFT, token throughput under concurrent users
UAT               → domain experts validate answer quality and citation accuracy

Evaluation track (parallel):
  Fixed evaluation dataset  → run on every prompt or model change
  Groundedness check        → automated per-response metric
  Relevance check           → automated per-response metric
  Abstention rate           → monitored in production
```

The evaluation track doesn't replace the standard test stages — it runs alongside them, measuring quality dimensions that functional tests can't capture.

---

## Common Anti-Patterns

**Ice cream cone** (inverted pyramid) — more E2E and [UAT](uat.md) than unit tests. The suite runs slowly, breaks constantly, and gives little signal about what failed.

**Mock everything** — unit tests mock external dependencies so thoroughly that the integration test stage reveals all the real bugs anyway. Mocks should be minimal and realistic.

**Skip load testing** — system passes all functional tests, deploys to production, and degrades immediately under real traffic. Load testing is skipped most often and costs the most when absent.

**[UAT](uat.md) as bug discovery** — [UAT](uat.md) should confirm the system works, not discover basic functional bugs. If [UAT](uat.md) is catching things unit/integration/E2E tests should have caught, the earlier stages are under-invested.

---

## Related

- [UAT](uat.md) — the final testing stage in detail
- [Fixed Evaluation Dataset](../../ai/evaluation/fixed-evaluation-dataset.md) — the AI-specific quality track that runs alongside staged testing
- [Staged Rollout](staged-rollout.md) — what happens after all testing stages pass: controlled release to production
- [Throughput and Latency](../architecture/throughput-and-latency.md) — P95/P99 metrics that load testing measures
