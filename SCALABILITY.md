# Scalability and capacity plan

- Keep ingestion/API paths fast; process expensive analysis asynchronously when the current architecture supports it.
- Bound event payload size, worker concurrency, queue depth, and provider calls.
- Use idempotency keys or stable event IDs to prevent duplicate analysis and duplicate notifications.
- Add pagination and time-window filters to incident and run-history endpoints.
- Store operational events durably; do not rely on process-local memory for recovery.
- Configure database pools and request timeouts based on deployment replica count.
- Track ingestion lag, queue age, analysis duration, p95/p99 latency, error rate, and dropped/retried events.
- Exercise replay, poison-message handling, dependency failure, and worker restart scenarios.
- Define data retention and access controls for logs and incident payloads.

## Release gates
- [ ] Retries are bounded and idempotent.
- [ ] Backpressure prevents resource exhaustion.
- [ ] Recovery/replay is tested.
- [ ] Load-test data and capacity limits are documented.

No load-test results are implied by this plan.
