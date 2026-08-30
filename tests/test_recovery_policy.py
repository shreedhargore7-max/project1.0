# ============================================================
# TESTS - RECOVERY POLICY
# ============================================================

from app.revenue_recovery.recovery_policy import (
    POLICY_ALLOW,
    POLICY_REVIEW,
    POLICY_MONITOR,
    POLICY_STOP,
    default_recovery_policy,
    validate_policy,
    is_payment_successful,
    should_stop_recovery,
    evaluate_recovery_eligibility,
    evaluate_batch_eligibility,
    build_policy_summary,
)


# ============================================================
# DEFAULT POLICY
# ============================================================

def test_default_policy_is_valid():

    policy = default_recovery_policy()

    assert (
        validate_policy(policy)
        is True
    )

    assert (
        policy["max_failed_attempts"]
        == 3
    )

    assert (
        policy["min_recovery_amount"]
        == 100.0
    )

    assert (
        policy["max_recovery_amount"]
        == 100000.0
    )

    assert (
        policy["min_risk_score"]
        == 40
    )


# ============================================================
# INVALID POLICY
# ============================================================

def test_invalid_policy_is_rejected():

    policy = {
        "max_failed_attempts": 0,
        "min_recovery_amount": 100,
        "max_recovery_amount": 100000,
        "min_risk_score": 40,
        "require_approval_above_amount": 10000,
    }

    assert (
        validate_policy(policy)
        is False
    )


# ============================================================
# SUCCESSFUL PAYMENT
# ============================================================

def test_successful_payment_is_detected():

    payment = {
        "payment_id": "pay_001",
        "amount": 5000,
        "status": "captured",
    }

    assert (
        is_payment_successful(payment)
        is True
    )


def test_successful_payment_is_stopped():

    payment = {
        "payment_id": "pay_001",
        "amount": 5000,
        "status": "captured",
    }

    should_stop, reason = (
        should_stop_recovery(
            payment
        )
    )

    assert should_stop is True

    assert (
        "already successful"
        in reason
    )


# ============================================================
# MAXIMUM FAILED ATTEMPTS
# ============================================================

def test_maximum_failed_attempts_stops_recovery():

    payment = {
        "payment_id": "pay_002",
        "amount": 10000,
        "status": "failed",
        "failed_attempts": 3,
    }

    policy = default_recovery_policy()

    should_stop, reason = (
        should_stop_recovery(
            payment,
            policy,
        )
    )

    assert should_stop is True

    assert (
        "maximum allowed"
        in reason
    )


# ============================================================
# FAILED PAYMENT BELOW ATTEMPT LIMIT
# ============================================================

def test_payment_below_attempt_limit_can_continue():

    payment = {
        "payment_id": "pay_003",
        "amount": 10000,
        "status": "failed",
        "failed_attempts": 1,
    }

    policy = default_recovery_policy()

    should_stop, reason = (
        should_stop_recovery(
            payment,
            policy,
        )
    )

    assert should_stop is False

    assert (
        "limit has not been reached"
        in reason
    )


# ============================================================
# LOW RISK
# ============================================================

def test_low_risk_payment_is_monitored():

    payment = {
        "payment_id": "pay_004",
        "amount": 5000,
        "status": "failed",
        "failed_attempts": 1,
    }

    risk = {
        "risk_score": 20,
        "risk_level": "LOW",
    }

    result = (
        evaluate_recovery_eligibility(
            payment,
            risk,
        )
    )

    assert (
        result["eligible"]
        is False
    )

    assert (
        result["action"]
        == POLICY_MONITOR
    )

    assert (
        result["requires_approval"]
        is False
    )


# ============================================================
# MEDIUM RISK
# ============================================================

def test_medium_risk_payment_is_eligible():

    payment = {
        "payment_id": "pay_005",
        "amount": 5000,
        "status": "failed",
        "failed_attempts": 1,
    }

    risk = {
        "risk_score": 50,
        "risk_level": "MEDIUM",
    }

    result = (
        evaluate_recovery_eligibility(
            payment,
            risk,
        )
    )

    assert (
        result["eligible"]
        is True
    )

    assert (
        result["action"]
        == POLICY_ALLOW
    )


# ============================================================
# HIGH RISK
# ============================================================

def test_high_risk_requires_review():

    payment = {
        "payment_id": "pay_006",
        "amount": 8000,
        "status": "failed",
        "failed_attempts": 2,
    }

    risk = {
        "risk_score": 80,
        "risk_level": "HIGH",
    }

    result = (
        evaluate_recovery_eligibility(
            payment,
            risk,
        )
    )

    assert (
        result["eligible"]
        is True
    )

    assert (
        result["action"]
        == POLICY_REVIEW
    )

    assert (
        result["requires_approval"]
        is True
    )


# ============================================================
# HIGH VALUE
# ============================================================

def test_high_value_payment_requires_review():

    payment = {
        "payment_id": "pay_007",
        "amount": 150000,
        "status": "failed",
        "failed_attempts": 1,
    }

    risk = {
        "risk_score": 80,
        "risk_level": "HIGH",
    }

    result = (
        evaluate_recovery_eligibility(
            payment,
            risk,
        )
    )

    assert (
        result["eligible"]
        is False
    )

    assert (
        result["action"]
        == POLICY_REVIEW
    )

    assert (
        result["requires_approval"]
        is True
    )


