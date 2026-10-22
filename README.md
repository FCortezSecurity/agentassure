# AgentAssure

**An experimental security assurance framework for AI agents.**

AgentAssure connects security requirements to reproducible tests, measured evidence, and actionable risk findings for AI agents that use tools.

## Project status

Early development. The current version validates YAML security-control definitions and includes automated unit tests. Agent attack trials, model comparisons, and measured effectiveness results are not implemented yet.

## Initial security controls

| ID | Control | Severity |
|---|---|---|
| AC-001 | Explicit authorization before sending email | High |
| AC-002 | Least-privilege tool access | High |
| AC-003 | Untrusted content isolation | Critical |
| AC-004 | Security decision logging | Medium |

These are requirements to evaluate, not claims that an agent already enforces them.

## Quick start

Requires Python 3.13.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python harness\control_validator.py
python -m pytest -v
```

## Planned capabilities

- Versioned security-control definitions
- Reproducible agent attack scenarios
- Deterministic evaluation and confidence intervals
- Risk register and remediation guidance
- Evidence-linked technical reports
- Automated tests in continuous integration

## Scope and limitations

This is a research and portfolio project using a fictional organization. Results depend on the tested models, configurations, tools, scenarios, and evaluation procedures. Passing tests does not establish that an agent is secure or that an organization is compliant with a standard.

Framework mappings are intended to support analysis, not to claim certification, audit completion, or regulatory compliance.
