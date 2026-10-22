import re
from pathlib import Path

import yaml


REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "severity",
    "description",
    "expected_behavior",
    "testable",
}

ALLOWED_SEVERITIES = {"critical", "high", "medium", "low"}
CONTROL_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*-\d{3}$")

TEXT_FIELDS = ("title", "category", "description")


def validate_control(control: object) -> list[str]:
    """Return validation errors for a single control definition."""
    if not isinstance(control, dict):
        return ["Control must be a YAML mapping."]

    errors = []

    missing = REQUIRED_FIELDS - control.keys()
    if missing:
        errors.append(
            f"Missing required fields: {', '.join(sorted(missing))}"
        )

    control_id = control.get("id")
    if not isinstance(control_id, str) or not CONTROL_ID_PATTERN.fullmatch(
        control_id
    ):
        errors.append(
            "id must use an uppercase identifier such as AC-001."
        )

    for field in TEXT_FIELDS:
        if field in control:
            value = control[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field} must be a non-empty string.")

    if "severity" in control:
        severity = control["severity"]
        if not isinstance(severity, str) or severity not in ALLOWED_SEVERITIES:
            errors.append(
                "Severity must be critical, high, medium, or low."
            )

    if "expected_behavior" in control:
        behavior = control["expected_behavior"]
        if (
            not isinstance(behavior, list)
            or not behavior
            or any(
                not isinstance(item, str) or not item.strip()
                for item in behavior
            )
        ):
            errors.append(
                "expected_behavior must be a non-empty list of non-empty strings."
            )

    if "testable" in control and not isinstance(control["testable"], bool):
        errors.append("testable must be true or false.")

    return errors


def validate_control_file(path: Path) -> list[str]:
    """Load and validate one YAML control file."""
    try:
        with path.open("r", encoding="utf-8-sig") as file:
            control = yaml.safe_load(file)
    except (OSError, yaml.YAMLError) as exc:
        return [f"Could not read valid YAML: {exc}"]

    return validate_control(control)


def main() -> int:
    """Validate all YAML controls in the repository."""
    root = Path(__file__).resolve().parent.parent
    control_files = sorted((root / "controls").glob("*.yaml"))

    if not control_files:
        print("ERROR: No control YAML files found.")
        return 1

    has_errors = False

    for path in control_files:
        errors = validate_control_file(path)

        if errors:
            has_errors = True
            print(f"FAIL: {path.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS: {path.name}")

    if has_errors:
        return 1

    print(f"\nValidated {len(control_files)} control(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
