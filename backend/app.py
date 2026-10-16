"""DFIP MVP: evidence-linked CI/CD log diagnosis."""
import re
from typing import Any
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="DevOps Failure Intelligence Platform", version="0.1.0",
              description="Analyze CI/CD logs and return evidence-linked diagnostic suggestions.")

RULES: list[dict[str, Any]] = [
 {"id":"dependency-resolution","title":"Dependency resolution failure","severity":"high",
  "patterns":[r"could not resolve dependencies",r"dependency resolution failed",r"could not find artifact",r"npm err!.*(eresolve|notarget)",r"no matching distribution found",r"package .* not found"],
  "cause":"A required package or dependency version cannot be resolved from the configured registry.",
  "fix":"Verify package coordinates and version constraints, registry access, lockfiles, and repository credentials. Re-run installation after correcting the mismatch."},
 {"id":"test-failure","title":"Automated test failure","severity":"high",
  "patterns":[r"tests? failed",r"failures:",r"assertionerror",r"assertion failed",r"there are test failures",r"error: test"],
  "cause":"One or more automated tests failed or an assertion did not match the actual result.",
  "fix":"Inspect the first failing test and stack trace. Reproduce locally, determine whether the defect is in code, test data, or environment, then add a regression test."},
 {"id":"build-compilation","title":"Build or compilation error","severity":"high",
  "patterns":[r"compilation failed",r"compilation error",r"cannot find symbol",r"syntaxerror",r"build failed",r"error:.*cannot be applied"],
  "cause":"The source code or build configuration could not be compiled successfully.",
  "fix":"Start with the earliest compiler error, verify language/runtime versions and imports, and rerun the build before investigating downstream errors."},
 {"id":"timeout","title":"Timeout or unavailable service","severity":"medium",
  "patterns":[r"timed out",r"timeout",r"connection refused",r"connection reset",r"could not connect",r"temporary failure in name resolution"],
  "cause":"A network call or dependent service did not respond in time or was unreachable.",
  "fix":"Check service health, DNS/network rules, endpoint configuration, and timeout budgets. Use bounded retries with backoff only for safe, idempotent operations."},
 {"id":"configuration","title":"Missing configuration or secret","severity":"high",
  "patterns":[r"missing environment variable",r"environment variable .* not set",r"secret .* not found",r"configuration .* missing",r"no such file or directory"],
  "cause":"A required environment variable, secret, configuration entry, or file may be unavailable in the CI/deployment environment.",
  "fix":"Compare required configuration with the deployment environment and confirm secret names and paths. Provide missing values through a secret manager; never print secret values into logs."},
 {"id":"resource-exhaustion","title":"Resource exhaustion","severity":"high",
  "patterns":[r"out of memory",r"oomkilled",r"memoryerror",r"no space left on device",r"disk quota exceeded"],
  "cause":"The process or runner may have exhausted memory, disk, or another constrained resource.",
  "fix":"Inspect runner/container resource limits and memory or disk usage. Reduce unnecessary artifacts or parallelism, and increase limits only after confirming the bottleneck."},
]

SECRET_PATTERNS = [
    # Redact common credential assignments before matched log lines are returned.
    (re.compile(r"(?i)\b(authorization\s*[:=]\s*bearer)\s+[A-Za-z0-9._~+/=-]+"), r"\1 [REDACTED]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_ACCESS_KEY]"),
    (re.compile(r'(?i)\b([A-Z0-9_.-]*(?:password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|private[_-]?key|auth[_-]?token|token)[A-Z0-9_.-]*)(\s*[:=]\s*)("[^"]*"|\'[^\']*\'|[^\s,;]+)'), r"\1\2[REDACTED]"),
]

def redact_line(line: str) -> str:
    """Mask common secrets before exposing matched log evidence to the caller."""
    redacted = line[:500]
    for pattern, replacement in SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


class AnalyzeRequest(BaseModel):
    logs: str = Field(min_length=1, max_length=200_000, description="Sanitized CI/CD log text")
    service: str = Field(default="unknown-service", max_length=120)

class Finding(BaseModel):
    rule_id: str
    title: str
    severity: str
    cause: str
    recommendation: str
    evidence: list[str]

class AnalyzeResponse(BaseModel):
    service: str
    status: str
    findings: list[Finding]
    summary: str
    disclaimer: str = "Rule-based suggestions are advisory. Validate evidence before changing production systems."

@app.get("/health")
def health():
    return {"status":"ok","service":"dfip-api","version":"0.1.0"}

