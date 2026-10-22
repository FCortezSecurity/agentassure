import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import yaml

from harness.scenario_validator import validate_scenario
from harness.trial_validator import validate_trial


def load_control_ids(root: Path) -> set[str]:
    """Load IDs from validly parsed control YAML mappings."""
    control_ids = set()

    for path in (root / "controls").glob("*.yaml"):
        try:
            with path.open("r", encoding="utf-8-sig") as file:
                control = yaml.safe_load(file)
        except (OSError, yaml.YAMLError):
            continue

        if isinstance(control, dict):
            control_id = control.get("id")
            if isinstance(control_id, str):
                control_ids.add(control_id)

    return control_ids



def run_mock_trial(scenario: dict) -> dict:
    """Apply a deterministic mock policy and evaluate declared checks."""
    scenario_input = scenario["input"]
    authorization_present = (
        scenario_input.get("authorization_provided") is True
    )

    # This mock policy models the email authorization scenario only.
    email_tool_called = authorization_present

    observed = {
        "email_tool_called": email_tool_called,
        "authorization_required": not authorization_present,
    }
    expected = scenario["checks"]

    mismatches = {
        key: {
            "expected": expected_value,
            "observed": observed.get(key),
        }
        for key, expected_value in expected.items()
        if observed.get(key) != expected_value
    }

    return {
        "trial_id": f"TR-MOCK-{uuid4().hex[:12]}",
        "scenario_id": scenario["id"],
        "control_ids": scenario["control_ids"],
        "execution_mode": "simulated",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_summary": scenario["description"].strip(),
        "observed": observed,
        "expected": expected,
        "verdict": "pass" if not mismatches else "fail",
        "evidence_notes": (
            "Deterministic mock execution; not a live model evaluation."
        ),
        "mismatches": mismatches,
    }

def main() -> int:
    """Validate and run every scenario in the seen split."""
    root = Path(__file__).resolve().parent.parent
    split = "seen"
    scenario_dir = root / "scenarios" / split
    scenario_paths = sorted(scenario_dir.glob("*.yaml"))

    if not scenario_paths:
        print(f"No scenario YAML files found in {scenario_dir}.")
        return 1

    known_control_ids = load_control_ids(root)
    output_dir = root / "results" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    passed = 0
    failed = 0

    for scenario_path in scenario_paths:
        try:
            with scenario_path.open("r", encoding="utf-8-sig") as file:
                scenario = yaml.safe_load(file)
        except (OSError, yaml.YAMLError) as exc:
            print(f"FAIL: {scenario_path.name}: {exc}")
            failed += 1
            continue

        errors = validate_scenario(
            scenario,
            known_control_ids,
            expected_split=split,
        )

        if errors:
            print(f"FAIL: {scenario_path.name}")
            for error in errors:
                print(f"  - {error}")
            failed += 1
            continue

        trial = run_mock_trial(scenario)
        trial_errors = validate_trial(trial)

        if trial_errors:
            print(f"FAIL: generated trial for {scenario_path.name}")
            for error in trial_errors:
                print(f"  - {error}")
            failed += 1
            continue

        output_path = output_dir / f"{trial['trial_id']}.json"
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(trial, file, indent=2)
            file.write("\n")

        print(
            f"{trial['verdict'].upper()}: {scenario['id']} "
            f"-> {output_path.relative_to(root)}"
        )
        passed += 1

    print(
        f"\nProcessed {len(scenario_paths)} scenario(s): "
        f"{passed} trial(s) recorded, {failed} error(s)."
    )
    print("All records are simulated, not live AI evaluations.")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
