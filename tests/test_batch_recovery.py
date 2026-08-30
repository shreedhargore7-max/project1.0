# ============================================================
# TESTS - BATCH RECOVERY
# ============================================================

from app.revenue_recovery.batch_recovery import (
    calculate_batch_recovery_metrics,
    build_batch_recovery_report,
)


# ============================================================
# BATCH RECOVERY METRICS
# ============================================================

def test_batch_recovery_metrics():

    payments = [

        {
            "payment_id": "pay_001",
            "amount": 20000,
            "risk_level": "HIGH",
        },

        {
            "payment_id": "pay_002",
            "amount": 10000,
            "risk_level": "HIGH",
        },

        {
            "payment_id": "pay_003",
            "amount": 5000,
            "risk_level": "MEDIUM",
        },

        {
            "payment_id": "pay_004",
            "amount": 1000,
            "risk_level": "LOW",
        },
    ]


    decisions = [

        {
            "payment_id": "pay_001",
            "amount": 20000,
            "action": "MANUAL_REVIEW",
            "requires_approval": True,
        },

        {
            "payment_id": "pay_002",
            "amount": 10000,
            "action": "RECOVERY_REVIEW",
            "requires_approval": True,
        },

        {
            "payment_id": "pay_003",
            "amount": 5000,
            "action": "MONITOR",
            "requires_approval": False,
        },

        {
            "payment_id": "pay_004",
            "amount": 1000,
            "action": "NO_ACTION",
            "requires_approval": False,
        },
    ]


    metrics = calculate_batch_recovery_metrics(

        payments,

        decisions,

        recovered_payment_ids={
            "pay_001"
        },
    )


    assert (
        metrics["total_transactions"]
        == 4
    )


    assert (
        metrics["total_revenue"]
        == 36000
    )


    assert (
        metrics["total_revenue_at_risk"]
        == 30000
    )


    assert (
        metrics["high_risk_transactions"]
        == 2
    )


    assert (
        metrics["medium_risk_transactions"]
        == 1
    )


    assert (
        metrics[
            "recovery_eligible_transactions"
        ]
        == 2
    )


    assert (
        metrics[
            "recovery_eligible_amount"
        ]
        == 30000
    )


    assert (
        metrics["recovered_amount"]
        == 20000
    )


    assert (
        abs(
            metrics["recovery_rate"]
            - (20 / 30)
        )
        < 0.0001
    )


    assert (
        metrics["unrecovered_amount"]
        == 10000
    )


# ============================================================
# OUTCOME-TRACKED RECOVERY
# ============================================================

def test_batch_metrics_use_actual_outcomes():

    payments = [

        {
            "payment_id": "pay_001",
            "amount": 20000,
            "risk_level": "HIGH",
        },

        {
            "payment_id": "pay_002",
            "amount": 10000,
            "risk_level": "HIGH",
        },

        {
            "payment_id": "pay_003",
            "amount": 5000,
            "risk_level": "HIGH",
        },
    ]


    decisions = [

        {
            "payment_id": "pay_001",
            "amount": 20000,
            "action": "MANUAL_REVIEW",
            "requires_approval": True,
        },

        {
            "payment_id": "pay_002",
            "amount": 10000,
            "action": "RECOVERY_REVIEW",
            "requires_approval": True,
        },

        {
            "payment_id": "pay_003",
            "amount": 5000,
            "action": "RECOVERY_REVIEW",
            "requires_approval": True,
        },
    ]


    outcomes = {

        "pay_001":
            "captured",

        "pay_002":
            "pending",

        "pay_003":
            "failed",
    }


    metrics = calculate_batch_recovery_metrics(

        payments,

        decisions,

        recovery_outcomes=outcomes,
    )


    assert (
        metrics["recovered_transactions"]
        == 1
    )


    assert (
        metrics["recovered_amount"]
        == 20000
    )


    assert (
        metrics["pending_transactions"]
        == 1
    )


    assert (
        metrics["pending_amount"]
        == 10000
    )


    assert (
        metrics["failed_transactions"]
        == 1
    )


    assert (
        metrics["failed_amount"]
        == 5000
    )


    assert (
        metrics["recovery_eligible_amount"]
        == 35000
    )


    assert (
        abs(
            metrics["recovery_rate"]
            - (20000 / 35000)
        )
        < 0.0001
    )


