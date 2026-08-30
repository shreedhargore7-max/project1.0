# ============================================================
# TESTS - RECOVERY WORKFLOW
# ============================================================

from app.revenue_recovery.recovery_workflow import (
    STATUS_ANALYZED,
    STATUS_APPROVAL_REQUIRED,
    STATUS_APPROVED,
    STATUS_EXECUTED,
    STATUS_REJECTED,
    STATUS_BLOCKED,
    analyze_recovery_opportunity,
    check_recovery_policy,
    select_workflow_strategy,
    request_recovery_approval,
    execute_recovery,
    run_recovery_workflow,
    build_recovery_message,
)

from app.revenue_recovery.recovery_policy import (
    default_recovery_policy,
)


# ============================================================
# TEST DATA
# ============================================================

def high_risk_payment():

    return {
        "payment_id": "pay_REC001",
        "amount": 20000,
        "currency": "INR",
        "status": "failed",

        # Below the default stopping threshold of 3.
        "failed_attempts": 2,
        "attempts": 3,

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


def stopped_payment():

    return {
        "payment_id": "pay_REC003",
        "amount": 20000,
        "currency": "INR",
        "status": "failed",

        # Reached the default stopping threshold.
        "failed_attempts": 3,
        "attempts": 4,

        "previous_successes": 6,
    }


# ============================================================
# ANALYSIS
# ============================================================

def test_analyze_recovery_opportunity():

    result = analyze_recovery_opportunity(
        high_risk_payment()
    )

    assert (
        result["status"]
        == STATUS_ANALYZED
    )

    assert (
        result["risk"]["risk_level"]
        == "HIGH"
    )

    assert result[
        "root_cause"
    ]["root_causes"]

    assert result[
        "decision"
    ]["action"]


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

    assert (
        result["policy_allowed"]
        is True
    )

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


def test_repeated_failure_is_blocked():

    result = analyze_recovery_opportunity(
        stopped_payment()
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
# STRATEGY
# ============================================================

def test_high_value_high_risk_gets_manual_review():

    result = analyze_recovery_opportunity(
        high_risk_payment()
    )

    result = check_recovery_policy(
        result
    )

    result = select_workflow_strategy(
        result
    )

    assert (
        result["strategy"]
        == "MANUAL_REVIEW"
    )

    assert (
        result["strategy_allowed"]
        is True
    )

    assert (
        result["strategy_requires_approval"]
        is True
    )


def test_policy_block_prevents_strategy_execution():

    result = analyze_recovery_opportunity(
        stopped_payment()
    )

    result = check_recovery_policy(
        result
    )

    result = select_workflow_strategy(
        result
    )

    assert (
        result["strategy_allowed"]
        is False
    )

    assert (
        result["strategy"]
        == "STOP"
    )

    assert (
        result["status"]
        == STATUS_BLOCKED
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

    result = select_workflow_strategy(
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

    result = select_workflow_strategy(
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

    result = select_workflow_strategy(
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
            "success":
                True,

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

    result = select_workflow_strategy(
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
# COMPLETE WORKFLOW
# ============================================================

def test_complete_workflow_reaches_approval():

    result = run_recovery_workflow(
        high_risk_payment(),
        approved=False,
        dry_run=True,
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        result["policy_allowed"]
        is True
    )

    assert (
        result["strategy_allowed"]
        is True
    )


def test_complete_workflow_executes_after_approval():

    result = run_recovery_workflow(
        high_risk_payment(),
        approved=True,
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


def test_complete_workflow_stops_after_attempt_limit():

    result = run_recovery_workflow(
        stopped_payment(),
        approved=True,
        dry_run=True,
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
        "MANUAL_REVIEW"
        in message
    )

    assert (
        "DRY"
        in message.upper()
    )


# ============================================================
# POLICY OVERRIDE TEST
# ============================================================

def test_custom_policy_can_change_attempt_limit():

    payment = high_risk_payment()

    custom_policy = (
        default_recovery_policy()
    )

    custom_policy[
        "max_failed_attempts"
    ] = 5

    result = run_recovery_workflow(
        payment,
        approved=True,
        dry_run=True,
        policy=custom_policy,
    )

    assert (
        result["policy_allowed"]
        is True
    )

    assert (
        result["strategy_allowed"]
        is True
    )

    assert (
        result["status"]
        == STATUS_EXECUTED
    )