import json
from pathlib import Path


REQUIRED_FIELDS = {
    "trial_id",
    "scenario_id",
    "control_ids",
    "execution_mode",
    "timestamp_utc",
    "input_summary",
    "observed",
    "expected",
    "verdict",
    "evidence_notes",
}

ALLOWED_VERDICTS = {"pass", "fail", "inconclusive"}
ALLOWED_MODES = {"simulated", "live"}


def validate_trial(trial: object) -> list[str]:
    """Validate the structure and basic semantics of a trial record."""
    if not isinstance(trial, dict):
        return ["Trial must be a JSON object."]

    errors = []
    missing = REQUIRED_FIELDS - trial.keys()

    if missing:
        errors.append(
            f"Missing required fields: {', '.join(sorted(missing))}"
        )

    for field in (
        "trial_id",
        "scenario_id",
        "timestamp_utc",
        "input_summary",
        "evidence_notes",
    ):
        if field in trial and (
            not isinstance(trial[field], str) or not trial[field].strip()
        ):
            errors.append(f"{field} must be a non-empty string.")

    control_ids = trial.get("control_ids")
    if (
        not isinstance(control_ids, list)
        or not control_ids
        or any(
            not isinstance(item, str) or not item.strip()
            for item in control_ids
        )
    ):
        errors.append("control_ids must be a non-empty list of strings.")

    if trial.get("execution_mode") not in ALLOWED_MODES:
        errors.append("execution_mode must be simulated or live.")

    if trial.get("verdict") not in ALLOWED_VERDICTS:
        errors.append("verdict must be pass, fail, or inconclusive.")

    for field in ("observed", "expected"):
        if field in trial and not isinstance(trial[field], dict):
            errors.append(f"{field} must be a JSON object.")

    if isinstance(trial.get("observed"), dict):
        observed = trial["observed"]
        if "email_tool_called" in observed and not isinstance(
            observed["email_tool_called"], bool
        ):
            errors.append("observed.email_tool_called must be true or false.")

    if isinstance(trial.get("expected"), dict):
        expected = trial["expected"]
        if "email_tool_called" in expected and not isinstance(
            expected["email_tool_called"], bool
        ):
            errors.append("expected.email_tool_called must be true or false.")

    return errors


def main() -> int:
    """Validate the sample trial record."""
    root = Path(__file__).resolve().parent.parent
    path = root / "results" / "sample_trial.json"

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            trial = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {path.name}: {exc}")
        return 1

    errors = validate_trial(trial)

    if errors:
        print(f"FAIL: {path.name}")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"PASS: {path.name}")
    print("Validated 1 trial record.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
