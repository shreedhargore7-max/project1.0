from app.revenue_recovery.decision_engine import (
    ACTION_NONE,
    ACTION_MONITOR,
    ACTION_RECOVERY_REVIEW,
    ACTION_MANUAL_REVIEW,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
    decide_recovery_action,
    decide_batch_actions,
    prioritize_decisions,
    build_decision_summary,
)


def test_successful_payment_requires_no_action():

    payment = {
        "payment_id": "pay_001",
        "amount": 10000,
        "status": "captured",
    }

    risk = {
        "risk_score": 0,
        "risk_level": "LOW",
    }

    root_cause = {
        "root_causes": [],
    }

    decision = decide_recovery_action(
        payment,
        risk,
        root_cause,
    )

    assert decision["action"] == ACTION_NONE
    assert decision["priority"] == PRIORITY_LOW
    assert decision["requires_approval"] is False


def test_low_risk_payment_is_monitored():

    payment = {
        "payment_id": "pay_002",
        "amount": 500,
        "status": "created",
    }

    risk = {
        "risk_score": 20,
        "risk_level": "LOW",
    }

    root_cause = {
        "root_causes": [],
    }

    decision = decide_recovery_action(
        payment,
        risk,
        root_cause,
    )

    assert decision["action"] == ACTION_MONITOR
    assert decision["priority"] == PRIORITY_LOW


def test_medium_risk_requires_review():

    payment = {
        "payment_id": "pay_003",
        "amount": 5000,
        "status": "failed",
    }

    risk = {
        "risk_score": 55,
        "risk_level": "MEDIUM",
    }

    root_cause = {
        "root_causes": [
            "payment_failure"
        ],
    }

    decision = decide_recovery_action(
        payment,
        risk,
        root_cause,
    )

    assert (
        decision["action"]
        == ACTION_RECOVERY_REVIEW
    )

    assert (
        decision["priority"]
        == PRIORITY_MEDIUM
    )

    assert (
        decision["requires_approval"]
        is True
    )


def test_high_value_high_risk_requires_manual_review():

    payment = {
        "payment_id": "pay_004",
        "amount": 20000,
        "status": "failed",
    }

    risk = {
        "risk_score": 90,
        "risk_level": "HIGH",
    }

    root_cause = {
        "root_causes": [
            "repeated_failure",
            "high_value_transaction",
        ],
    }

    decision = decide_recovery_action(
        payment,
        risk,
        root_cause,
    )

    assert (
        decision["action"]
        == ACTION_MANUAL_REVIEW
    )

    assert (
        decision["priority"]
        == PRIORITY_HIGH
    )

    assert (
        decision["requires_approval"]
        is True
    )


def test_repeated_failure_gets_recovery_review():

    payment = {
        "payment_id": "pay_005",
        "amount": 3000,
        "status": "failed",
    }

    risk = {
        "risk_score": 75,
        "risk_level": "HIGH",
    }

    root_cause = {
        "root_causes": [
            "repeated_failure",
        ],
    }

    decision = decide_recovery_action(
        payment,
        risk,
        root_cause,
    )

    assert (
        decision["action"]
        == ACTION_RECOVERY_REVIEW
    )

    assert (
        decision["priority"]
        == PRIORITY_HIGH
    )

    assert (
        decision["requires_approval"]
        is True
    )


def test_batch_decisions():

    payments = [
        {
            "payment_id": "pay_001",
            "amount": 20000,
            "status": "failed",
        },
        {
            "payment_id": "pay_002",
            "amount": 500,
            "status": "created",
        },
    ]

    risk_results = [
        {
            "risk_score": 90,
            "risk_level": "HIGH",
        },
        {
            "risk_score": 20,
            "risk_level": "LOW",
        },
    ]

    root_cause_results = [
        {
            "root_causes": [
                "high_value_transaction",
            ],
        },
        {
            "root_causes": [],
        },
    ]

    decisions = decide_batch_actions(
        payments,
        risk_results,
        root_cause_results,
    )

    assert len(decisions) == 2


def test_prioritization():

    decisions = [
        {
            "payment_id": "pay_low",
            "priority": PRIORITY_LOW,
            "amount": 1000,
        },
        {
            "payment_id": "pay_high",
            "priority": PRIORITY_HIGH,
            "amount": 5000,
        },
        {
            "payment_id": "pay_medium",
            "priority": PRIORITY_MEDIUM,
            "amount": 3000,
        },
    ]

    ordered = prioritize_decisions(
        decisions
    )

    assert (
        ordered[0]["priority"]
        == PRIORITY_HIGH
    )

    assert (
        ordered[-1]["priority"]
        == PRIORITY_LOW
    )

