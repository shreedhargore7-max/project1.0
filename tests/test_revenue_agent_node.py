from app.revenue_recovery.agent_node import (
    parse_payment_records,
    analyze_revenue_recovery,
    build_revenue_recovery_answer,
    revenue_recovery_node,
)


def sample_payments():

    return [

        {
            "payment_id": "pay_AGENT001",
            "amount": 20000,
            "currency": "INR",
            "status": "failed",
            "failed_attempts": 4,
            "attempts": 5,
            "previous_successes": 6,
        },

        {
            "payment_id": "pay_AGENT002",
            "amount": 500,
            "currency": "INR",
            "status": "created",
            "failed_attempts": 0,
            "attempts": 1,
            "previous_successes": 0,
        },

    ]


def test_parse_payment_list():

    payments = sample_payments()

    result = parse_payment_records(
        payments
    )

    assert len(result) == 2


def test_analyze_revenue_recovery():

    result = analyze_revenue_recovery(
        sample_payments()
    )

    assert result["risk_results"]

    assert result["root_cause_results"]

    assert result["decisions"]

    assert result["prioritized_decisions"]


def test_build_answer():

    analysis = analyze_revenue_recovery(
        sample_payments()
    )

    answer = build_revenue_recovery_answer(
        analysis
    )

    assert (
        "Revenue Recovery Analysis"
        in answer
    )

    assert (
        "pay_AGENT001"
        in answer
    )

    assert (
        "20000"
        in answer
    )


def test_agent_node_with_supplied_data():

    state = {
        "question":
            "Which payments are at risk?",

        "recovery_payments":
            sample_payments(),

        "tool": "revenue_recovery",

        "tool_result": "",
    }

    result = revenue_recovery_node(
        state
    )

    assert (
        result["recovery_status"]
        == "ANALYZED"
    )

    assert result["tool_result"]

    assert (
        "Revenue Recovery Analysis"
        in result["tool_result"]
    )


def test_revenue_node_normalizes_and_enriches():

    payments = [
        {
            "id": "pay_INTEGRATION001",
            "customer_id": "cust_001",
            "amount": 20000,
            "currency": "INR",
            "status": "failed",
        },
        {
            "id": "pay_INTEGRATION002",
            "customer_id": "cust_001",
            "amount": 5000,
            "currency": "INR",
            "status": "captured",
        },
    ]

    state = {
        "question": "Which payments are at risk?",
        "recovery_payments": payments,
        "tool": "revenue_recovery",
        "tool_result": "",
    }

    result = revenue_recovery_node(
        state
    )

    assert (
        result["recovery_status"]
        == "ANALYZED"
    )

    enriched = result[
        "recovery_payments"
    ]

    assert len(enriched) == 2

    assert (
        enriched[0]["payment_id"]
        == "pay_INTEGRATION001"
    )

    assert (
        enriched[0]["attempts"]
        >= 2
    )

    assert (
        enriched[0]["previous_successes"]
        >= 1
    )


def test_revenue_node_uses_enriched_data_for_analysis():

    payments = [
        {
            "id": "pay_INTEGRATION003",
            "customer_id": "cust_002",
            "amount": 20000,
            "currency": "INR",
            "status": "failed",
        },
        {
            "id": "pay_INTEGRATION004",
            "customer_id": "cust_002",
            "amount": 15000,
            "currency": "INR",
            "status": "failed",
        },
        {
            "id": "pay_INTEGRATION005",
            "customer_id": "cust_002",
            "amount": 5000,
            "currency": "INR",
            "status": "captured",
        },
    ]

    state = {
        "question": "Which payments are at risk?",
        "recovery_payments": payments,
        "tool": "revenue_recovery",
        "tool_result": "",
    }

    result = revenue_recovery_node(
        state
    )

    decisions = result[
        "recovery_analysis"
    ][
        "decisions"
    ]

    assert decisions

    assert all(
        "payment_id" in item
        for item in decisions
    )


def test_revenue_recovery_follow_up():

    payments = [
        {
            "payment_id": "pay_DEMO007",
            "amount": 25000,
            "currency": "INR",
            "status": "failed",
            "failed_attempts": 5,
            "attempts": 6,
            "previous_successes": 8,
        }
    ]

    state = {
        "question": "Why is pay_DEMO007 risky?",
        "recovery_payments": payments,
        "tool": "revenue_recovery",
        "tool_result": "",
    }

    result = revenue_recovery_node(state)

    assert result["recovery_status"] == "ANALYZED"
    assert "pay_DEMO007" in result["tool_result"]
    assert "HIGH" in result["tool_result"]
    assert "100" in result["tool_result"]
    assert "failed" in result["tool_result"].lower()
