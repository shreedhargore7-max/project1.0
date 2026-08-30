# ============================================================
# TESTS - OUTCOME TRACKER
# ============================================================

from app.revenue_recovery.outcome_tracker import (
    OUTCOME_CREATED,
    OUTCOME_PENDING,
    OUTCOME_CAPTURED,
    OUTCOME_FAILED,
    OUTCOME_EXPIRED,
    OUTCOME_STOPPED,
    OUTCOME_REJECTED,
    classify_outcome_status,
    track_payment_outcome,
    track_batch_outcomes,
    calculate_outcome_metrics,
    build_outcome_summary,
)


# ============================================================
# STATUS CLASSIFICATION
# ============================================================

def test_captured_status_is_normalized():

    assert (
        classify_outcome_status("captured")
        == OUTCOME_CAPTURED
    )


def test_paid_status_is_captured():

    assert (
        classify_outcome_status("paid")
        == OUTCOME_CAPTURED
    )


def test_pending_status():

    assert (
        classify_outcome_status("pending")
        == OUTCOME_PENDING
    )


def test_created_status():

    # CREATED must remain distinct from PENDING.
    # A created recovery link does not mean that a
    # customer payment is already pending.

    assert (
        classify_outcome_status("created")
        == OUTCOME_CREATED
    )


def test_failed_status():

    assert (
        classify_outcome_status("failed")
        == OUTCOME_FAILED
    )


def test_expired_status_is_failed():

    assert (
        classify_outcome_status("expired")
        == OUTCOME_FAILED
    )


def test_stopped_status_is_failed():

    assert (
        classify_outcome_status("stopped")
        == OUTCOME_FAILED
    )


def test_rejected_status_is_failed():

    assert (
        classify_outcome_status("rejected")
        == OUTCOME_FAILED
    )


# ============================================================
# SINGLE OUTCOME
# ============================================================

def test_captured_payment_is_recovered():

    payment = {
        "payment_id": "pay_001",
        "amount": 20000,
    }

    result = track_payment_outcome(
        payment,
        "captured",
    )

    assert (
        result["payment_id"]
        == "pay_001"
    )

    assert (
        result["status"]
        == OUTCOME_CAPTURED
    )

    assert (
        result["recovered"]
        is True
    )

    assert (
        result["recovered_amount"]
        == 20000
    )


def test_created_payment_is_not_recovered():

    payment = {
        "payment_id": "pay_002",
        "amount": 10000,
    }

    result = track_payment_outcome(
        payment,
        "created",
    )

    # CREATED is not PENDING and is not RECOVERED.

    assert (
        result["status"]
        == OUTCOME_CREATED
    )

    assert (
        result["recovered"]
        is False
    )

    assert (
        result["recovered_amount"]
        == 0
    )


def test_failed_payment_is_not_recovered():

    payment = {
        "payment_id": "pay_003",
        "amount": 5000,
    }

    result = track_payment_outcome(
        payment,
        "failed",
    )

    assert (
        result["status"]
        == OUTCOME_FAILED
    )

    assert (
        result["recovered"]
        is False
    )

    assert (
        result["recovered_amount"]
        == 0
    )


# ============================================================
# BATCH TRACKING
# ============================================================

def test_batch_outcomes():

    payments = [

        {
            "payment_id": "pay_A",
            "amount": 20000,
        },

        {
            "payment_id": "pay_B",
            "amount": 10000,
        },

        {
            "payment_id": "pay_C",
            "amount": 5000,
        },
    ]

    outcomes = {

        "pay_A":
            "captured",

        "pay_B":
            "created",

        "pay_C":
            "failed",
    }

    result = track_batch_outcomes(
        payments,
        outcomes,
    )

    assert len(result) == 3

    by_id = {
        item["payment_id"]:
            item
        for item in result
    }

    assert (
        by_id["pay_A"]["recovered"]
        is True
    )

    assert (
        by_id["pay_B"]["status"]
        == OUTCOME_CREATED
    )

    assert (
        by_id["pay_B"]["recovered"]
        is False
    )

    assert (
        by_id["pay_C"]["status"]
        == OUTCOME_FAILED
    )


# ============================================================
# OUTCOME METRICS
# ============================================================

def test_outcome_metrics():

    outcomes = [

        {
            "payment_id": "pay_001",
            "amount": 20000,
            "status": "CAPTURED",
        },

        {
            "payment_id": "pay_002",
            "amount": 10000,
            "status": "PENDING",
        },

        {
            "payment_id": "pay_003",
            "amount": 5000,
            "status": "FAILED",
        },

        {
            "payment_id": "pay_004",
            "amount": 15000,
            "status": "CAPTURED",
        },
    ]

    metrics = calculate_outcome_metrics(
        outcomes,
        eligible_amount=50000,
    )

    assert (
        metrics["total_transactions"]
        == 4
    )

    assert (
        metrics["recovered_transactions"]
        == 2
    )

    assert (
        metrics["recovered_amount"]
        == 35000
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
        metrics["eligible_amount"]
        == 50000
    )

    assert (
        abs(
            metrics["recovery_rate"]
            - 0.7
        )
        < 0.0001
    )

    assert (
        metrics["unrecovered_amount"]
        == 15000
    )


# ============================================================
# LINK CREATION IS NOT RECOVERY
# ============================================================

def test_link_creation_is_not_recovery():

    outcomes = [

        {
            "payment_id": "pay_001",
            "amount": 25000,
            "status": OUTCOME_CREATED,
        }
    ]

    metrics = calculate_outcome_metrics(
        outcomes,
        eligible_amount=25000,
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
# EMPTY OUTCOMES
# ============================================================

def test_empty_outcomes():

    metrics = calculate_outcome_metrics(
        [],
        eligible_amount=0,
    )

    assert (
        metrics["total_transactions"]
        == 0
    )

    assert (
        metrics["recovered_transactions"]
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


# ============================================================
# SUMMARY
# ============================================================

def test_outcome_summary():

    metrics = {

        "total_transactions":
            100,

        "eligible_amount":
            100000,

        "recovered_transactions":
            25,

        "recovered_amount":
            60000,

        "recovery_rate":
            0.6,

        "created_transactions":
            10,

        "created_amount":
            10000,

        "pending_amount":
            20000,

        "failed_amount":
            20000,

        "unrecovered_amount":
            40000,
    }

    summary = build_outcome_summary(
        metrics
    )

    assert (
        "Transactions tracked: 100"
        in summary
    )

    assert (
        "₹100,000.00"
        in summary
    )

    assert (
        "Money recovered: ₹60,000.00"
        in summary
    )

    assert (
        "Recovery rate: 60.00%"
        in summary
    )

    assert (
        "Created transactions: 10"
        in summary
    )