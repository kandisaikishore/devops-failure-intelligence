# Research sources and product rationale

The product direction is informed by the research summary. Third-party market figures are directional context, not proof of customer demand or a revenue forecast.

- OpenTelemetry Java documentation: https://opentelemetry.io/docs/languages/java/ — standard telemetry concepts for metrics, logs, and traces.
- OpenTelemetry Java instrumentation ecosystem: https://opentelemetry.io/docs/languages/java/instrumentation/ — instrumentation approaches and signal correlation.
- Mordor Intelligence observability market overview: https://www.mordorintelligence.com/industry-reports/observability-market — market-size estimate referenced in the research report.

## Product decision
Start with a small, testable DevOps incident diagnosis workflow rather than attempting to recreate a complete enterprise observability stack. Validate the log-analysis pain point first; expand into telemetry ingestion, persistent incident tracking, and LLM-assisted summaries only after pilot feedback.