@app.get("/api/rules")
def list_rules():
    return {"rules":[{"id":r["id"],"title":r["title"],"severity":r["severity"]} for r in RULES]}

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    lines = [line.strip()[:500] for line in request.logs.splitlines() if line.strip()]
    findings = []
    for rule in RULES:
        matches = [line for line in lines if any(re.search(p, line, re.IGNORECASE) for p in rule["patterns"])]
        if matches:
            findings.append(Finding(rule_id=rule["id"], title=rule["title"], severity=rule["severity"],
                cause=rule["cause"], recommendation=rule["fix"], evidence=[redact_line(line) for line in matches[:3]]))
    status = "findings" if findings else "unclassified"
    summary = (f"Detected {len(findings)} likely failure pattern(s). Review the evidence and validate next steps."
               if findings else "No known failure pattern matched. Review the sanitized log and add a rule if this recurs.")
    return AnalyzeResponse(service=request.service.strip() or "unknown-service", status=status, findings=findings, summary=summary)

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DFIP — Incident Intelligence</title><style>
:root{color-scheme:dark;--bg:#0b1020;--panel:#121a2c;--line:#27344d;--text:#e8eefb;--muted:#9eacc5;--accent:#7c9cff;--green:#63d8b2}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#182444,var(--bg) 58%);font:15px/1.5 system-ui,sans-serif;color:var(--text)}
main{max-width:1000px;margin:auto;padding:36px 20px 70px}.eyebrow{color:var(--green);font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:12px}h1{font-size:clamp(30px,5vw,48px);line-height:1.1;margin:12px 0}p{color:var(--muted)}
.grid{display:grid;grid-template-columns:1.2fr .8fr;gap:18px;margin-top:28px}.card{background:#111a2bef;border:1px solid var(--line);border-radius:16px;padding:22px}
label{display:block;font-weight:600;margin:14px 0 7px}input,textarea{width:100%;background:#0a1020;border:1px solid var(--line);border-radius:9px;padding:12px;color:var(--text);font:inherit}textarea{min-height:220px;resize:vertical}
button{margin-top:14px;background:var(--accent);border:0;border-radius:9px;padding:12px 17px;color:#081126;font-weight:800;cursor:pointer}button:disabled{opacity:.5}.pill{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:4px 9px;color:var(--green);font-size:12px}
.muted{font-size:13px;color:var(--muted)}.finding{border:1px solid var(--line);border-radius:12px;padding:15px;margin:12px 0}.finding h3{margin:6px 0}.finding pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#090f1c;border-radius:8px;padding:10px;color:#c5d3f2;font-size:12px}
.empty{border:1px dashed var(--line);padding:20px;border-radius:12px;color:var(--muted)}footer{margin-top:22px;color:var(--muted);font-size:12px}@media(max-width:720px){.grid{grid-template-columns:1fr}main{padding:25px 14px}}
</style></head><body><main><div class="eyebrow">DFIP · Developer tools</div><h1>Turn failed builds into a clear next step.</h1>
<p>Paste sanitized CI/CD logs. DFIP matches common failure signatures, cites matching lines, and suggests a practical investigation path.</p>
<div class="grid"><section class="card"><h2>Analyze a failure</h2><form id="form"><label for="service">Service or repository</label><input id="service" maxlength="120" value="sample-api">
<label for="logs">Build or deployment logs</label><textarea id="logs" maxlength="200000" required>[ERROR] Could not resolve dependencies for project sample-api
[ERROR] Dependency resolution failed: package version not found</textarea>
<p class="muted">Remove tokens, passwords, personal data, and private URLs before submitting. This MVP processes logs in memory and does not persist them.</p><button id="submit" type="submit">Analyze logs →</button></form></section>
<aside class="card"><span class="pill">MVP · Rule-based</span><h2>What you get</h2><p><strong>Evidence first</strong><br>Matched log lines explain why a rule triggered.</p><p><strong>Actionable suggestions</strong><br>Recommendations point to a concrete next step.</p><p><strong>Honest uncertainty</strong><br>Unknown patterns are reported as unclassified.</p><p class="muted">AI summaries, GitHub Actions ingestion, incident history, and alerts are future milestones—not enabled in this MVP.</p></aside></div>
<section id="results" aria-live="polite"><div class="empty">Run an analysis to see findings here.</div></section><footer>DFIP is an advisory tool. Review changes and follow your team's production change process.</footer></main>
<script>
var form=document.querySelector('#form'),button=document.querySelector('#submit'),results=document.querySelector('#results');
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
form.addEventListener('submit',async function(e){e.preventDefault();button.disabled=true;button.textContent='Analyzing…';results.innerHTML='<div class="empty">Analyzing sanitized logs…</div>';
try{var response=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({service:document.querySelector('#service').value,logs:document.querySelector('#logs').value})});var data=await response.json();if(!response.ok)throw new Error((data.detail&&data.detail[0]&&data.detail[0].msg)||'Request failed');
var html='<div class="card"><span class="pill">'+esc(data.status)+'</span><h2>Analysis result</h2><p>'+esc(data.summary)+'</p>';
if(!data.findings.length)html+='<div class="empty">No rule matched. Review the full sanitized log and extend the rules for recurring failures.</div>';
data.findings.forEach(function(f){html+='<article class="finding"><span class="pill">'+esc(f.severity)+' · '+esc(f.rule_id)+'</span><h3>'+esc(f.title)+'</h3><p><strong>Likely cause:</strong> '+esc(f.cause)+'</p><p><strong>Recommended next step:</strong> '+esc(f.recommendation)+'</p><p><strong>Evidence:</strong></p>'+f.evidence.map(function(x){return '<pre>'+esc(x)+'</pre>'}).join('')+'</article>'});
html+='<p class="muted">'+esc(data.disclaimer)+'</p></div>';results.innerHTML=html;
}catch(err){results.innerHTML='<div class="empty">Could not analyze logs: '+esc(err.message)+'</div>'}finally{button.disabled=false;button.textContent='Analyze logs →'}});
</script></body></html>"""
