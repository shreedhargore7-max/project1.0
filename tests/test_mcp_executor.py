from app.revenue_recovery.mcp_executor import (
    ACTION_CREATE_PAYMENT_LINK,
    execute_approved_action,
    recovery_executor,
)


def valid_payment():

    return {
        "payment_id": "pay_MCP001",
        "amount": 2000,
        "currency": "INR",
    }


def test_dry_run_payment_link():

    result = execute_approved_action(
        payment=valid_payment(),
        action=ACTION_CREATE_PAYMENT_LINK,
        dry_run=True,
    )

    assert result["success"] is True

    assert result["executed"] is False

    assert result["mode"] == "dry_run"

    assert (
        result["payment_id"]
        == "pay_MCP001"
    )

    assert result["amount"] == 2000


def test_invalid_action_is_blocked():

    result = execute_approved_action(
        payment=valid_payment(),
        action="DELETE_ACCOUNT",
        dry_run=True,
    )

    assert result["success"] is False

    assert result["executed"] is False

    assert result["mode"] == "blocked"


def test_missing_payment_id_is_blocked():

    payment = {
        "amount": 2000,
        "currency": "INR",
    }

    result = execute_approved_action(
        payment=payment,
        action=ACTION_CREATE_PAYMENT_LINK,
        dry_run=True,
    )

    assert result["success"] is False

    assert result["mode"] == "blocked"


def test_invalid_amount_is_blocked():

    payment = {
        "payment_id": "pay_MCP002",
        "amount": 0,
        "currency": "INR",
    }

    result = execute_approved_action(
        payment=payment,
        action=ACTION_CREATE_PAYMENT_LINK,
        dry_run=True,
    )

    assert result["success"] is False

    assert result["mode"] == "blocked"


def test_recovery_executor_maps_action():

    result = recovery_executor(
        payment=valid_payment(),
        action="RECOVERY_REVIEW",
        dry_run=True,
    )

    assert result["success"] is True

    assert result["executed"] is False

    assert (
        result["action"]
        == ACTION_CREATE_PAYMENT_LINK
    )


def test_manual_review_maps_to_payment_link():

    result = recovery_executor(
        payment=valid_payment(),
        action="MANUAL_REVIEW",
        dry_run=True,
    )

    assert result["success"] is True

    assert result["mode"] == "dry_run"


def test_unknown_recovery_action_is_blocked():

    result = recovery_executor(
        payment=valid_payment(),
        action="UNKNOWN_ACTION",
        dry_run=True,
    )

    assert result["success"] is False

    assert result["mode"] == "blocked"