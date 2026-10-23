# AgentAssure

**An experimental security assurance framework for AI agents.**

AgentAssure is a research and portfolio project exploring how to connect AI-agent security requirements to reproducible tests, structured evidence, measurable risk, and actionable remediation.

The project uses a fictional cross-border freight brokerage assistant as its target environment. The intended system may interact with email, shipment files, and third-party rate tools. All initial testing is designed for controlled, non-production environments.

## Project status

**Early development — evaluation framework prototype.**

Implemented so far:

- YAML security-control definitions and validation.
- Structured security-scenario definitions with control references.
- Trial-record validation.
- Deterministic mock trial execution.
- Expected-versus-observed check evaluation.
- JSON evidence records with verdicts and mismatch details.
- Automated unit tests for validation and evaluation behavior.

The current runner uses deterministic simulated behavior. It does **not** yet test a live AI model, establish real-world attack success rates, or demonstrate the effectiveness of production defenses.

## Project evidence

### Automated test suite

![AgentAssure automated test suite](docs/assets/01-test-suite-passing.png)

### Security control mapped to a test scenario

![Control-to-scenario mapping](docs/assets/02-control-scenario-mapping.png)

### Detecting a simulated security violation

![AgentAssure simulated failure detection](docs/assets/04-security-violation-detected.png)

The failure-detection example deliberately injects unexpected observations to verify that the evaluator reports failed checks. It is a test of the evaluation logic, not a live AI attack.

## Initial security controls

| ID | Control | Severity |
|---|---|---|
| AC-001 | Explicit authorization before sending email | High |
| AC-002 | Least-privilege tool access | High |
| AC-003 | Untrusted content isolation | Critical |
| AC-004 | Security decision logging | Medium |

These controls define requirements to evaluate. Their presence in the repository does not mean an AI agent already enforces them.

## Quick start

Requires Python 3.13.

Create and activate a virtual environment, then install the dependencies:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the control validator, automated tests, and deterministic mock trials:

```powershell
python harness\control_validator.py
python -m pytest -v
python -m harness.run_trial
```

The mock runner writes structured JSON trial records to `results/raw/`. These generated records are local artifacts and are excluded from version control by the current Git configuration.

## Planned capabilities

1. Expand the security-control and attack-scenario libraries.
2. Strengthen evaluation correctness, evidence validation, and reproducibility.
3. Introduce a sandboxed agent interface for testing tool-use behavior.
4. Evaluate multiple model configurations using repeated trials.
5. Report uncertainty and compare baseline behavior against defenses.
6. Evaluate held-out attacks after defense configurations are frozen.
7. Generate a risk register and evidence-linked remediation reports.
8. Add continuous integration and a documentation site.

## Research and governance alignment

The project intends to map relevant controls and findings to selected guidance from OWASP Top 10 for LLM Applications, MITRE ATLAS, the NIST AI Risk Management Framework, and ISO/IEC 42001.

Mappings will be documented as analytical references. They are not claims of certification, independent audit, or regulatory compliance.

## Scope and limitations

AgentAssure is an experimental research and portfolio project using a fictional organization and controlled test scenarios.

Results from future evaluations will depend on the model, model configuration, agent implementation, tools, defenses, scenario selection, and evaluation procedure. Simulated results must remain distinguishable from live model measurements.

A passing test suite demonstrates that the tested software checks behave as expected under those tests. It does not establish that an AI agent is secure. Likewise, observing no failures in a finite number of trials does not prove that an attack is impossible or that residual risk is zero.

## License

See [LICENSE](LICENSE).
