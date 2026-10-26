# Development, Evaluation, and Security Guide

DFIP analyzes CI/CD or deployment failure evidence and provides diagnostic guidance. Remediation decisions should remain under human control unless a specific, reviewed automation is explicitly implemented.

## Confirm current integrations

Inspect the source, configuration, and package manifests to identify supported log formats, CI providers, data stores, and model integrations. Do not claim automatic ingestion or autonomous remediation unless the current branch implements and tests it.

## Evaluation dataset

Use synthetic or sanitized log fixtures. For each fixture, record:
- Expected failure category
- Relevant evidence lines or patterns
- Expected confidence/uncertainty behavior
- Safe next diagnostic steps
- Cases that should be classified as unknown or ambiguous

Keep a regression set for common failures and ensure that adding a new classifier does not silently degrade existing cases.

## Log privacy

- Redact tokens, passwords, authorization headers, connection strings, and other sensitive values before persistence or display.
- Do not include complete raw logs in exception messages by default.
- Preserve enough surrounding evidence for troubleshooting.
- Test redaction with fake credentials and verify that logs and API responses do not expose them.

## Reliability and failure handling

Test empty logs, malformed input, truncated logs, oversized input, unknown failure signatures, timeouts, and unavailable downstream services. Return an explicit unknown/partial result rather than inventing a diagnosis when evidence is insufficient.

## Human review

Recommendations should cite the evidence supporting them and distinguish observed facts from hypotheses. Do not execute destructive remediation automatically based only on a classifier result.

## Pull-request checklist

- [ ] Add sanitized fixtures and regression tests.
- [ ] Run the declared unit/integration checks.
- [ ] Verify redaction and safe error handling.
- [ ] State which provider integrations were mocked or not tested.
- [ ] Keep the human approval boundary explicit.
