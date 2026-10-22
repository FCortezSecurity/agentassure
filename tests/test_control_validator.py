from harness.control_validator import validate_control


def valid_control():
    return {
        "id": "AC-001",
        "title": "Explicit authorization before sending email",
        "category": "tool_security",
        "severity": "high",
        "description": "Require authorization before sending email.",
        "expected_behavior": [
            "Reject unauthorized send requests.",
            "Validate recipient and message.",
        ],
        "testable": True,
    }


def test_valid_control_has_no_errors():
    assert validate_control(valid_control()) == []


def test_missing_required_field_is_rejected():
    control = valid_control()
    del control["title"]

    errors = validate_control(control)

    assert any("title" in error for error in errors)


def test_invalid_severity_is_rejected():
    control = valid_control()
    control["severity"] = "extreme"

    errors = validate_control(control)

    assert any("Severity" in error for error in errors)


def test_empty_expected_behavior_is_rejected():
    control = valid_control()
    control["expected_behavior"] = []

    errors = validate_control(control)

    assert any("expected_behavior" in error for error in errors)

def test_empty_title_is_rejected():
    control = valid_control()
    control["title"] = "   "

    errors = validate_control(control)

    assert any("title" in error for error in errors)


def test_malformed_control_id_is_rejected():
    control = valid_control()
    control["id"] = "control-1"

    errors = validate_control(control)

    assert any("id must use" in error for error in errors)


def test_expected_behavior_items_must_be_strings():
    control = valid_control()
    control["expected_behavior"] = ["Reject unauthorized requests", 123]

    errors = validate_control(control)

    assert any("expected_behavior" in error for error in errors)
