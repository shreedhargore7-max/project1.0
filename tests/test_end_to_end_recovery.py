from app.revenue_recovery.end_to_end import (
    analyze_recovery_request,
    select_top_opportunity,
    build_top_approval_request,
    run_end_to_end_recovery,
)


def sample_payments():

    return [
        {
            "payment_id": "pay_E2E001",
            "amount": 20000,
            "currency": "INR",
            "status": "failed",
            "failed_attempts": 4,
            "attempts": 5,
            "previous_successes": 6,
        },
        {
            "payment_id": "pay_E2E002",
            "amount": 500,
            "currency": "INR",
            "status": "created",
            "failed_attempts": 0,
            "attempts": 1,
            "previous_successes": 0,
        },
    ]


def test_end_to_end_analysis():

    result = analyze_recovery_request(
        sample_payments()
    )

    assert result["risk_results"]

    assert result["root_cause_results"]

    assert result["decisions"]


def test_top_opportunity():

    analysis = analyze_recovery_request(
        sample_payments()
    )

    top = select_top_opportunity(
        analysis
    )

    assert top is not None

    assert (
        top["payment_id"]
        == "pay_E2E001"
    )


def test_approval_request():

    analysis = analyze_recovery_request(
        sample_payments()
    )

    approval = build_top_approval_request(
        sample_payments(),
        analysis,
    )

    assert approval is not None

    assert (
        approval["payment_id"]
        == "pay_E2E001"
    )

    assert (
        approval["requires_approval"]
        is True
    )


def test_rejected_end_to_end():

    result = run_end_to_end_recovery(
        sample_payments(),
        approved=False,
        dry_run=True,
    )

    assert (
        result["approval"]["approved"]
        is False
    )

    assert (
        result["execution"]
        is not None
    )

    assert (
        result["execution"]["executed"]
        is False
    )


def test_approved_dry_run():

    result = run_end_to_end_recovery(
        sample_payments(),
        approved=True,
        dry_run=True,
    )

    assert (
        result["approval"]["approved"]
        is True
    )

    assert (
        result["execution"]["mode"]
        == "dry_run"
    )

    assert (
        result["execution"]["executed"]
        is False
    )


def test_mock_live_execution():

    calls = []

    def mock_executor(
        payment,
        action,
    ):

        calls.append({
            "payment_id":
                payment["payment_id"],
            "action":
                action,
        })

        return {
            "success": True,
            "executed": True,
            "mode": "mock_live",
        }

    result = run_end_to_end_recovery(
        sample_payments(),
        approved=True,
        dry_run=False,
        executor=mock_executor,
    )

    assert (
        result["execution"]["executed"]
        is True
    )

    assert (
        result["execution"]["mode"]
        == "mock_live"
    )

    assert len(calls) == 1

    assert (
        calls[0]["payment_id"]
        == "pay_E2E001"
    )