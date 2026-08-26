from app.revenue_recovery.root_cause import (
    CAUSE_PAYMENT_FAILURE,
    CAUSE_REPEATED_FAILURE,
    CAUSE_HIGH_VALUE,
    CAUSE_MANY_ATTEMPTS,
    CAUSE_CUSTOMER_HISTORY,
    find_root_causes,
    analyze_root_cause,
    analyze_root_causes,
    aggregate_root_causes,
    get_primary_root_cause,
    build_root_cause_summary,
)


def test_root_causes_for_failed_payment():

    payment = {
        "payment_id": "pay_ROOT001",
        "amount": 20000,
        "status": "failed",
        "failed_attempts": 4,
        "attempts": 5,
        "previous_successes": 6,
    }

    causes = find_root_causes(
        payment
    )

    assert CAUSE_PAYMENT_FAILURE in causes
    assert CAUSE_REPEATED_FAILURE in causes
    assert CAUSE_HIGH_VALUE in causes
    assert CAUSE_MANY_ATTEMPTS in causes
    assert CAUSE_CUSTOMER_HISTORY in causes


def test_analyze_single_payment():

    payment = {
        "payment_id": "pay_ROOT002",
        "amount": 15000,
        "status": "failed",
        "failed_attempts": 2,
        "attempts": 3,
        "previous_successes": 4,
    }

    result = analyze_root_cause(
        payment
    )

    assert (
        result["payment_id"]
        == "pay_ROOT002"
    )

    assert result["root_causes"]

    assert result["explanations"]


def test_batch_root_cause_analysis():

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
            "status": "failed",
            "failed_attempts": 1,
            "attempts": 1,
            "previous_successes": 0,
        },

    ]

    results = analyze_root_causes(
        payments
    )

    assert len(results) == 2


def test_root_cause_aggregation():

    results = [

        {
            "root_causes": [
                CAUSE_PAYMENT_FAILURE,
                CAUSE_REPEATED_FAILURE,
            ]
        },

        {
            "root_causes": [
                CAUSE_PAYMENT_FAILURE,
            ]
        },

        {
            "root_causes": [
                CAUSE_HIGH_VALUE,
            ]
        },

    ]

    aggregated = aggregate_root_causes(
        results
    )

    assert (
        aggregated[CAUSE_PAYMENT_FAILURE]
        == 2
    )

    assert (
        aggregated[CAUSE_REPEATED_FAILURE]
        == 1
    )

    assert (
        aggregated[CAUSE_HIGH_VALUE]
        == 1
    )


def test_primary_root_cause():

    causes = [
        CAUSE_HIGH_VALUE,
        CAUSE_REPEATED_FAILURE,
        CAUSE_MANY_ATTEMPTS,
    ]

    primary = get_primary_root_cause(
        causes
    )

    assert (
        primary
        == CAUSE_REPEATED_FAILURE
    )


def test_root_cause_summary():

    results = [

        {
            "root_causes": [
                CAUSE_PAYMENT_FAILURE,
                CAUSE_REPEATED_FAILURE,
            ]
        },

        {
            "root_causes": [
                CAUSE_PAYMENT_FAILURE,
            ]
        },

    ]

    summary = build_root_cause_summary(
        results
    )

    assert (
        summary["total_transactions"]
        == 2
    )

    assert (
        summary["root_cause_counts"][
            CAUSE_PAYMENT_FAILURE
        ]
        == 2
    )

    assert (
        summary["primary_root_cause"]
        == CAUSE_PAYMENT_FAILURE
    )