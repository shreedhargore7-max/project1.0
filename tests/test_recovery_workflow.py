from app.revenue_recovery.recovery_workflow import (
    STATUS_APPROVAL_REQUIRED,
    STATUS_APPROVED,
    STATUS_EXECUTED,
    STATUS_REJECTED,
    STATUS_BLOCKED,
    analyze_recovery_opportunity,
    check_recovery_policy,
    request_recovery_approval,
    execute_recovery,
    run_recovery_workflow,
    build_recovery_message,
)


def high_risk_payment():

    return {
        "payment_id": "pay_REC001",
        "amount": 20000,
        "currency": "INR",
        "status": "failed",
        "failed_attempts": 4,
        "attempts": 5,
        "previous_successes": 6,
    }


def low_risk_payment():

    return {
        "payment_id": "pay_REC002",
        "amount": 500,
        "currency": "INR",
        "status": "created",
        "failed_attempts": 0,
        "attempts": 1,
        "previous_successes": 0,
    }


# ============================================================
# ANALYSIS
# ============================================================

def test_analyze_recovery_opportunity():

    result = analyze_recovery_opportunity(
        high_risk_payment()
    )

    assert result["status"] == "ANALYZED"

    assert result["risk"]["risk_level"] == "HIGH"

    assert result["root_cause"]["root_causes"]

    assert result["decision"]["action"]


# ============================================================
# POLICY
# ============================================================

def test_policy_requires_approval():

    result = analyze_recovery_opportunity(
        high_risk_payment()
    )

    result = check_recovery_policy(
        result
    )

    assert result["policy_allowed"] is True

    assert (
        result["status"]
        == STATUS_APPROVAL_REQUIRED
    )


def test_low_risk_is_blocked():

    result = analyze_recovery_opportunity(
        low_risk_payment()
    )

    result = check_recovery_policy(
        result
    )

    assert (
        result["status"]
        == STATUS_BLOCKED
    )

    assert (
        result["policy_allowed"]
        is False
    )


# ============================================================
# APPROVAL
# ============================================================

def test_rejected_recovery():

    result = analyze_recovery_opportunity(
        high_risk_payment()
    )

    result = check_recovery_policy(
        result
    )

    result = request_recovery_approval(
        result,
        approved=False,
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        result["approval"]
        is False
    )


def test_approved_recovery():

    result = analyze_recovery_opportunity(
        high_risk_payment()
    )

    result = check_recovery_policy(
        result
    )

    result = request_recovery_approval(
        result,
        approved=True,
    )

    assert (
        result["status"]
        == STATUS_APPROVED
    )

    assert (
        result["approval"]
        is True
    )


# ============================================================
# DRY RUN
# ============================================================

def test_dry_run_does_not_execute_external_action():

    result = analyze_recovery_opportunity(
        high_risk_payment()
    )

    result = check_recovery_policy(
        result
    )

    result = request_recovery_approval(
        result,
        approved=True,
    )

    result = execute_recovery(
        result,
        dry_run=True,
    )

    assert (
        result["status"]
        == STATUS_EXECUTED
    )

    assert (
        result["execution"]["mode"]
        == "dry_run"
    )

    assert (
        result["execution"]["executed"]
        is False
    )


# ============================================================
# LIVE EXECUTOR MOCK
# ============================================================

def test_mock_executor():

    calls = []

    def mock_executor(
        payment,
        action,
    ):

        calls.append(
            {
                "payment_id":
                    payment["payment_id"],

                "action":
                    action,
            }
        )

        return {
            "success": True,
            "message":
                "Mock recovery executed",
        }

    result = run_recovery_workflow(
        high_risk_payment(),
        approved=True,
        executor=mock_executor,
        dry_run=False,
    )

    assert (
        result["status"]
        == STATUS_EXECUTED
    )

    assert (
        result["execution"]["mode"]
        == "live"
    )

    assert (
        result["execution"]["executed"]
        is True
    )

    assert len(calls) == 1


# ============================================================
# EXECUTION WITHOUT APPROVAL
# ============================================================

def test_execution_without_approval_is_blocked():

    result = analyze_recovery_opportunity(
        high_risk_payment()
    )

    result = check_recovery_policy(
        result
    )

    result = execute_recovery(
        result,
        dry_run=True,
    )

    assert (
        result["status"]
        == STATUS_BLOCKED
    )


# ============================================================
# USER MESSAGE
# ============================================================

def test_build_recovery_message():

    result = run_recovery_workflow(
        high_risk_payment(),
        approved=True,
        dry_run=True,
    )

    message = build_recovery_message(
        result
    )

    assert (
        "pay_REC001"
        in message
    )

    assert (
        "HIGH"
        in message
    )

    assert (
        "DRY"
        in message.upper()
    )