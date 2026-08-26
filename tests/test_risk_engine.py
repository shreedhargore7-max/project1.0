from app.revenue_recovery.risk_engine import (
    calculate_risk_score,
    analyze_payment,
    analyze_payments,
    build_risk_summary,
)


def test_high_risk_payment():

    payment = {
        "payment_id": "pay_TEST001",
        "amount": 20000,
        "currency": "INR",
        "status": "failed",
        "failed_attempts": 4,
        "attempts": 5,
        "previous_successes": 6,
    }

    score = calculate_risk_score(
        payment
    )

    assert score >= 70


def test_payment_analysis():

    payment = {
        "payment_id": "pay_TEST002",
        "amount": 5000,
        "currency": "INR",
        "status": "failed",
        "failed_attempts": 2,
        "attempts": 3,
        "previous_successes": 3,
    }

    result = analyze_payment(
        payment
    )

    assert result["payment_id"] == "pay_TEST002"

    assert result["amount"] == 5000

    assert result["risk_score"] > 0

    assert result["risk_level"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    assert result["reasons"]


def test_batch_analysis():

    payments = [

        {
            "payment_id": "pay_001",
            "amount": 20000,
            "status": "failed",
            "failed_attempts": 4,
            "attempts": 5,
            "previous_successes": 6,
        },

        {
            "payment_id": "pay_002",
            "amount": 500,
            "status": "created",
            "failed_attempts": 0,
            "attempts": 1,
            "previous_successes": 0,
        },

    ]

    results = analyze_payments(
        payments
    )

    assert len(
        results
    ) == 2

    assert results[0]["risk_score"] >= (
        results[1]["risk_score"]
    )


def test_summary():

    results = [

        {
            "risk_level": "HIGH",
            "revenue_at_risk": 20000,
        },

        {
            "risk_level": "MEDIUM",
            "revenue_at_risk": 5000,
        },

        {
            "risk_level": "LOW",
            "revenue_at_risk": 0,
        },

    ]

    summary = build_risk_summary(
        results
    )

    assert summary[
        "total_transactions"
    ] == 3

    assert summary[
        "high_risk_transactions"
    ] == 1

    assert summary[
        "medium_risk_transactions"
    ] == 1

    assert summary[
        "low_risk_transactions"
    ] == 1

    assert summary[
        "total_revenue_at_risk"
    ] == 25000