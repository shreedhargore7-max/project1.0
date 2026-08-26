from app.revenue_recovery.history_enrichment import (
    build_history_key,
    build_history_summary,
    enrich_payment_history,
    calculate_batch_history_metrics,
)


def test_customer_history_key_uses_customer_id():

    payment = {
        "payment_id": "pay_001",
        "customer_id": "cust_001",
    }

    result = build_history_key(
        payment,
        0,
    )

    assert (
        result
        == "customer_id:cust_001"
    )


def test_customer_history_key_falls_back_to_payment():

    payment = {
        "payment_id": "pay_002",
    }

    result = build_history_key(
        payment,
        1,
    )

    assert (
        result
        == "payment:pay_002"
    )


def test_history_summary():

    payments = [
        {
            "payment_id": "pay_001",
            "customer_id": "cust_001",
            "amount": 10000,
            "status": "failed",
        },
        {
            "payment_id": "pay_002",
            "customer_id": "cust_001",
            "amount": 5000,
            "status": "captured",
        },
        {
            "payment_id": "pay_003",
            "customer_id": "cust_001",
            "amount": 3000,
            "status": "failed",
        },
    ]

    result = build_history_summary(
        payments
    )

    summary = result[
        "customer_id:cust_001"
    ]

    assert (
        summary["history_count"]
        == 3
    )

    assert (
        summary["attempts"]
        == 3
    )

    assert (
        summary["failed_attempts"]
        == 2
    )

    assert (
        summary["previous_successes"]
        == 1
    )


def test_history_failure_rate():

    payments = [
        {
            "payment_id": "pay_001",
            "customer_id": "cust_001",
            "amount": 1000,
            "status": "failed",
        },
        {
            "payment_id": "pay_002",
            "customer_id": "cust_001",
            "amount": 1000,
            "status": "failed",
        },
        {
            "payment_id": "pay_003",
            "customer_id": "cust_001",
            "amount": 1000,
            "status": "captured",
        },
        {
            "payment_id": "pay_004",
            "customer_id": "cust_001",
            "amount": 1000,
            "status": "captured",
        },
    ]

    result = build_history_summary(
        payments
    )

    summary = result[
        "customer_id:cust_001"
    ]

    assert (
        summary["failure_rate"]
        == 0.5
    )


def test_enrich_payment_history():

    payments = [
        {
            "payment_id": "pay_001",
            "customer_id": "cust_001",
            "amount": 10000,
            "status": "failed",
        },
        {
            "payment_id": "pay_002",
            "customer_id": "cust_001",
            "amount": 5000,
            "status": "captured",
        },
        {
            "payment_id": "pay_003",
            "customer_id": "cust_001",
            "amount": 3000,
            "status": "failed",
        },
    ]

    result = enrich_payment_history(
        payments
    )

    assert len(result) == 3

    assert (
        result[0]["attempts"]
        == 3
    )

    assert (
        result[0]["failed_attempts"]
        == 2
    )

    assert (
        result[0]["previous_successes"]
        == 1
    )

    assert (
        result[0]["history_count"]
        == 3
    )

    assert (
        result[0]["failure_rate"]
        == 0.6667
    )


def test_existing_derived_values_are_preserved():

    payments = [
        {
            "payment_id": "pay_001",
            "customer_id": "cust_001",
            "amount": 10000,
            "status": "failed",
            "attempts": 5,
            "failed_attempts": 4,
            "previous_successes": 7,
        },
        {
            "payment_id": "pay_002",
            "customer_id": "cust_001",
            "amount": 5000,
            "status": "captured",
        },
    ]

    result = enrich_payment_history(
        payments
    )

    assert (
        result[0]["attempts"]
        >= 5
    )

    assert (
        result[0]["failed_attempts"]
        >= 4
    )

    assert (
        result[0]["previous_successes"]
        >= 7
    )


def test_customers_are_kept_separate():

    payments = [
        {
            "payment_id": "pay_001",
            "customer_id": "cust_001",
            "amount": 1000,
            "status": "failed",
        },
        {
            "payment_id": "pay_002",
            "customer_id": "cust_002",
            "amount": 2000,
            "status": "captured",
        },
    ]

    result = build_history_summary(
        payments
    )

    assert len(result) == 2

    assert (
        result[
            "customer_id:cust_001"
        ]["failed_attempts"]
        == 1
    )

    assert (
        result[
            "customer_id:cust_002"
        ]["previous_successes"]
        == 1
    )


def test_anonymous_payments_do_not_merge():

    payments = [
        {
            "payment_id": "pay_001",
            "amount": 1000,
            "status": "failed",
        },
        {
            "payment_id": "pay_002",
            "amount": 1000,
            "status": "captured",
        },
    ]

    result = build_history_summary(
        payments
    )

    assert len(result) == 2


def test_batch_history_metrics():

    payments = [
        {
            "payment_id": "pay_001",
            "customer_id": "cust_001",
            "amount": 1000,
            "status": "failed",
        },
        {
            "payment_id": "pay_002",
            "customer_id": "cust_001",
            "amount": 1000,
            "status": "captured",
        },
    ]

    result = calculate_batch_history_metrics(
        payments
    )

    assert (
        result["total_payments"]
        == 2
    )

    assert (
        result["total_attempts"]
        == 2
    )

    assert (
        result["total_failed_attempts"]
        == 1
    )

    assert (
        result["total_successes"]
        == 1
    )

    assert (
        result["failure_rate"]
        == 0.5
    )


def test_empty_batch_metrics():

    result = calculate_batch_history_metrics(
        []
    )

    assert (
        result["total_payments"]
        == 0
    )

    assert (
        result["total_attempts"]
        == 0
    )

    assert (
        result["total_failed_attempts"]
        == 0
    )

    assert (
        result["total_successes"]
        == 0
    )

    assert (
        result["failure_rate"]
        == 0.0
    )