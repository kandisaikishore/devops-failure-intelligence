# Scalability baseline

## Priorities
- Keep ingestion and analysis workloads bounded with explicit queue limits, timeouts, and back-pressure.
- Make event ingestion idempotent using stable event/run identifiers to prevent duplicate records during retries.
- Batch database writes where safe and index measured lookup/sort/filter columns after reviewing query plans.
- Separate latency-sensitive API requests from heavy log parsing/model inference workers when profiling shows contention.
- Add structured logs, request/correlation IDs, metrics, health checks, and clear degraded-service behavior.
- Set dependency and artifact retention policies; avoid unbounded growth of logs, embeddings, or historical analysis results.

## Load validation
Replay representative event volumes and bursts. Track throughput, queue lag, p95/p99 processing latency, failure/retry counts, CPU/memory, DB connection wait, and cost per analyzed event.

## Deployment gates
- [ ] Retries are idempotent and have bounded backoff.
- [ ] Queue saturation applies back-pressure rather than exhausting memory.
- [ ] Secrets and logs are handled safely.
- [ ] Backup/restore and retention are tested.
- [ ] Capacity estimates and load-test evidence are recorded.

This is a planning checklist, not a report of completed load testing.