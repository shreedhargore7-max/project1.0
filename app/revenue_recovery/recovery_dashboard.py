# ============================================================
# REVENUE RECOVERY - STREAMLIT DASHBOARD
# ============================================================

import streamlit as st


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# BUILD DASHBOARD METRICS
# ============================================================

def build_recovery_dashboard_metrics(
    analysis: dict,
) -> dict:

    if not isinstance(
        analysis,
        dict,
    ):
        return {
            "total_transactions": 0,
            "total_revenue": 0.0,
            "revenue_at_risk": 0.0,
            "high_risk": 0,
            "medium_risk": 0,
            "eligible_transactions": 0,
            "eligible_amount": 0.0,
            "approval_required": 0,
            "manual_review": 0,
            "recovery_review": 0,
        }

    risk_results = analysis.get(
        "risk_results",
        [],
    )

    decisions = analysis.get(
        "prioritized_decisions",
        analysis.get(
            "decisions",
            [],
        ),
    )

    payments = analysis.get(
        "payments",
        [],
    )

    # --------------------------------------------------------
    # Payment totals
    # --------------------------------------------------------

    total_transactions = len(
        payments
    )

    total_revenue = sum(
        _safe_float(
            payment.get(
                "amount",
                0,
            )
        )
        for payment in payments
        if isinstance(
            payment,
            dict,
        )
    )

    # --------------------------------------------------------
    # Risk metrics
    # --------------------------------------------------------

    high_risk = 0
    medium_risk = 0
    revenue_at_risk = 0.0

    for result in risk_results:

        if not isinstance(
            result,
            dict,
        ):
            continue

        level = str(
            result.get(
                "risk_level",
                "",
            )
        ).upper()

        amount = _safe_float(
            result.get(
                "revenue_at_risk",
                0,
            )
        )

        if level == "HIGH":

            high_risk += 1
            revenue_at_risk += amount

        elif level == "MEDIUM":

            medium_risk += 1

    # --------------------------------------------------------
    # Decision metrics
    # --------------------------------------------------------

    eligible_transactions = 0
    eligible_amount = 0.0

    approval_required = 0
    manual_review = 0
    recovery_review = 0

    for decision in decisions:

        if not isinstance(
            decision,
            dict,
        ):
            continue

        action = str(
            decision.get(
                "action",
                "",
            )
        ).upper()

        amount = _safe_float(
            decision.get(
                "amount",
                0,
            )
        )

        requires_approval = bool(
            decision.get(
                "requires_approval",
                False,
            )
        )

        if action in {
            "MANUAL_REVIEW",
            "RECOVERY_REVIEW",
        }:

            eligible_transactions += 1
            eligible_amount += amount

        if requires_approval:

            approval_required += 1

        if action == "MANUAL_REVIEW":

            manual_review += 1

        elif action == "RECOVERY_REVIEW":

            recovery_review += 1

    return {
        "total_transactions":
            total_transactions,

        "total_revenue":
            round(
                total_revenue,
                2,
            ),

        "revenue_at_risk":
            round(
                revenue_at_risk,
                2,
            ),

        "high_risk":
            high_risk,

        "medium_risk":
            medium_risk,

        "eligible_transactions":
            eligible_transactions,

        "eligible_amount":
            round(
                eligible_amount,
                2,
            ),

        "approval_required":
            approval_required,

        "manual_review":
            manual_review,

        "recovery_review":
            recovery_review,
    }


# ============================================================
# DISPLAY KPI CARDS
# ============================================================

def display_recovery_kpis(
    metrics: dict,
) -> None:

    st.subheader(
        "💰 Revenue Recovery Overview"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Transactions",
            f"{metrics.get('total_transactions', 0):,}",
        )

    with col2:

        st.metric(
            "Revenue",
            (
                f"₹"
                f"{metrics.get('total_revenue', 0):,.2f}"
            ),
        )

    with col3:

        st.metric(
            "Revenue at Risk",
            (
                f"₹"
                f"{metrics.get('revenue_at_risk', 0):,.2f}"
            ),
        )

    with col4:

        st.metric(
            "High Risk",
            f"{metrics.get('high_risk', 0):,}",
        )


# ============================================================
# DISPLAY RECOVERY STATUS
# ============================================================

def display_recovery_status(
    metrics: dict,
) -> None:

    st.subheader(
        "🛡️ Recovery Controls"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Recovery Eligible",
            f"{metrics.get('eligible_transactions', 0):,}",
        )

    with col2:

        st.metric(
            "Eligible Amount",
            (
                f"₹"
                f"{metrics.get('eligible_amount', 0):,.2f}"
            ),
        )

    with col3:

        st.metric(
            "Approval Required",
            f"{metrics.get('approval_required', 0):,}",
        )

    with col4:

        st.metric(
            "Medium Risk",
            f"{metrics.get('medium_risk', 0):,}",
        )


# ============================================================
# DISPLAY DECISION BREAKDOWN
# ============================================================

def display_decision_breakdown(
    metrics: dict,
) -> None:

    st.subheader(
        "📊 Recovery Decision Breakdown"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "Manual reviews"
        )

        st.progress(
            min(
                metrics.get(
                    "manual_review",
                    0,
                )
                / max(
                    metrics.get(
                        "eligible_transactions",
                        1,
                    ),
                    1,
                ),
                1.0,
            )
        )

        st.caption(
            (
                f"{metrics.get('manual_review', 0)} "
                "transaction(s)"
            )
        )

    with col2:

        st.write(
            "Recovery reviews"
        )

        st.progress(
            min(
                metrics.get(
                    "recovery_review",
                    0,
                )
                / max(
                    metrics.get(
                        "eligible_transactions",
                        1,
                    ),
                    1,
                ),
                1.0,
            )
        )

        st.caption(
            (
                f"{metrics.get('recovery_review', 0)} "
                "transaction(s)"
            )
        )


# ============================================================
# DISPLAY PRIORITY TABLE
# ============================================================

def display_priority_table(
    analysis: dict,
) -> None:

    prioritized = analysis.get(
        "prioritized_decisions",
        [],
    )

    if not prioritized:

        st.info(
            "No recovery opportunities are currently identified."
        )

        return

    st.subheader(
        "🎯 Recovery Priority Queue"
    )

    rows = []

    for item in prioritized[:10]:

        if not isinstance(
            item,
            dict,
        ):
            continue

        rows.append(
            {
                "Payment":
                    item.get(
                        "payment_id",
                        "unknown",
                    ),

                "Amount":
                    f"₹{_safe_float(item.get('amount', 0)):,.2f}",

                "Priority":
                    item.get(
                        "priority",
                        "UNKNOWN",
                    ),

                "Action":
                    item.get(
                        "action",
                        "UNKNOWN",
                    ),

                "Approval":
                    (
                        "YES"
                        if item.get(
                            "requires_approval",
                            False,
                        )
                        else "NO"
                    ),
            }
        )

    if rows:

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# DISPLAY FULL DASHBOARD
# ============================================================

def display_recovery_dashboard(
    analysis: dict,
) -> None:

    if not isinstance(
        analysis,
        dict,
    ):

        st.info(
            "Revenue recovery analysis is not available yet."
        )

        return

    metrics = build_recovery_dashboard_metrics(
        analysis
    )

    st.divider()

    display_recovery_kpis(
        metrics
    )

    display_recovery_status(
        metrics
    )

    display_decision_breakdown(
        metrics
    )

    display_priority_table(
        analysis
    )

    st.divider()