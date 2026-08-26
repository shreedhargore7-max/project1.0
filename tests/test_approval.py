from app.revenue_recovery.approval import (
    APPROVAL_APPROVED,
    APPROVAL_REJECTED,
    APPROVAL_REQUIRED,
    APPROVAL_BLOCKED,
    build_approval_request,
    approve_recovery,
    can_execute_recovery,
)


def decision():
    return {
        "action": "RECOVERY_REVIEW",
        "priority": "HIGH",
        "reason": (
            "Repeated payment failures"
        ),
        "requires_approval": True,
    }


def payment():
    return {
        "payment_id": "pay_APPROVAL001",
        "amount": 5000,
        "currency": "INR",
    }


def test_build_approval_request():

    result = build_approval_request(
        payment(),
        decision(),
    )

    assert (
        result["status"]
        == APPROVAL_REQUIRED
    )

    assert (
        result["payment_id"]
        == "pay_APPROVAL001"
    )

    assert (
        result["requires_approval"]
        is True
    )


def test_approval():

    request = build_approval_request(
        payment(),
        decision(),
    )

    result = approve_recovery(
        request,
        approved=True,
    )

    assert (
        result["status"]
        == APPROVAL_APPROVED
    )

    assert result["approved"] is True

    assert can_execute_recovery(
        result
    ) is True


def test_rejection():

    request = build_approval_request(
        payment(),
        decision(),
    )

    result = approve_recovery(
        request,
        approved=False,
    )

    assert (
        result["status"]
        == APPROVAL_REJECTED
    )

    assert result["approved"] is False

    assert can_execute_recovery(
        result
    ) is False


def test_non_approval_action_is_blocked():

    request = build_approval_request(
        payment(),
        {
            "action": "MONITOR",
            "priority": "LOW",
            "requires_approval": False,
        },
    )

    assert (
        request["status"]
        == APPROVAL_BLOCKED
    )

    result = approve_recovery(
        request,
        approved=True,
    )

    assert (
        result["status"]
        == APPROVAL_BLOCKED
    )

    assert can_execute_recovery(
        result
    ) is False