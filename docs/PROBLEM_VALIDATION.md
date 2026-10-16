# Problem validation plan

## Hypothesis
Small engineering teams spend avoidable time diagnosing CI/CD failures because useful evidence is buried in noisy logs and existing tools can require context switching. This is a hypothesis to validate, not proof of demand.

## Initial target users
- Junior and mid-level developers maintaining build pipelines
- Small DevOps/platform teams
- Maintainers of public repositories with recurring CI failures

## Interview questions
1. Describe the last CI/CD failure you investigated.
2. How long did it take to identify the likely cause?
3. Which tools, searches, or people helped you?
4. What was missing from your existing workflow?
5. Would evidence-linked diagnosis save time? What would make you distrust it?
6. What logs or metadata would you refuse to send to a third party?
7. Would you adopt a local/self-hosted tool, a hosted service, or neither?

## Two-week validation experiment
1. Interview at least 8 developers or DevOps practitioners.
2. Collect 20 sanitized representative failure logs with permission.
3. Manually label the failure category and relevant evidence.
4. Compare the tool output against those labels.
5. Ask 5 users to try the MVP and record time-to-first-useful-action and usefulness ratings.
6. Prioritize recurring patterns where users report meaningful friction.

## Initial success criteria
- At least 5 of 8 interviewees describe a recent concrete log-diagnosis pain point.
- Measure category precision/recall and evidence relevance on labeled samples; do not report accuracy without a defined dataset.
- At least 4 of 5 pilot users complete an analysis without assistance.
- Every diagnosis includes supporting log evidence or explicitly returns unclassified.
- No secrets or full logs are persisted by the MVP.

These are proposed experiments, not external market facts. Revise thresholds based on observed behaviour.

## Privacy and safety
- Ask users to sanitize logs before submission.
- Never commit production logs, tokens, credentials, or customer data.
- Do not execute suggested commands automatically.
- Keep remediation under human control.
- Before production use, add authentication, rate limiting, audit controls, retention policy, and verified secret redaction.
