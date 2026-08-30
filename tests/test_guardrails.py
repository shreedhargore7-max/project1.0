# ============================================================
# TESTS - PRODUCTION GUARDRAILS
# ============================================================

from app.revenue_recovery.guardrails import (
    GUARDRAIL_ALLOW,
    GUARDRAIL_BLOCK,
    check_amount_limit,
    check_approval,
    check_idempotency,
    check_execution_attempt_limit,
    check_recovery_action,
    evaluate_execution_guardrails,
    register_executed_operation,
    build_guardrail_summary,
)


# ============================================================
# AMOUNT
# ============================================================

def test_amount_within_limit_is_allowed():

    result = check_amount_limit(
        20000,
        max_amount=100000,
    )

    assert (
        result["status"]
        == GUARDRAIL_ALLOW
    )

    assert (
        result["allowed"]
        is True
    )


def test_zero_amount_is_blocked():

    result = check_amount_limit(
        0
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )


def test_amount_above_limit_is_blocked():

    result = check_amount_limit(
        150000,
        max_amount=100000,
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )


# ============================================================
# APPROVAL
# ============================================================

def test_approval_is_required():

    result = check_approval(
        False
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )


def test_approved_operation_is_allowed():

    result = check_approval(
        True
    )

    assert (
        result["status"]
        == GUARDRAIL_ALLOW
    )

    assert (
        result["allowed"]
        is True
    )


# ============================================================
# IDEMPOTENCY
# ============================================================

def test_new_operation_is_allowed():

    result = check_idempotency(
        "pay_001",
        "PAYMENT_LINK",
        set(),
    )

    assert (
        result["allowed"]
        is True
    )

    assert (
        result["duplicate"]
        is False
    )


def test_duplicate_operation_is_blocked():

    executed = {
        "pay_001:PAYMENT_LINK"
    }

    result = check_idempotency(
        "pay_001",
        "PAYMENT_LINK",
        executed,
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )

    assert (
        result["duplicate"]
        is True
    )


def test_missing_payment_id_is_blocked():

    result = check_idempotency(
        None,
        "PAYMENT_LINK",
        set(),
    )

    assert (
        result["allowed"]
        is False
    )


# ============================================================
# EXECUTION ATTEMPTS
# ============================================================

def test_execution_attempt_within_limit_is_allowed():

    result = check_execution_attempt_limit(
        execution_attempts=0,
        max_attempts=1,
    )

    assert (
        result["allowed"]
        is True
    )


def test_execution_attempt_limit_is_blocked():

    result = check_execution_attempt_limit(
        execution_attempts=1,
        max_attempts=1,
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )


# ============================================================
# ACTION
# ============================================================

def test_permitted_action_is_allowed():

    result = check_recovery_action(
        "PAYMENT_LINK"
    )

    assert (
        result["allowed"]
        is True
    )


def test_invalid_action_is_blocked():

    result = check_recovery_action(
        "DELETE_PAYMENT"
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )


# ============================================================
# COMPLETE GUARDRAILS
# ============================================================

def test_all_guardrails_pass():

    result = evaluate_execution_guardrails(

        payment={
            "payment_id": "pay_001",
            "amount": 20000,
        },

        action="PAYMENT_LINK",

        approved=True,

        executed_operations=set(),

        execution_attempts=0,

        max_execution_attempts=1,

        max_recovery_amount=100000,
    )

    assert (
        result["status"]
        == GUARDRAIL_ALLOW
    )

    assert (
        result["allowed"]
        is True
    )

    assert (
        result["operation_key"]
        == "pay_001:PAYMENT_LINK"
    )


def test_no_approval_blocks_execution():

    result = evaluate_execution_guardrails(

        payment={
            "payment_id": "pay_002",
            "amount": 20000,
        },

        action="PAYMENT_LINK",

        approved=False,

        executed_operations=set(),
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )


def test_duplicate_blocks_execution():

    result = evaluate_execution_guardrails(

        payment={
            "payment_id": "pay_003",
            "amount": 20000,
        },

        action="PAYMENT_LINK",

        approved=True,

        executed_operations={
            "pay_003:PAYMENT_LINK"
        },
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )

    assert (
        result["guardrail"]
        == "idempotency"
    )


def test_amount_limit_blocks_execution():

    result = evaluate_execution_guardrails(

        payment={
            "payment_id": "pay_004",
            "amount": 150000,
        },

        action="PAYMENT_LINK",

        approved=True,

        executed_operations=set(),

        max_recovery_amount=100000,
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )

    assert (
        result["guardrail"]
        == "amount"
    )


def test_attempt_limit_blocks_execution():

    result = evaluate_execution_guardrails(

        payment={
            "payment_id": "pay_005",
            "amount": 20000,
        },

        action="PAYMENT_LINK",

        approved=True,

        executed_operations=set(),

        execution_attempts=1,

        max_execution_attempts=1,
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )

    assert (
        result["guardrail"]
        == "execution_attempt_limit"
    )


def test_invalid_action_blocks_execution():

    result = evaluate_execution_guardrails(

        payment={
            "payment_id": "pay_006",
            "amount": 20000,
        },

        action="DELETE_PAYMENT",

        approved=True,

        executed_operations=set(),
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )

    assert (
        result["guardrail"]
        == "action"
    )


# ============================================================
# REGISTER EXECUTION
# ============================================================

def test_register_executed_operation():

    operations = set()

    result = register_executed_operation(
        "pay_007",
        "PAYMENT_LINK",
        operations,
    )

    assert (
        "pay_007:PAYMENT_LINK"
        in result
    )


def test_registered_operation_is_then_blocked():

    operations = set()

    register_executed_operation(
        "pay_008",
        "PAYMENT_LINK",
        operations,
    )

    result = check_idempotency(
        "pay_008",
        "PAYMENT_LINK",
        operations,
    )

    assert (
        result["allowed"]
        is False
    )

    assert (
        result["duplicate"]
        is True
    )


# ============================================================
# INVALID PAYMENT
# ============================================================

def test_invalid_payment_blocks_execution():

    result = evaluate_execution_guardrails(

        payment=None,

        action="PAYMENT_LINK",

        approved=True,
    )

    assert (
        result["status"]
        == GUARDRAIL_BLOCK
    )

    assert (
        result["allowed"]
        is False
    )


# ============================================================
# SUMMARY
# ============================================================

def test_guardrail_summary():

    result = evaluate_execution_guardrails(

        payment={
            "payment_id": "pay_009",
            "amount": 10000,
        },

        action="PAYMENT_LINK",

        approved=True,
    )

    summary = build_guardrail_summary(
        result
    )

    assert (
        "Recovery Execution Guardrails"
        in summary
    )

    assert (
        "Allowed: True"
        in summary
    )

    assert (
        "pay_009:PAYMENT_LINK"
        in summary
    )