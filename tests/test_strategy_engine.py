# ============================================================
# TESTS - STRATEGY ENGINE
# ============================================================

from app.revenue_recovery.strategy_engine import (
    STRATEGY_MONITOR,
    STRATEGY_RETRY,
    STRATEGY_PAYMENT_LINK,
    STRATEGY_MANUAL_REVIEW,
    STRATEGY_STOP,
    is_successful_payment,
    select_recovery_strategy,
    select_batch_recovery_strategies,
    build_strategy_summary,
)


def test_successful_payment_is_detected():

    payment = {
        "payment_id": "pay_001",
        "amount": 5000,
        "status": "captured",
    }

    assert (
        is_successful_payment(
            payment
        )
        is True
    )


def test_low_risk_is_monitored():

    result = select_recovery_strategy(

        {
            "payment_id": "pay_002",
            "amount": 1000,
            "status": "failed",
            "failed_attempts": 1,
        },

        {
            "risk_score": 20,
            "risk_level": "LOW",
        },

        {
            "eligible": True,
            "requires_approval": False,
            "max_attempts": 3,
        },
    )


    assert (
        result["strategy"]
        == STRATEGY_MONITOR
    )


    assert (
        result["requires_approval"]
        is False
    )


def test_medium_risk_uses_retry():

    result = select_recovery_strategy(

        {
            "payment_id": "pay_003",
            "amount": 5000,
            "status": "failed",
            "failed_attempts": 1,
        },

        {
            "risk_score": 50,
            "risk_level": "MEDIUM",
        },

        {
            "eligible": True,
            "requires_approval": False,
            "max_attempts": 3,
        },
    )


    assert (
        result["strategy"]
        == STRATEGY_RETRY
    )


def test_high_risk_uses_payment_link():

    result = select_recovery_strategy(

        {
            "payment_id": "pay_004",
            "amount": 7000,
            "status": "failed",
            "failed_attempts": 2,
        },

        {
            "risk_score": 80,
            "risk_level": "HIGH",
        },

        {
            "eligible": True,
            "requires_approval": True,
            "max_attempts": 3,
        },
    )


    assert (
        result["strategy"]
        == STRATEGY_PAYMENT_LINK
    )


    assert (
        result["requires_approval"]
        is True
    )


def test_high_value_high_risk_requires_manual_review():

    result = select_recovery_strategy(

        {
            "payment_id": "pay_005",
            "amount": 25000,
            "status": "failed",
            "failed_attempts": 2,
        },

        {
            "risk_score": 100,
            "risk_level": "HIGH",
        },

        {
            "eligible": True,
            "requires_approval": True,
            "max_attempts": 3,
        },
    )


    assert (
        result["strategy"]
        == STRATEGY_MANUAL_REVIEW
    )


    assert (
        result["requires_approval"]
        is True
    )


def test_maximum_attempts_stops_recovery():

    result = select_recovery_strategy(

        {
            "payment_id": "pay_006",
            "amount": 10000,
            "status": "failed",
            "failed_attempts": 3,
        },

        {
            "risk_score": 90,
            "risk_level": "HIGH",
        },

        {
            "eligible": True,
            "requires_approval": True,
            "max_attempts": 3,
        },
    )


    assert (
        result["strategy"]
        == STRATEGY_STOP
    )


    assert (
        result["requires_approval"]
        is True
    )


def test_ineligible_payment_is_stopped():

    result = select_recovery_strategy(

        {
            "payment_id": "pay_007",
            "amount": 5000,
            "status": "failed",
            "failed_attempts": 1,
        },

        {
            "risk_score": 90,
            "risk_level": "HIGH",
        },

        {
            "eligible": False,
            "requires_approval": False,
            "max_attempts": 3,
        },
    )


    assert (
        result["strategy"]
        == STRATEGY_STOP
    )


def test_successful_payment_is_stopped():

    result = select_recovery_strategy(

        {
            "payment_id": "pay_008",
            "amount": 5000,
            "status": "captured",
            "failed_attempts": 0,
        },

        {
            "risk_score": 10,
            "risk_level": "LOW",
        },

        {
            "eligible": True,
            "requires_approval": False,
            "max_attempts": 3,
        },
    )


    assert (
        result["strategy"]
        == STRATEGY_STOP
    )


def test_invalid_amount_is_stopped():

    result = select_recovery_strategy(

        {
            "payment_id": "pay_009",
            "amount": 0,
            "status": "failed",
            "failed_attempts": 1,
        },

        {
            "risk_score": 80,
            "risk_level": "HIGH",
        },

        {
            "eligible": True,
            "requires_approval": True,
            "max_attempts": 3,
        },
    )


    assert (
        result["strategy"]
        == STRATEGY_STOP
    )


def test_batch_strategy_selection():

    payments = [

        {
            "payment_id": "pay_A",
            "amount": 25000,
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
            "amount": 1000,
            "status": "failed",
            "failed_attempts": 1,
        },
    ]


    # Deliberately different ordering.
    risk_results = [

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

        {
            "payment_id": "pay_A",
            "risk_score": 100,
            "risk_level": "HIGH",
        },
    ]


    policy_results = [

        {
            "payment_id": "pay_A",
            "eligible": True,
            "requires_approval": True,
            "max_attempts": 3,
        },

        {
            "payment_id": "pay_B",
            "eligible": True,
            "requires_approval": False,
            "max_attempts": 3,
        },

        {
            "payment_id": "pay_C",
            "eligible": True,
            "requires_approval": False,
            "max_attempts": 3,
        },
    ]


    result = select_batch_recovery_strategies(

        payments,

        risk_results,

        policy_results,
    )


    by_id = {
        item["payment_id"]: item
        for item in result
    }


    assert (
        by_id["pay_A"]["strategy"]
        == STRATEGY_MANUAL_REVIEW
    )


    assert (
        by_id["pay_B"]["strategy"]
        == STRATEGY_RETRY
    )


    assert (
        by_id["pay_C"]["strategy"]
        == STRATEGY_MONITOR
    )


def test_strategy_summary():

    strategies = [

        {
            "payment_id": "pay_001",
            "strategy": STRATEGY_MANUAL_REVIEW,
            "requires_approval": True,
        },

        {
            "payment_id": "pay_002",
            "strategy": STRATEGY_PAYMENT_LINK,
            "requires_approval": True,
        },

        {
            "payment_id": "pay_003",
            "strategy": STRATEGY_RETRY,
            "requires_approval": False,
        },

        {
            "payment_id": "pay_004",
            "strategy": STRATEGY_MONITOR,
            "requires_approval": False,
        },

        {
            "payment_id": "pay_005",
            "strategy": STRATEGY_STOP,
            "requires_approval": True,
        },
    ]


    summary = build_strategy_summary(
        strategies
    )


    assert (
        summary["total"]
        == 5
    )


    assert (
        summary["manual_review"]
        == 1
    )


    assert (
        summary["payment_link"]
        == 1
    )


    assert (
        summary["retry"]
        == 1
    )


    assert (
        summary["monitor"]
        == 1
    )


    assert (
        summary["stop"]
        == 1
    )


    assert (
        summary["approval_required"]
        == 3
    )