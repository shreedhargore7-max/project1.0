# ============================================================
# REVENUE RECOVERY - AGENT NODE
# ============================================================

import ast
import json
import re

from pathlib import Path
from typing import Any


from app.agent.mcp_tools import (
    mcp_razorpay_fetch_all_payments,
)


from app.revenue_recovery.risk_engine import (
    analyze_payments,
    build_risk_summary,
)


from app.revenue_recovery.root_cause import (
    analyze_root_causes,
    build_root_cause_summary,
)


from app.revenue_recovery.decision_engine import (
    decide_batch_actions,
    prioritize_decisions,
    build_decision_summary,
)


from app.revenue_recovery.payment_normalizer import (
    normalize_and_validate_payments,
)


from app.revenue_recovery.history_enrichment import (
    enrich_payment_history,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


SAMPLE_PAYMENTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "revenue_recovery"
    / "sample_payments.json"
)


# ============================================================
# LOAD DEMO PAYMENTS
# ============================================================

def load_sample_payments() -> list[dict]:
    """
    Load controlled demo payment data.

    This is used when available so the revenue-recovery
    engine has structured fields such as:

        payment_id
        amount
        status
        failed_attempts
        attempts
        previous_successes
    """

    if not SAMPLE_PAYMENTS_FILE.exists():

        return []

    try:

        with SAMPLE_PAYMENTS_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        if not isinstance(
            data,
            list,
        ):

            return []

        return [
            item
            for item in data
            if isinstance(
                item,
                dict,
            )
        ]

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):

        return []


# ============================================================
# PARSE MCP RESULT
# ============================================================

def parse_payment_records(
    raw_result: Any,
) -> list[dict]:

    """
    Convert the Razorpay MCP response into a list of
    payment dictionaries.

    The parser fails safely when the response format
    is unknown.
    """

    if raw_result is None:

        return []


    # --------------------------------------------------------
    # ALREADY A LIST
    # --------------------------------------------------------

    if isinstance(
        raw_result,
        list,
    ):

        return [
            item
            for item in raw_result
            if isinstance(
                item,
                dict,
            )
        ]


    # --------------------------------------------------------
    # DICTIONARY
    # --------------------------------------------------------

    if isinstance(
        raw_result,
        dict,
    ):

        for key in (
            "items",
            "data",
            "payments",
            "results",
        ):

            value = raw_result.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return [
                    item
                    for item in value
                    if isinstance(
                        item,
                        dict,
                    )
                ]


        return [
            raw_result
        ]


    # --------------------------------------------------------
    # NON-STRING
    # --------------------------------------------------------

    if not isinstance(
        raw_result,
        str,
    ):

        return []


    text = raw_result.strip()


    if not text:

        return []


    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    try:

        parsed = json.loads(
            text
        )

        return parse_payment_records(
            parsed
        )

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):

        pass


    # --------------------------------------------------------
    # PYTHON LITERAL
    # --------------------------------------------------------

    try:

        parsed = ast.literal_eval(
            text
        )

        return parse_payment_records(
            parsed
        )

    except (
        ValueError,
        SyntaxError,
        TypeError,
    ):

        return []


# ============================================================
# RUN REVENUE ANALYSIS
# ============================================================

def analyze_revenue_recovery(
    payments: list[dict],
) -> dict:

    """
    Run the complete revenue-recovery analytical pipeline.

    No external write operation is performed here.
    """

    risk_results = analyze_payments(
        payments
    )


    root_cause_results = analyze_root_causes(
        payments
    )


    decisions = decide_batch_actions(
        payments,
        risk_results,
        root_cause_results,
    )


    prioritized = prioritize_decisions(
        decisions
    )


    return {

        "payments":
            payments,

        "risk_results":
            risk_results,

        "risk_summary":
            build_risk_summary(
                risk_results
            ),

        "root_cause_results":
            root_cause_results,

        "root_cause_summary":
            build_root_cause_summary(
                root_cause_results
            ),

        "decisions":
            decisions,

        "prioritized_decisions":
            prioritized,

        "decision_summary":
            build_decision_summary(
                decisions
            ),
    }


# ============================================================
# USER-FACING SUMMARY
# ============================================================