# ============================================================
# CREATED PAYMENT LINK IS NOT RECOVERY
# ============================================================

def test_created_payment_link_is_not_recovered():

    payments = [

        {
            "payment_id": "pay_001",
            "amount": 25000,
            "risk_level": "HIGH",
        }
    ]


    decisions = [

        {
            "payment_id": "pay_001",
            "amount": 25000,
            "action": "MANUAL_REVIEW",
            "requires_approval": True,
        }
    ]


    outcomes = {

        "pay_001":
            "created",
    }


    metrics = calculate_batch_recovery_metrics(

        payments,

        decisions,

        recovery_outcomes=outcomes,
    )


    assert (
        metrics["recovered_amount"]
        == 0
    )


    assert (
        metrics["recovered_transactions"]
        == 0
    )


    assert (
        metrics["created_transactions"]
        == 1
    )


    assert (
        metrics["created_amount"]
        == 25000
    )


    assert (
        metrics["recovery_rate"]
        == 0
    )


# ============================================================
# RECOVERY MUST NOT BE CLAIMED
# ============================================================

def test_recovery_not_claimed_without_recovered_id():

    payments = [

        {
            "payment_id": "pay_001",
            "amount": 20000,
            "risk_level": "HIGH",
        }
    ]


    decisions = [

        {
            "payment_id": "pay_001",
            "amount": 20000,
            "action": "RECOVERY_REVIEW",
            "requires_approval": True,
        }
    ]


    metrics = calculate_batch_recovery_metrics(

        payments,

        decisions,
    )


    assert (
        metrics["recovered_amount"]
        == 0
    )


    assert (
        metrics["recovery_rate"]
        == 0
    )


    assert (
        metrics["recovered_transactions"]
        == 0
    )


# ============================================================
# REPORT
# ============================================================

def test_report():

    metrics = {

        "total_transactions":
            100,

        "total_revenue":
            500000,

        "total_revenue_at_risk":
            100000,

        "recovery_eligible_transactions":
            20,

        "recovery_eligible_amount":
            80000,

        "approved_transactions":
            12,

        "approved_amount":
            60000,

        "recovered_transactions":
            8,

        "recovered_amount":
            40000,

        "recovery_rate":
            0.5,

        "pending_transactions":
            2,

        "pending_amount":
            10000,

        "failed_transactions":
            2,

        "failed_amount":
            10000,

        "unrecovered_amount":
            40000,
    }


    report = build_batch_recovery_report(
        metrics
    )


    assert (
        "Transactions analyzed: 100"
        in report
    )


    assert (
        "₹100,000.00"
        in report
    )


    assert (
        "Recovery rate: 50.00%"
        in report
    )


    assert (
        "Recovered: ₹40,000.00"
        in report
    )


    assert (
        "Pending amount: ₹10,000.00"
        in report
    )


    assert (
        "Failed amount: ₹10,000.00"
        in report
    )


# ============================================================
# EMPTY BATCH
# ============================================================

def test_empty_batch():

    metrics = calculate_batch_recovery_metrics(

        [],

        [],
    )


    assert (
        metrics["total_transactions"]
        == 0
    )


    assert (
        metrics["total_revenue"]
        == 0
    )


    assert (
        metrics["total_revenue_at_risk"]
        == 0
    )


    assert (
        metrics["recovered_amount"]
        == 0
    )


    assert (
        metrics["recovery_rate"]
        == 0
    )


    assert (
        metrics["unrecovered_amount"]
        == 0
    )