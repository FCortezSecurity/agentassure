
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import yaml

from harness.evaluator import evaluate_checks
from harness.scenario_validator import validate_scenario
from harness.trial_validator import validate_trial


ROOT = Path(__file__).resolve().parent.parent
SCENARIO_DIR = ROOT / "scenarios" / "seen"
RESULTS_DIR = ROOT / "results" / "raw"


def load_control_ids() -> set[str]:
    """Load the IDs of all defined controls."""
    control_ids = set()
    controls_dir = ROOT / "controls"

    for path in controls_dir.glob("*.yaml"):
        with path.open("r", encoding="utf-8-sig") as file:
            control = yaml.safe_load(file)

        if isinstance(control, dict) and isinstance(control.get("id"), str):
            control_ids.add(control["id"])

    return control_ids


def run_mock_trial(
    scenario: dict,
    observed_override: dict | None = None,
) -> dict:
    """
    Run a deterministic scenario-specific mock, not a live AI model.

    observed_override is intended for testing evaluator behavior when
    the simulated agent produces unexpected observations.
    """
    scenario_input = scenario["input"]
    scenario_id = scenario["id"]

    if scenario_id == "SC-001":
        authorization_present = (
            scenario_input.get("authorization_provided") is True
        )

        observed = {
            "email_tool_called": authorization_present,
            "authorization_required": not authorization_present,
        }

    elif scenario_id == "SC-002":
        authorized_tools = scenario_input.get("authorized_tools", [])
        requested_tool = scenario_input.get("requested_tool")

        # Simulate enforcement: only explicitly authorized tools may run.
        restricted_tool_called = requested_tool in authorized_tools

        observed = {
            "restricted_tool_called": restricted_tool_called,
            "denial_recorded": not restricted_tool_called,
        }

    else:
        raise ValueError(
            f"No mock behavior defined for scenario {scenario_id!r}"
        )

    # Allow tests to inject unexpected observations.
    if observed_override is not None:
        observed = observed_override

    # Evaluate every trial, including trials without an override.
    expected = scenario["checks"]
    evaluation = evaluate_checks(expected, observed)

    return {
        "trial_id": f"TR-MOCK-{uuid4().hex[:12]}",
        "scenario_id": scenario_id,
        "control_ids": scenario["control_ids"],
        "execution_mode": "simulated",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_summary": scenario["description"].strip(),
        "observed": observed,
        "expected": expected,
        "verdict": evaluation["verdict"],
        "evidence_notes": (
            "Deterministic scenario-specific mock; "
            "not a live model evaluation."
        ),
        "mismatches": evaluation["mismatches"],
    }


def main() -> int:
    """Validate scenarios, run mock trials, and save JSON evidence records."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    control_ids = load_control_ids()
    scenario_paths = sorted(SCENARIO_DIR.glob("*.yaml"))

    if not scenario_paths:
        print(f"No scenarios found in {SCENARIO_DIR}")
        return 1

    processed = 0
    errors = 0

    for scenario_path in scenario_paths:
        try:
            with scenario_path.open("r", encoding="utf-8-sig") as file:
                scenario = yaml.safe_load(file)

            if not isinstance(scenario, dict):
                raise ValueError("Scenario YAML must contain a mapping.")

            scenario_errors = validate_scenario(
                scenario,
                control_ids,
                expected_split="seen",
            )

            if scenario_errors:
                raise ValueError(
                    "Invalid scenario: " + "; ".join(scenario_errors)
                )

            trial = run_mock_trial(scenario)

            trial_errors = validate_trial(trial)

            if trial_errors:
                raise ValueError(
                    "Invalid trial: " + "; ".join(trial_errors)
                )

            output_path = RESULTS_DIR / f"{trial['trial_id']}.json"

            with output_path.open("w", encoding="utf-8") as file:
                json.dump(trial, file, indent=2)
                file.write("\n")

            print(
                f"{trial['verdict'].upper()}: "
                f"{scenario['id']} -> "
                f"{output_path.relative_to(ROOT)}"
            )

            processed += 1

        except (OSError, ValueError, yaml.YAMLError) as exc:
            print(f"ERROR: {scenario_path.name}: {exc}")
            errors += 1

    print(
        f"\nProcessed {processed} scenario(s): "
        f"{processed} trial(s) recorded, {errors} error(s)."
    )
    print("All records are simulated, not live AI evaluations.")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
