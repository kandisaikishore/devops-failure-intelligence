# MVP architecture

## Request flow

    Browser dashboard
          |
          | POST /api/analyze (sanitized log text)
          v
    FastAPI validation (Pydantic; max 200 KB)
          |
          v
    Rule engine (regex signatures)
          |
          +--> Findings: cause, severity, recommendation, matched evidence
          |
          +--> No match: status=unclassified (no fabricated diagnosis)
          v
    JSON response rendered by dashboard

    GET /health --> deployment health check
    GET /api/rules --> supported detection rules

## Current scope
- Single-process FastAPI application
- Rule signatures for dependency resolution, tests, compilation, timeout/network, configuration, and resource exhaustion
- Evidence-linked recommendations
- Browser UI and JSON API
- Automated tests and GitHub Actions CI
- Render Blueprint for deployment

## Deliberate limitations
- No persistent incident database yet
- No automatic GitHub Actions log ingestion yet
- No LLM calls or AI-generated root-cause claims yet
- No authentication; do not expose publicly to sensitive log data
- No automatic remediation or production changes

## Next milestones
1. Validate log categories and workflow with real users.
2. Add GitHub App/webhook ingestion with least-privilege permissions and signature verification.
3. Add optional PostgreSQL incident history and retention controls.
4. Add opt-in LLM summaries grounded in matched log evidence, with secret redaction and evaluation tests.
5. Add authentication, rate limiting, audit events, and operational monitoring before handling customer logs.