def build_revenue_recovery_answer(
    analysis: dict,
) -> str:

    risk_summary = analysis.get(
        "risk_summary",
        {},
    )


    decision_summary = analysis.get(
        "decision_summary",
        {},
    )


    prioritized = analysis.get(
        "prioritized_decisions",
        [],
    )


    total_transactions = (
        risk_summary.get(
            "total_transactions",
            0,
        )
    )


    high_risk = (
        risk_summary.get(
            "high_risk_transactions",
            0,
        )
    )


    medium_risk = (
        risk_summary.get(
            "medium_risk_transactions",
            0,
        )
    )


    revenue_at_risk = (
        risk_summary.get(
            "total_revenue_at_risk",
            0,
        )
    )


    lines = [

        "## Revenue Recovery Analysis",

        "",

        f"Transactions analyzed: "
        f"{total_transactions}",

        f"High-risk transactions: "
        f"{high_risk}",

        f"Medium-risk transactions: "
        f"{medium_risk}",

        f"Potential revenue at risk: "
        f"₹{revenue_at_risk}",

        "",

    ]


    # --------------------------------------------------------
    # PRIORITY OPPORTUNITIES
    # --------------------------------------------------------

    if prioritized:

        lines.append(
            "### Priority opportunities"
        )


        shown = 0


        for item in prioritized:

            if shown >= 5:

                break


            priority = item.get(
                "priority",
                "UNKNOWN",
            )


            action = item.get(
                "action",
                "UNKNOWN",
            )


            payment_id = item.get(
                "payment_id",
                "unknown",
            )


            amount = item.get(
                "amount",
                0,
            )


            approval = item.get(
                "requires_approval",
                False,
            )


            lines.append(

                f"- `{payment_id}` — "
                f"₹{amount} — "
                f"Priority: **{priority}** — "
                f"Action: **{action}** — "
                f"Approval required: **{approval}**"

            )


            shown += 1


    else:

        lines.append(
            "No recovery opportunities were identified."
        )


    lines.extend([

        "",

        f"High-priority decisions: "
        f"{decision_summary.get('high_priority', 0)}",

        f"Recovery reviews: "
        f"{decision_summary.get('recovery_review', 0)}",

        f"Manual reviews: "
        f"{decision_summary.get('manual_review', 0)}",

    ])


    return "\n".join(
        lines
    )


# ============================================================
# GET PAYMENT DATA
# ============================================================

def get_recovery_payment_data() -> tuple[
    list[dict],
    str,
]:
    """
    Prefer structured demo data.

    Fall back to live Razorpay payment data if the
    demo dataset does not exist.
    """

    # --------------------------------------------------------
    # DEMO DATA FIRST
    # --------------------------------------------------------

    sample_payments = (
        load_sample_payments()
    )


    if sample_payments:

        return (
            sample_payments,
            "demo",
        )


    # --------------------------------------------------------
    # LIVE RAZORPAY FALLBACK
    # --------------------------------------------------------

    try:

        raw_result = (
            mcp_razorpay_fetch_all_payments(
                count=100,
                skip=0,
            )
        )


        payments = parse_payment_records(
            raw_result
        )


        return (
            payments,
            "razorpay",
        )


    except Exception:

        return (
            [],
            "razorpay",
        )


# ============================================================
# FIND HIGHEST PRIORITY PAYMENT
# ============================================================

def get_highest_priority_payment(
    analysis: dict,
) -> dict | None:

    prioritized = analysis.get(
        "prioritized_decisions",
        [],
    )


    if not prioritized:

        return None


    return prioritized[0]


# ============================================================
# LANGGRAPH NODE
# ============================================================

