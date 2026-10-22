from pathlib import Path

import yaml

from harness.run_trial import run_mock_trial


ROOT = Path(__file__).resolve().parent.parent


def load_scenario(filename: str) -> dict:
    path = ROOT / "scenarios" / "seen" / filename
    with path.open("r", encoding="utf-8-sig") as file:
        return yaml.safe_load(file)


def test_unauthorized_email_scenario_passes():
    scenario = load_scenario("SC-001.yaml")

    trial = run_mock_trial(scenario)

    assert trial["verdict"] == "pass"
    assert trial["observed"]["email_tool_called"] is False


def test_restricted_tool_scenario_passes():
    scenario = load_scenario("SC-002.yaml")

    trial = run_mock_trial(scenario)

    assert trial["verdict"] == "pass"
    assert trial["observed"]["restricted_tool_called"] is False
    assert trial["observed"]["denial_recorded"] is True


def test_unknown_scenario_is_rejected():
    scenario = load_scenario("SC-002.yaml")
    scenario["id"] = "SC-UNKNOWN"

    try:
        run_mock_trial(scenario)
    except ValueError as exc:
        assert "No mock behavior defined" in str(exc)
    else:
        raise AssertionError("Unknown scenario should be rejected.")

def test_unauthorized_email_send_is_detected():
    scenario = load_scenario("SC-001.yaml")

    trial = run_mock_trial(
        scenario,
        observed_override={
            "email_tool_called": True,
            "authorization_required": False,
        },
    )

    assert trial["verdict"] == "fail"
    assert "email_tool_called" in trial["mismatches"]
    assert "authorization_required" in trial["mismatches"]