def test_decision_summary():

    decisions = [
        {
            "action": ACTION_MANUAL_REVIEW,
            "priority": PRIORITY_HIGH,
            "requires_approval": True,
            "amount": 20000,
        },
        {
            "action": ACTION_RECOVERY_REVIEW,
            "priority": PRIORITY_MEDIUM,
            "requires_approval": True,
            "amount": 5000,
        },
        {
            "action": ACTION_MONITOR,
            "priority": PRIORITY_LOW,
            "requires_approval": False,
            "amount": 500,
        },
    ]

    summary = build_decision_summary(
        decisions
    )

    assert summary[
        "total_decisions"
    ] == 3

    assert summary[
        "high_priority"
    ] == 1

    assert summary[
        "medium_priority"
    ] == 1

    assert summary[
        "low_priority"
    ] == 1

    assert summary[
        "approval_required"
    ] == 2

    assert summary[
        "recovery_review"
    ] == 1

    assert summary[
        "manual_review"
    ] == 1


# ============================================================
# NEW CALIBRATION TESTS
# ============================================================

def test_high_risk_high_value_cannot_be_monitored():

    payment = {
        "payment_id": "pay_DEMO007",
        "amount": 25000,
        "status": "failed",
    }

    risk = {
        "risk_score": 100,
        "risk_level": "HIGH",
    }

    root_cause = {
        "root_causes": [
            "payment_failure",
            "repeated_failure",
            "high_value_transaction",
        ],
    }

    decision = decide_recovery_action(
        payment,
        risk,
        root_cause,
    )

    assert decision["priority"] == PRIORITY_HIGH

    assert decision["action"] == ACTION_MANUAL_REVIEW

    assert decision["requires_approval"] is True


def test_high_risk_repeated_failure_is_recovery_review():

    payment = {
        "payment_id": "pay_DEMO003",
        "amount": 8500,
        "status": "failed",
    }

    risk = {
        "risk_score": 70,
        "risk_level": "HIGH",
    }

    root_cause = {
        "root_causes": [
            "payment_failure",
            "repeated_failure",
        ],
    }

    decision = decide_recovery_action(
        payment,
        risk,
        root_cause,
    )

    assert decision["priority"] == PRIORITY_HIGH

    assert decision["action"] == ACTION_RECOVERY_REVIEW

    assert decision["requires_approval"] is True


def test_all_high_risk_transactions_require_active_action():

    payments = [
        {
            "payment_id": "pay_DEMO007",
            "amount": 25000,
            "status": "failed",
        },
        {
            "payment_id": "pay_DEMO009",
            "amount": 18000,
            "status": "failed",
        },
    ]

    risk_results = [
        {
            "risk_score": 100,
            "risk_level": "HIGH",
        },
        {
            "risk_score": 90,
            "risk_level": "HIGH",
        },
    ]

    root_cause_results = [
        {
            "root_causes": [
                "payment_failure",
                "repeated_failure",
                "high_value_transaction",
            ],
        },
        {
            "root_causes": [
                "payment_failure",
                "repeated_failure",
            ],
        },
    ]

    decisions = decide_batch_actions(
        payments,
        risk_results,
        root_cause_results,
    )

    assert all(
        item["priority"] == PRIORITY_HIGH
        for item in decisions
    )

    assert all(
        item["action"] != ACTION_MONITOR
        for item in decisions
    )


# ============================================================
# PAYMENT-ID MAPPING REGRESSION TEST
# ============================================================

def test_batch_decisions_match_by_payment_id_not_position():

    payments = [
        {
            "payment_id": "pay_A",
            "amount": 5000,
            "status": "failed",
        },
        {
            "payment_id": "pay_B",
            "amount": 20000,
            "status": "failed",
        },
        {
            "payment_id": "pay_C",
            "amount": 1000,
            "status": "created",
        },
    ]

    # Deliberately sorted differently from payments.
    risk_results = [
        {
            "payment_id": "pay_B",
            "risk_score": 100,
            "risk_level": "HIGH",
        },
        {
            "payment_id": "pay_A",
            "risk_score": 70,
            "risk_level": "HIGH",
        },
        {
            "payment_id": "pay_C",
            "risk_score": 10,
            "risk_level": "LOW",
        },
    ]

    root_cause_results = [
        {
            "payment_id": "pay_B",
            "root_causes": [
                "payment_failure",
                "repeated_failure",
                "high_value_transaction",
            ],
        },
        {
            "payment_id": "pay_A",
            "root_causes": [
                "payment_failure",
                "repeated_failure",
            ],
        },
        {
            "payment_id": "pay_C",
            "root_causes": [],
        },
    ]

    decisions = decide_batch_actions(
        payments,
        risk_results,
        root_cause_results,
    )

    by_id = {
        item["payment_id"]: item
        for item in decisions
    }

    assert (
        by_id["pay_B"]["priority"]
        == PRIORITY_HIGH
    )

    assert (
        by_id["pay_B"]["action"]
        == ACTION_MANUAL_REVIEW
    )

    assert (
        by_id["pay_A"]["priority"]
        == PRIORITY_HIGH
    )

    assert (
        by_id["pay_A"]["action"]
        == ACTION_RECOVERY_REVIEW
    )

    assert (
        by_id["pay_C"]["priority"]
        == PRIORITY_LOW
    )

    assert (
        by_id["pay_C"]["action"]
        == ACTION_MONITOR
    )
