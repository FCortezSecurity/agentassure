def evaluate_checks(
    expected: dict[str, bool],
    observed: dict[str, object],
) -> dict:
    """Compare expected boolean checks with independently supplied observations."""
    mismatches = {}

    for key, expected_value in expected.items():
        observed_value = observed.get(key)

        if observed_value is not expected_value:
            mismatches[key] = {
                "expected": expected_value,
                "observed": observed_value,
            }

    return {
        "verdict": "pass" if not mismatches else "fail",
        "mismatches": mismatches,
    }