# ============================================================
# LOW AMOUNT
# ============================================================

def test_low_amount_is_not_recovered():

    payment = {
        "payment_id": "pay_008",
        "amount": 50,
        "status": "failed",
        "failed_attempts": 1,
    }

    risk = {
        "risk_score": 80,
        "risk_level": "HIGH",
    }

    result = (
        evaluate_recovery_eligibility(
            payment,
            risk,
        )
    )

    assert (
        result["eligible"]
        is False
    )

    assert (
        result["action"]
        == POLICY_MONITOR
    )


# ============================================================
# MISSING PAYMENT ID
# ============================================================

def test_missing_payment_id_is_stopped():

    payment = {
        "amount": 5000,
        "status": "failed",
        "failed_attempts": 1,
    }

    risk = {
        "risk_score": 80,
        "risk_level": "HIGH",
    }

    result = (
        evaluate_recovery_eligibility(
            payment,
            risk,
        )
    )

    assert (
        result["eligible"]
        is False
    )

    assert (
        result["action"]
        == POLICY_STOP
    )

    assert (
        result["requires_approval"]
        is False
    )


# ============================================================
# PAYMENT ABOVE MAXIMUM
# ============================================================

def test_payment_above_maximum_requires_review():

    policy = default_recovery_policy()

    payment = {
        "payment_id": "pay_009",
        "amount": 150000,
        "status": "failed",
        "failed_attempts": 1,
    }

    risk = {
        "risk_score": 70,
        "risk_level": "MEDIUM",
    }

    result = (
        evaluate_recovery_eligibility(
            payment,
            risk,
            policy,
        )
    )

    assert (
        result["eligible"]
        is False
    )

    assert (
        result["action"]
        == POLICY_REVIEW
    )

    assert (
        result["requires_approval"]
        is True
    )


# ============================================================
# STOP AFTER TOO MANY FAILURES
# ============================================================

def test_repeated_failure_stops_recovery():

    payment = {
        "payment_id": "pay_010",
        "amount": 10000,
        "status": "failed",
        "failed_attempts": 4,
    }

    risk = {
        "risk_score": 90,
        "risk_level": "HIGH",
    }

    policy = default_recovery_policy()

    result = (
        evaluate_recovery_eligibility(
            payment,
            risk,
            policy,
        )
    )

    assert (
        result["eligible"]
        is False
    )

    assert (
        result["action"]
        == POLICY_STOP
    )


# ============================================================
# BATCH EVALUATION
# ============================================================

def test_batch_eligibility():

    payments = [

        {
            "payment_id": "pay_A",
            "amount": 20000,
            "status": "failed",
            "failed_attempts": 2,
        },

        {
            "payment_id": "pay_B",
            "amount": 5000,
            "status": "failed",
            "failed_attempts": 1,
        },

        {
            "payment_id": "pay_C",
            "amount": 500,
            "status": "failed",
            "failed_attempts": 1,
        },
    ]


    risk_results = [

        {
            "payment_id": "pay_A",
            "risk_score": 90,
            "risk_level": "HIGH",
        },

        {
            "payment_id": "pay_B",
            "risk_score": 50,
            "risk_level": "MEDIUM",
        },

        {
            "payment_id": "pay_C",
            "risk_score": 20,
            "risk_level": "LOW",
        },
    ]


    result = evaluate_batch_eligibility(
        payments,
        risk_results,
    )


    assert len(result) == 3


    by_id = {
        item["payment_id"]: item
        for item in result
    }


    assert (
        by_id["pay_A"]["action"]
        == POLICY_REVIEW
    )


    assert (
        by_id["pay_B"]["action"]
        == POLICY_ALLOW
    )


    assert (
        by_id["pay_C"]["action"]
        == POLICY_MONITOR
    )


# ============================================================
# POLICY SUMMARY
# ============================================================

def test_policy_summary():

    evaluations = [

        {
            "payment_id": "pay_001",
            "amount": 20000,
            "eligible": True,
            "action": POLICY_REVIEW,
            "requires_approval": True,
        },

        {
            "payment_id": "pay_002",
            "amount": 5000,
            "eligible": True,
            "action": POLICY_ALLOW,
            "requires_approval": False,
        },

        {
            "payment_id": "pay_003",
            "amount": 500,
            "eligible": False,
            "action": POLICY_MONITOR,
            "requires_approval": False,
        },

        {
            "payment_id": "pay_004",
            "amount": 10000,
            "eligible": False,
            "action": POLICY_STOP,
            "requires_approval": True,
        },
    ]


    summary = build_policy_summary(
        evaluations
    )


    assert (
        summary["total"]
        == 4
    )


    assert (
        summary["eligible"]
        == 2
    )


    assert (
        summary["review"]
        == 1
    )


    assert (
        summary["monitor"]
        == 1
    )


    assert (
        summary["stopped"]
        == 1
    )


    assert (
        summary["approval_required"]
        == 2
    )


    assert (
        summary["eligible_amount"]
        == 25000
    )