def revenue_recovery_node(
    state: dict,
) -> dict:

    question = state.get(
        "question",
        "",
    )


    # --------------------------------------------------------
    # SUPPLIED TEST DATA
    # --------------------------------------------------------

    supplied_payments = state.get(
        "recovery_payments"
    )


    if isinstance(
        supplied_payments,
        list,
    ):

        payments = [
            payment
            for payment in supplied_payments
            if isinstance(
                payment,
                dict,
            )
        ]

        data_source = "supplied"

    else:

        payments, data_source = (
            get_recovery_payment_data()
        )


    # --------------------------------------------------------
    # NO DATA
    # --------------------------------------------------------

    if not payments:

        state["tool_result"] = (
            "I couldn't find structured payment "
            "records to analyze for revenue recovery."
        )

        state["recovery_status"] = (
            "NO_DATA"
        )

        return state


    # --------------------------------------------------------
    # NORMALIZE PAYMENT DATA
    # --------------------------------------------------------

    try:

        normalized_payments = (
            normalize_and_validate_payments(
                payments
            )
        )

        if not normalized_payments:

            state["tool_result"] = (
                "I couldn't find valid structured payment "
                "records for revenue recovery analysis."
            )

            state["recovery_status"] = (
                "NO_VALID_DATA"
            )

            return state


        # ----------------------------------------------------
        # HISTORICAL ENRICHMENT
        # ----------------------------------------------------

        enriched_payments = (
            enrich_payment_history(
                normalized_payments
            )
        )


        # ----------------------------------------------------
        # ANALYSIS
        # ----------------------------------------------------

        analysis = analyze_revenue_recovery(
            enriched_payments
        )


        state[
            "recovery_analysis"
        ] = analysis

        state[
            "recovery_payments"
        ] = enriched_payments


        # ----------------------------------------------------
        # SPECIFIC REVENUE-RECOVERY PAYMENT EXPLANATION
        # ----------------------------------------------------

        q = question.lower()

        payment_id_match = re.search(
            r"\bpay_[A-Za-z0-9]+\b",
            question,
        )

        explain_risk_request = (
            payment_id_match is not None
            and any(
                phrase in q
                for phrase in [
                    "why is",
                    "why does",
                    "why was",
                    "why is this risky",
                    "why is it risky",
                    "risk reason",
                    "risk reasons",
                    "explain this payment",
                    "explain the payment",
                    "tell me about this payment",
                    "what is wrong with",
                    "what's wrong with",
                ]
            )
        )

        if explain_risk_request:

            requested_payment_id = payment_id_match.group(0)

            matching_risk = next(
                (
                    item
                    for item in analysis.get("risk_results", [])
                    if item.get("payment_id") == requested_payment_id
                ),
                None,
            )

            if matching_risk is None:

                state["tool_result"] = (
                    f"I couldn't find `{requested_payment_id}` in the "
                    "current revenue-recovery analysis."
                )

                state["recovery_status"] = "PAYMENT_NOT_FOUND_IN_ANALYSIS"
                state["last_tool_result"] = state["tool_result"]
                state["recovery_data_source"] = data_source
                return state

            reasons = matching_risk.get("reasons", [])

            if not isinstance(reasons, list):
                reasons = [str(reasons)] if reasons else []

            lines = [
                f"### Why `{requested_payment_id}` is risky",
                "",
                f"**Risk level:** **{matching_risk.get('risk_level', 'UNKNOWN')}**",
                f"**Risk score:** **{matching_risk.get('risk_score', 0)}**",
                f"**Amount:** ₹{matching_risk.get('amount', 0)}",
                f"**Revenue at risk:** ₹{matching_risk.get('revenue_at_risk', 0)}",
                "",
                "**Reasons:**",
            ]

            if reasons:
                lines.extend(
                    f"- {reason}"
                    for reason in reasons
                )
            else:
                lines.append("- No detailed risk reasons were recorded.")

            state["tool_result"] = "\n".join(lines)
            state["last_tool_result"] = state["tool_result"]
            state["recovery_status"] = "ANALYZED"
            state["recovery_data_source"] = data_source
            return state

        # ----------------------------------------------------
        # HIGHEST-PRIORITY RECOVERY REQUEST
        # ----------------------------------------------------


        recovery_request = any(

            phrase in q

            for phrase in [

                "recover the highest-priority payment",

                "recover the highest priority payment",

                "recover the top payment",

                "recover the most risky payment",

                "recover the highest risk payment",

            ]

        )


        if recovery_request:

            top = (
                get_highest_priority_payment(
                    analysis
                )
            )


            if top is None:

                state["tool_result"] = (
                    "I couldn't identify a recovery "
                    "opportunity."
                )

                state["recovery_status"] = (
                    "NO_OPPORTUNITY"
                )

                return state


            payment_id = top.get(
                "payment_id",
                "unknown",
            )


            amount = top.get(
                "amount",
                0,
            )


            priority = top.get(
                "priority",
                "UNKNOWN",
            )


            action = top.get(
                "action",
                "UNKNOWN",
            )


            approval = top.get(
                "requires_approval",
                True,
            )


            state["tool_result"] = (

                "### Highest-Priority Recovery\n\n"

                f"**Payment:** `{payment_id}`\n\n"

                f"**Amount:** ₹{amount}\n\n"

                f"**Priority:** **{priority}**\n\n"

                f"**Recommended action:** "
                f"**{action}**\n\n"

                f"**Approval required:** "
                f"**{approval}**\n\n"

                "The recovery action will not be executed "
                "automatically. Explicit user approval is "
                "required."

            )


        else:

            state["tool_result"] = (
                build_revenue_recovery_answer(
                    analysis
                )
            )


        state["last_tool_result"] = (
            state["tool_result"]
        )


        state["recovery_status"] = (
            "ANALYZED"
        )


        state["recovery_data_source"] = (
            data_source
        )


    except Exception as error:

        state["tool_result"] = (
            "Revenue recovery analysis failed: "
            f"{error}"
        )


        state["recovery_status"] = (
            "FAILED"
        )


    return state


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "SAMPLE_PAYMENTS_FILE",

    "load_sample_payments",

    "parse_payment_records",

    "analyze_revenue_recovery",

    "build_revenue_recovery_answer",

    "get_recovery_payment_data",

    "get_highest_priority_payment",

    "revenue_recovery_node",

]