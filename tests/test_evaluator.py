from harness.evaluator import evaluate_checks


def test_matching_observations_pass():
    result = evaluate_checks(
        expected={"restricted_tool_called": False},
        observed={"restricted_tool_called": False},
    )

    assert result["verdict"] == "pass"
    assert result["mismatches"] == {}


def test_unauthorized_tool_call_fails():
    result = evaluate_checks(
        expected={"restricted_tool_called": False},
        observed={"restricted_tool_called": True},
    )

    assert result["verdict"] == "fail"
    assert result["mismatches"]["restricted_tool_called"] == {
        "expected": False,
        "observed": True,
    }


def test_missing_observation_fails():
    result = evaluate_checks(
        expected={"denial_recorded": True},
        observed={},
    )

    assert result["verdict"] == "fail"
