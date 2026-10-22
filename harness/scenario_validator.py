from pathlib import Path

import yaml


REQUIRED_FIELDS = {
    "id",
    "title",
    "control_ids",
    "threat_category",
    "severity",
    "split",
    "description",
    "input",
    "expected_behavior",
    "success_criteria",
    "checks",
}

ALLOWED_SEVERITIES = {"critical", "high", "medium", "low"}
ALLOWED_SPLITS = {"seen", "held_out"}


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_scenario(
    scenario: object,
    known_control_ids: set[str],
    expected_split: str | None = None,
) -> list[str]:
    """Validate one scenario and its links to security controls."""
    if not isinstance(scenario, dict):
        return ["Scenario must be a YAML mapping."]

    errors = []
    missing = REQUIRED_FIELDS - scenario.keys()

    if missing:
        errors.append(
            f"Missing required fields: {', '.join(sorted(missing))}"
        )

    scenario_id = scenario.get("id")
    if (
        not isinstance(scenario_id, str)
        or len(scenario_id) != 6
        or not scenario_id.startswith("SC-")
        or not scenario_id[3:].isdigit()
    ):
        errors.append("id must use a format such as SC-001.")

    for field in ("title", "threat_category", "description"):
        if field in scenario and not non_empty_string(scenario[field]):
            errors.append(f"{field} must be a non-empty string.")

    severity = scenario.get("severity")
    if severity not in ALLOWED_SEVERITIES:
        errors.append("severity must be critical, high, medium, or low.")

    split = scenario.get("split")
    if split not in ALLOWED_SPLITS:
        errors.append("split must be seen or held_out.")
    elif expected_split is not None and split != expected_split:
        errors.append(
            f"split must be {expected_split} for this directory."
        )

    control_ids = scenario.get("control_ids")
    if (
        not isinstance(control_ids, list)
        or not control_ids
        or any(not non_empty_string(item) for item in control_ids)
    ):
        errors.append("control_ids must be a non-empty list of strings.")
    else:
        for control_id in control_ids:
            if control_id not in known_control_ids:
                errors.append(f"Unknown control ID: {control_id}.")

    scenario_input = scenario.get("input")
    if not isinstance(scenario_input, dict) or not scenario_input:
        errors.append("input must be a non-empty mapping.")

    for field in ("expected_behavior", "success_criteria"):
        value = scenario.get(field)
        if (
            not isinstance(value, list)
            or not value
            or any(not non_empty_string(item) for item in value)
        ):
            errors.append(f"{field} must be a non-empty list of strings.")
    # Validate expected outcome checks.
    checks = scenario.get("checks")
    if not isinstance(checks, dict) or not checks:
        errors.append("checks must be a non-empty mapping.")
    else:
        for field, value in checks.items():
            if not isinstance(field, str) or not field.strip():
                errors.append("Check names must be non-empty strings.")
            if not isinstance(value, bool):
                errors.append(f"Check {field!r} must have a boolean value.")

    return errors


def validate_scenario_file(
    path: Path,
    known_control_ids: set[str],
    expected_split: str | None = None,
) -> list[str]:
    """Load and validate a scenario YAML file."""
    try:
        with path.open("r", encoding="utf-8-sig") as file:
            scenario = yaml.safe_load(file)
    except (OSError, yaml.YAMLError) as exc:
        return [f"Could not read valid YAML: {exc}"]

    errors = validate_scenario(
        scenario,
        known_control_ids,
        expected_split=expected_split,
    )

    if isinstance(scenario, dict):
        scenario_id = scenario.get("id")
        if isinstance(scenario_id, str) and path.stem != scenario_id:
            errors.append(
                f"Filename must match scenario ID: expected {scenario_id}.yaml."
            )

    return errors


def main() -> int:
    """Validate scenario files and their referenced controls."""
    root = Path(__file__).resolve().parent.parent
    controls_dir = root / "controls"

    known_control_ids = set()
    for path in controls_dir.glob("*.yaml"):
        try:
            with path.open("r", encoding="utf-8-sig") as file:
                control = yaml.safe_load(file)
            if isinstance(control, dict) and isinstance(control.get("id"), str):
                known_control_ids.add(control["id"])
        except (OSError, yaml.YAMLError):
            continue

    scenario_files = []
    for split in ("seen", "held_out"):
        directory = root / "scenarios" / split
        for path in sorted(directory.glob("*.yaml")):
            scenario_files.append((path, split))

    if not scenario_files:
        print("ERROR: No scenario YAML files found.")
        return 1

    has_errors = False
    passed = 0

    for path, expected_split in scenario_files:
        errors = validate_scenario_file(
            path,
            known_control_ids,
            expected_split=expected_split,
        )

        if errors:
            has_errors = True
            print(f"FAIL: {path.relative_to(root)}")
            for error in errors:
                print(f"  - {error}")
        else:
            passed += 1
            print(f"PASS: {path.relative_to(root)}")

    if has_errors:
        print("\nScenario validation failed.")
        return 1

    print(f"\nValidated {passed} scenario(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
