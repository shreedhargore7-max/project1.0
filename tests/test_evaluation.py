from app.revenue_recovery.evaluation import (
    evaluate_risk_predictions,
    evaluate_decisions,
    evaluate_priorities,
    evaluate_approval_safety,
    evaluate_top_priority,
    evaluate_recovery_system,
    build_evaluation_report,
)


def test_risk_accuracy():

    expected = {
        "pay_001": "HIGH",
        "pay_002": "MEDIUM",
        "pay_003": "LOW",
    }

    actual = [
        {
            "payment_id": "pay_001",
            "risk_level": "HIGH",
        },
        {
            "payment_id": "pay_002",
            "risk_level": "MEDIUM",
        },
        {
            "payment_id": "pay_003",
            "risk_level": "LOW",
        },
    ]

    result = evaluate_risk_predictions(
        expected,
        actual,
    )

    assert result["accuracy"] == 1.0
    assert result["correct"] == 3


def test_decision_accuracy():

    expected = {
        "pay_001": "MANUAL_REVIEW",
        "pay_002": "RECOVERY_REVIEW",
        "pay_003": "MONITOR",
    }

    actual = [
        {
            "payment_id": "pay_001",
            "action": "MANUAL_REVIEW",
        },
        {
            "payment_id": "pay_002",
            "action": "RECOVERY_REVIEW",
        },
        {
            "payment_id": "pay_003",
            "action": "MONITOR",
        },
    ]

    result = evaluate_decisions(
        expected,
        actual,
    )

    assert result["accuracy"] == 1.0


def test_priority_accuracy():

    expected = {
        "pay_001": "HIGH",
        "pay_002": "MEDIUM",
        "pay_003": "LOW",
    }

    actual = [
        {
            "payment_id": "pay_001",
            "priority": "HIGH",
        },
        {
            "payment_id": "pay_002",
            "priority": "MEDIUM",
        },
        {
            "payment_id": "pay_003",
            "priority": "LOW",
        },
    ]

    result = evaluate_priorities(
        expected,
        actual,
    )

    assert result["accuracy"] == 1.0


def test_approval_safety():

    decisions = [
        {
            "action": "MANUAL_REVIEW",
            "requires_approval": True,
        },
        {
            "action": "RECOVERY_REVIEW",
            "requires_approval": True,
        },
        {
            "action": "MONITOR",
            "requires_approval": False,
        },
    ]

    result = evaluate_approval_safety(
        decisions
    )

    assert (
        result["sensitive_actions"]
        == 2
    )

    assert (
        result["protected"]
        == 2
    )

    assert (
        result["violations"]
        == 0
    )

    assert (
        result["safety_rate"]
        == 1.0
    )


def test_top_priority():

    prioritized = [
        {
            "payment_id": "pay_TOP",
            "priority": "HIGH",
        },
        {
            "payment_id": "pay_OTHER",
            "priority": "MEDIUM",
        },
    ]

    result = evaluate_top_priority(
        "pay_TOP",
        prioritized,
    )

    assert result["correct"] is True


def test_complete_evaluation():

    evaluation = evaluate_recovery_system(

        expected_risk_levels={
            "pay_001": "HIGH",
            "pay_002": "LOW",
        },

        expected_actions={
            "pay_001": "MANUAL_REVIEW",
            "pay_002": "MONITOR",
        },

        expected_priorities={
            "pay_001": "HIGH",
            "pay_002": "LOW",
        },

        expected_top_payment="pay_001",

        risk_results=[
            {
                "payment_id": "pay_001",
                "risk_level": "HIGH",
            },
            {
                "payment_id": "pay_002",
                "risk_level": "LOW",
            },
        ],

        decisions=[
            {
                "payment_id": "pay_001",
                "action": "MANUAL_REVIEW",
                "priority": "HIGH",
                "requires_approval": True,
            },
            {
                "payment_id": "pay_002",
                "action": "MONITOR",
                "priority": "LOW",
                "requires_approval": False,
            },
        ],

        prioritized_decisions=[
            {
                "payment_id": "pay_001",
                "priority": "HIGH",
            },
            {
                "payment_id": "pay_002",
                "priority": "LOW",
            },
        ],
    )

    assert (
        evaluation["risk"]["accuracy"]
        == 1.0
    )

    assert (
        evaluation["decisions"]["accuracy"]
        == 1.0
    )

    assert (
        evaluation["priorities"]["accuracy"]
        == 1.0
    )

    assert (
        evaluation["approval_safety"]["violations"]
        == 0
    )

    assert (
        evaluation["top_priority"]["correct"]
        is True
    )


def test_evaluation_report():

    evaluation = {
        "risk": {
            "accuracy": 1.0,
        },
        "decisions": {
            "accuracy": 1.0,
        },
        "priorities": {
            "accuracy": 1.0,
        },
        "approval_safety": {
            "safety_rate": 1.0,
            "violations": 0,
        },
        "top_priority": {
            "correct": True,
        },
    }

    report = build_evaluation_report(
        evaluation
    )

    assert (
        "Risk accuracy: 100.0%"
        in report
    )

    assert (
        "Decision accuracy: 100.0%"
        in report
    )

    assert (
        "Priority accuracy: 100.0%"
        in report
    )

    assert (
        "Top-priority selection: PASS"
        in report
    )