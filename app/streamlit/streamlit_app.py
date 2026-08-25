import os
import sys
import re
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# OBSERVABILITY
# ============================================================

from app.monitoring.logger import (
    create_request_id,
    log_event,
)


# ============================================================
# UNIFIED AGENT
# ============================================================

from app.agent.unified_agent import graph


# ============================================================
# RAZORPAY MCP WRITE TOOLS
# ============================================================

from app.agent.mcp_tools import (
    mcp_razorpay_create_order,
    mcp_razorpay_create_payment_link,
    mcp_razorpay_create_refund,
    mcp_razorpay_update_order,
    mcp_razorpay_update_payment,
    mcp_razorpay_update_refund,
    mcp_razorpay_update_payment_link,
    mcp_razorpay_payment_link_notify,
    mcp_razorpay_payment_link_upi_create,
    mcp_razorpay_create_qr_code,
    mcp_razorpay_capture_payment,
    mcp_razorpay_initiate_payment,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Intelligent AI Assistant",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🤖 Intelligent AI Assistant"
)

st.caption(
    "Memory • PDF RAG • Chat History • Razorpay MCP • AI"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_razorpay_action" not in st.session_state:
    st.session_state.pending_razorpay_action = None

if "last_razorpay_result" not in st.session_state:
    st.session_state.last_razorpay_result = ""

if "previous_tool" not in st.session_state:
    st.session_state.previous_tool = ""

if "current_request_id" not in st.session_state:
    st.session_state.current_request_id = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ Chat Controls"
    )

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.pending_razorpay_action = None

        st.session_state.last_razorpay_result = ""

        st.session_state.previous_tool = ""

        st.rerun()

    st.divider()

    st.subheader(
        "🧠 Agent Capabilities"
    )

    st.write(
        "🧠 Long-term Memory"
    )

    st.write(
        "📄 PDF RAG"
    )

    st.write(
        "💬 Chat History"
    )

    st.write(
        "💳 Razorpay MCP"
    )

    st.write(
        "✨ General AI"
    )

    st.divider()

    if st.session_state.pending_razorpay_action:

        st.warning(
            "⚠️ Razorpay action is waiting for confirmation."
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and message.get("tool")
        ):

            st.caption(
                f"🔧 Tool used: {message['tool']}"
            )


# ============================================================
# CHAT HISTORY
# ============================================================

def get_chat_history():

    history = []

    for message in st.session_state.messages:

        role = message["role"]

        content = message["content"]

        if role == "user":

            history.append(
                f"user: {content}"
            )

        elif role == "assistant":

            history.append(
                f"assistant: {content}"
            )

    return "\n".join(history)


# ============================================================
# HELPER: EXTRACT AMOUNT
# ============================================================

def extract_amount(text):

    patterns = [

        r"(?:₹|rs\.?|inr)\s*([0-9]+(?:\.[0-9]+)?)",

        r"([0-9]+(?:\.[0-9]+)?)\s*(?:rupees|rs|inr)",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = float(
                match.group(1)
            )

            if value.is_integer():

                return int(value)

            return value

    return None


# ============================================================
# HELPER: EXTRACT ORDER ID
# ============================================================

def extract_order_id(text):

    match = re.search(
        r"order_[A-Za-z0-9]+",
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(0)

    return None


# ============================================================
# HELPER: EXTRACT PAYMENT ID
# ============================================================

def extract_payment_id(text):

    match = re.search(
        r"pay_[A-Za-z0-9]+",
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(0)

    return None


# ============================================================
# HELPER: EXTRACT REFUND ID
# ============================================================

def extract_refund_id(text):

    match = re.search(
        r"rfnd_[A-Za-z0-9]+",
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(0)

    return None


# ============================================================
# HELPER: EXTRACT PAYMENT LINK ID
# ============================================================

def extract_payment_link_id(text):

    match = re.search(
        r"plink_[A-Za-z0-9]+",
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(0)

    return None


# ============================================================
# HELPER: EXTRACT RECEIPT
# ============================================================

def extract_receipt(text):

    match = re.search(
        r"(?:receipt)\s*(?:is|=)?\s*([A-Za-z0-9_-]+)",
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(1)

    return None


# ============================================================
# HELPER: EXTRACT DESCRIPTION
# ============================================================

def extract_description(text):

    quoted = re.search(
        r'["\']([^"\']+)["\']',
        text
    )

    if quoted:

        return quoted.group(1)

    match = re.search(
        r"(?:description|for)\s+(.+?)(?:\s+with\s+receipt|\s*$)",
        text,
        re.IGNORECASE
    )

    if match:

        description = match.group(1).strip()

        description = re.sub(
            r"\s+for testing$",
            "",
            description,
            flags=re.IGNORECASE
        )

        if description:

            return description

    return "Testing payment"


# ============================================================
# RAZORPAY WRITE ACTION DETECTOR
# ============================================================

def detect_razorpay_write_action(question):

    q = question.lower().strip()


    # ========================================================
    # CREATE ORDER
    # ========================================================

    if (
        "create" in q
        and "order" in q
    ):

        amount = extract_amount(
            question
        )

        receipt = extract_receipt(
            question
        )

        if amount is None:

            return {
                "error": "Please provide the order amount."
            }

        return {

            "tool": "create_order",

            "arguments": {
                "amount": amount,
                "currency": "INR",
                "receipt": receipt,
            },

            "label": "Create Razorpay Order",
        }


    # ========================================================
    # CREATE PAYMENT LINK
    # ========================================================

    if (
        (
            "create" in q
            and "payment link" in q
        )
        or
        (
            "generate" in q
            and "payment link" in q
        )
    ):

        amount = extract_amount(
            question
        )

        if amount is None:

            return {
                "error": (
                    "Please provide the payment-link amount."
                )
            }

        description = extract_description(
            question
        )

        return {

            "tool": "create_payment_link",

            "arguments": {
                "amount": amount,
                "currency": "INR",
                "description": description,
            },

            "label": "Create Razorpay Payment Link",
        }


    # ========================================================
    # CREATE REFUND
    # ========================================================

    if (
        "create refund" in q
        or "issue refund" in q
        or "refund payment" in q
    ):

        payment_id = extract_payment_id(
            question
        )

        if not payment_id:

            return {
                "error": (
                    "Please provide the Razorpay payment ID "
                    "for the refund."
                )
            }

        amount = extract_amount(
            question
        )

        arguments = {
            "payment_id": payment_id
        }

        if amount is not None:

            arguments["amount"] = amount

        return {

            "tool": "create_refund",

            "arguments": arguments,

            "label": "Create Razorpay Refund",
        }


    # ========================================================
    # UPDATE ORDER
    # ========================================================

    if (
        "update order" in q
        or "modify order" in q
    ):

        order_id = extract_order_id(
            question
        )

        if not order_id:

            return {
                "error": (
                    "Please provide the Razorpay order ID."
                )
            }

        note_match = re.search(
            r"(?:note|notes)\s+(?:saying|is|to)?\s*[\"']?(.+?)[\"']?$",
            question,
            re.IGNORECASE
        )

        if note_match:

            note = note_match.group(1).strip()

        else:

            note = "Updated by AI assistant"

        return {

            "tool": "update_order",

            "arguments": {

                "order_id": order_id,

                "notes": {
                    "test": note
                },

            },

            "label": "Update Razorpay Order",
        }


    # ========================================================
    # UPDATE PAYMENT
    # ========================================================

    if (
        "update payment" in q
        or "modify payment" in q
    ):

        payment_id = extract_payment_id(
            question
        )

        if not payment_id:

            return {
                "error": (
                    "Please provide the Razorpay payment ID."
                )
            }

        note_match = re.search(
            r"(?:note|notes)\s+(?:saying|is|to)?\s*[\"']?(.+?)[\"']?$",
            question,
            re.IGNORECASE
        )

        if note_match:

            note = note_match.group(1).strip()

        else:

            note = "Updated by AI assistant"

        return {

            "tool": "update_payment",

            "arguments": {

                "payment_id": payment_id,

                "notes": {
                    "test": note
                },

            },

            "label": "Update Razorpay Payment",
        }


    # ========================================================
    # UPDATE REFUND
    # ========================================================

    if (
        "update refund" in q
        or "modify refund" in q
    ):

        refund_id = extract_refund_id(
            question
        )

        if not refund_id:

            return {
                "error": (
                    "Please provide the Razorpay refund ID."
                )
            }

        return {

            "tool": "update_refund",

            "arguments": {

                "refund_id": refund_id,

                "notes": {
                    "test": "Updated by AI assistant"
                },

            },

            "label": "Update Razorpay Refund",
        }


    # ========================================================
    # UPDATE PAYMENT LINK
    # ========================================================

    if (
        "update payment link" in q
        or "modify payment link" in q
    ):

        payment_link_id = extract_payment_link_id(
            question
        )

        if not payment_link_id:

            return {
                "error": (
                    "Please provide the Razorpay payment "
                    "link ID."
                )
            }

        reference_match = re.search(
            r"(?:reference id|reference)\s*(?:is|=)?\s*([A-Za-z0-9_-]+)",
            question,
            re.IGNORECASE
        )

        arguments = {

            "payment_link_id":
                payment_link_id

        }

        if reference_match:

            arguments["reference_id"] = (
                reference_match.group(1)
            )

        return {

            "tool": "update_payment_link",

            "arguments": arguments,

            "label": "Update Razorpay Payment Link",
        }


    # ========================================================
    # PAYMENT LINK NOTIFICATION
    # ========================================================

    if (
        (
            "notify" in q
            and "payment link" in q
        )
        or
        "send payment link" in q
    ):

        payment_link_id = extract_payment_link_id(
            question
        )

        if not payment_link_id:

            return {
                "error": (
                    "Please provide the Razorpay payment "
                    "link ID."
                )
            }

        medium = "sms"

        if "email" in q:

            medium = "email"

        elif "whatsapp" in q:

            medium = "whatsapp"

        return {

            "tool": "payment_link_notify",

            "arguments": {

                "payment_link_id":
                    payment_link_id,

                "medium":
                    medium,

            },

            "label":
                "Send Razorpay Payment Link Notification",
        }


    # ========================================================
    # CREATE UPI PAYMENT LINK
    # ========================================================

    if (
        "upi payment link" in q
        or "create upi link" in q
    ):

        amount = extract_amount(
            question
        )

        if amount is None:

            return {
                "error": (
                    "Please provide the UPI payment amount."
                )
            }

        return {

            "tool":
                "payment_link_upi_create",

            "arguments": {

                "amount":
                    amount,

                "currency":
                    "INR",

                "description":
                    extract_description(question),

            },

            "label":
                "Create Razorpay UPI Payment Link",
        }


    # ========================================================
    # CREATE QR
    # ========================================================

    if (
        "create qr" in q
        or "create a qr" in q
        or "generate qr" in q
    ):

        amount = extract_amount(
            question
        )

        if amount is None:

            return {
                "error": (
                    "Please provide the QR payment amount."
                )
            }

        return {

            "tool":
                "create_qr_code",

            "arguments": {

                "payment_amount":
                    amount,

                "description":
                    extract_description(question),

            },

            "label":
                "Create Razorpay QR Code",
        }


    # ========================================================
    # CAPTURE PAYMENT
    # ========================================================

    if (
        "capture payment" in q
        or "capture the payment" in q
    ):

        payment_id = extract_payment_id(
            question
        )

        amount = extract_amount(
            question
        )

        if not payment_id:

            return {
                "error":
                    "Please provide the payment ID."
            }

        if amount is None:

            return {
                "error":
                    "Please provide the capture amount."
            }

        return {

            "tool":
                "capture_payment",

            "arguments": {

                "payment_id":
                    payment_id,

                "amount":
                    amount,

                "currency":
                    "INR",

            },

            "label":
                "Capture Razorpay Payment",
        }


    # ========================================================
    # INITIATE PAYMENT
    # ========================================================

    if (
        "initiate payment" in q
        or "start payment" in q
    ):

        amount = extract_amount(
            question
        )

        order_id = extract_order_id(
            question
        )

        if amount is None:

            return {
                "error":
                    "Please provide the payment amount."
            }

        if not order_id:

            return {
                "error":
                    "Please provide the Razorpay order ID."
            }

        return {

            "tool":
                "initiate_payment",

            "arguments": {

                "amount":
                    amount,

                "currency":
                    "INR",

                "order_id":
                    order_id,

            },

            "label":
                "Initiate Razorpay Payment",
        }


    # ========================================================
    # NOT A WRITE OPERATION
    # ========================================================

    return None


# ============================================================
# CONFIRMATION TEXT
# ============================================================

def build_confirmation(action):

    tool = action["tool"]

    args = action["arguments"]

    label = action["label"]

    lines = [

        "⚠️ **Razorpay confirmation required**",

        "",

        f"**Action:** {label}",

        "",

    ]

    for key, value in args.items():

        if value is None:

            continue

        pretty_key = key.replace(
            "_",
            " "
        ).title()

        lines.append(
            f"**{pretty_key}:** `{value}`"
        )

    lines.extend(
        [

            "",

            "This operation can modify your Razorpay account.",

            "",

            "**Do you want to continue?**",

            "",

            "Type **YES** to execute or **NO** to cancel.",

        ]
    )

    return "\n".join(
        lines
    )


# ============================================================
# EXECUTE CONFIRMED RAZORPAY ACTION
# ============================================================

def execute_confirmed_razorpay_action(
    action
):

    tool = action["tool"]

    args = action["arguments"]


    # ========================================================
    # CREATE ORDER
    # ========================================================

    if tool == "create_order":

        return mcp_razorpay_create_order(

            amount=args["amount"],

            currency=args.get(
                "currency",
                "INR"
            ),

            receipt=args.get(
                "receipt"
            ),

        )


    # ========================================================
    # CREATE PAYMENT LINK
    # ========================================================

    if tool == "create_payment_link":

        return mcp_razorpay_create_payment_link(

            amount=args["amount"],

            description=args["description"],

            currency=args.get(
                "currency",
                "INR"
            ),

        )


    # ========================================================
    # CREATE REFUND
    # ========================================================

    if tool == "create_refund":

        return mcp_razorpay_create_refund(

            payment_id=args["payment_id"],

            amount=args.get(
                "amount"
            ),

        )


    # ========================================================
    # UPDATE ORDER
    # ========================================================

    if tool == "update_order":

        return mcp_razorpay_update_order(

            order_id=args["order_id"],

            notes=args["notes"],

        )


    # ========================================================
    # UPDATE PAYMENT
    # ========================================================

    if tool == "update_payment":

        return mcp_razorpay_update_payment(

            payment_id=args["payment_id"],

            notes=args["notes"],

        )


    # ========================================================
    # UPDATE REFUND
    # ========================================================

    if tool == "update_refund":

        return mcp_razorpay_update_refund(

            refund_id=args["refund_id"],

            notes=args["notes"],

        )


    # ========================================================
    # UPDATE PAYMENT LINK
    # ========================================================

    if tool == "update_payment_link":

        update_args = {

            key: value

            for key, value in args.items()

            if key != "payment_link_id"

        }

        return mcp_razorpay_update_payment_link(

            args["payment_link_id"],

            **update_args

        )


    # ========================================================
    # PAYMENT LINK NOTIFY
    # ========================================================

    if tool == "payment_link_notify":

        return mcp_razorpay_payment_link_notify(

            payment_link_id=args[
                "payment_link_id"
            ],

            medium=args[
                "medium"
            ],

        )


    # ========================================================
    # UPI PAYMENT LINK
    # ========================================================

    if tool == "payment_link_upi_create":

        return mcp_razorpay_payment_link_upi_create(

            amount=args["amount"],

            description=args["description"],

            currency=args.get(
                "currency",
                "INR"
            ),

        )


    # ========================================================
    # QR CODE
    # ========================================================

    if tool == "create_qr_code":

        return mcp_razorpay_create_qr_code(

            payment_amount=args[
                "payment_amount"
            ],

            description=args.get(
                "description",
                ""
            ),

        )


    # ========================================================
    # CAPTURE PAYMENT
    # ========================================================

    if tool == "capture_payment":

        return mcp_razorpay_capture_payment(

            payment_id=args[
                "payment_id"
            ],

            amount=args[
                "amount"
            ],

            currency=args.get(
                "currency",
                "INR"
            ),

        )


    # ========================================================
    # INITIATE PAYMENT
    # ========================================================

    if tool == "initiate_payment":

        return mcp_razorpay_initiate_payment(

            amount=args[
                "amount"
            ],

            currency=args.get(
                "currency",
                "INR"
            ),

            order_id=args[
                "order_id"
            ],

        )


    raise ValueError(
        f"Unsupported confirmed Razorpay operation: {tool}"
    )


# ============================================================
# SAVE MESSAGE
# ============================================================

def save_message(
    role,
    content,
    tool=""
):

    st.session_state.messages.append(

        {
            "role": role,

            "content": content,

            "tool": tool,

        }

    )


# ============================================================
# CHAT INPUT
# ============================================================

user_question = st.chat_input(
    "Ask me anything..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_question:

    request_id = create_request_id()

    st.session_state.current_request_id = (
        request_id
    )

    log_event(
        request_id,
        "REQUEST_RECEIVED",
        "User message received by Streamlit"
    )


    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    save_message(
        "user",
        user_question
    )


    # ========================================================
    # DISPLAY USER
    # ========================================================

    with st.chat_message("user"):

        st.markdown(
            user_question
        )


    # ========================================================
    # CHECK EXISTING CONFIRMATION
    # ========================================================

    pending = (
        st.session_state.pending_razorpay_action
    )


    # ========================================================
    # CONFIRMATION RESPONSE
    # ========================================================

    if pending:

        answer = ""

        selected_tool = ""

        normalized = (
            user_question
            .strip()
            .lower()
        )


        # ====================================================
        # YES
        # ====================================================

        if normalized in {

            "yes",
            "y",
            "confirm",
            "confirmed",
            "yes please",
            "proceed",
            "continue",

        }:

            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "💳 Executing Razorpay operation..."
                ):

                    try:

                        log_event(
                            request_id,
                            "RAZORPAY_CONFIRMED",
                            pending.get(
                                "tool",
                                ""
                            )
                        )

                        result = (
                            execute_confirmed_razorpay_action(
                                pending
                            )
                        )

                        selected_tool = (
                            f"razorpay.{pending['tool']}"
                        )

                        answer = (
                            "✅ **Razorpay operation "
                            "completed successfully.**"
                        )

                        log_event(
                            request_id,
                            "RAZORPAY_OPERATION_COMPLETED",
                            pending.get(
                                "tool",
                                ""
                            )
                        )

                        st.markdown(
                            answer
                        )

                        st.caption(
                            f"🔧 Tool used: {selected_tool}"
                        )

                        with st.expander(
                            "💳 Razorpay MCP Result"
                        ):

                            st.code(
                                str(result),
                                language="json"
                            )


                    except Exception as e:

                        log_event(
                            request_id,
                            "ERROR",
                            f"Razorpay operation failed: {e}"
                        )

                        answer = (
                            "❌ **Razorpay operation failed.**\n\n"
                            f"`{str(e)}`"
                        )

                        st.error(
                            str(e)
                        )


            st.session_state.pending_razorpay_action = (
                None
            )

            save_message(
                "assistant",
                answer,
                selected_tool
            )


        # ====================================================
        # NO
        # ====================================================

        elif normalized in {

            "no",
            "n",
            "cancel",
            "cancel it",
            "don't",
            "do not",

        }:

            answer = (
                "❌ **Razorpay operation cancelled.**\n\n"
                "No changes were made to your Razorpay account."
            )

            with st.chat_message(
                "assistant"
            ):

                st.markdown(
                    answer
                )

            st.session_state.pending_razorpay_action = (
                None
            )

            save_message(
                "assistant",
                answer
            )


        # ====================================================
        # INVALID CONFIRMATION
        # ====================================================

        else:

            answer = (
                "⚠️ I have a Razorpay operation waiting "
                "for confirmation.\n\n"
                "Please type **YES** to execute it or "
                "**NO** to cancel it."
            )

            with st.chat_message(
                "assistant"
            ):

                st.warning(
                    answer
                )

            save_message(
                "assistant",
                answer
            )


    # ========================================================
    # NEW REQUEST
    # ========================================================

    else:

        # ----------------------------------------------------
        # DETECT WRITE OPERATION
        # ----------------------------------------------------

        write_action = (
            detect_razorpay_write_action(
                user_question
            )
        )


        # ----------------------------------------------------
        # WRITE OPERATION
        # ----------------------------------------------------

        if write_action:

            with st.chat_message(
                "assistant"
            ):

                if write_action.get(
                    "error"
                ):

                    answer = (
                        f"❌ {write_action['error']}"
                    )

                    st.error(
                        write_action["error"]
                    )

                    save_message(
                        "assistant",
                        answer
                    )

                else:

                    st.session_state.pending_razorpay_action = (
                        write_action
                    )

                    answer = build_confirmation(
                        write_action
                    )

                    st.markdown(
                        answer
                    )

                    st.caption(
                        "🔐 Confirmation required before Razorpay execution."
                    )

                    save_message(
                        "assistant",
                        answer
                    )


        # ----------------------------------------------------
        # NORMAL READ / GENERAL REQUEST
        # ----------------------------------------------------

        else:

            chat_history = (
                get_chat_history()
            )

            initial_state = {

                "request_id":
                    request_id,

                "question":
                    user_question,

                "chat_history":
                    chat_history,

                "memory_context":
                    "",

                "tool":
                    "",

                "previous_tool":
                    st.session_state.get(
                        "previous_tool",
                        ""
                    ),

                "tool_result":
                    "",

                "last_tool_result":
                    st.session_state.get(
                        "last_razorpay_result",
                        ""
                    ),

                "answer":
                    "",
            }


            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "🤔 Agent is thinking..."
                ):

                    try:

                        # ====================================
                        # GRAPH
                        # ====================================

                        result = graph.invoke(
                            initial_state
                        )


                        # ====================================
                        # SAVE PREVIOUS TOOL
                        # ====================================

                        st.session_state.previous_tool = (
                            result.get(
                                "tool",
                                ""
                            )
                        )


                        # ====================================
                        # REQUEST COMPLETED LOG
                        # ====================================

                        log_event(
                            request_id,
                            "REQUEST_COMPLETED",
                            f"tool={result.get('tool', '')}"
                        )


                        # ====================================
                        # SAVE RAZORPAY RESULT
                        # ====================================

                        if (
                            result.get(
                                "tool"
                            )
                            == "razorpay"
                        ):

                            razorpay_result = (
                                result.get(
                                    "last_tool_result",
                                    result.get(
                                        "tool_result",
                                        ""
                                    )
                                )
                            )

                            if razorpay_result:

                                st.session_state.last_razorpay_result = (
                                    razorpay_result
                                )


                        # ====================================
                        # ANSWER
                        # ====================================

                        answer = result.get(
                            "answer",
                            ""
                        )


                        if not answer:

                            answer = (
                                "I couldn't generate an answer."
                            )


                        # ====================================
                        # SELECTED TOOL
                        # ====================================

                        selected_tool = result.get(
                            "tool",
                            ""
                        )


                        # ====================================
                        # DISPLAY ANSWER
                        # ====================================

                        st.markdown(
                            answer
                        )


                        # ====================================
                        # TOOL DISPLAY
                        # ====================================

                        if selected_tool:

                            st.caption(
                                f"🔧 Tool used: {selected_tool}"
                            )


                        # ====================================
                        # RAZORPAY RAW RESULT
                        # ====================================

                        tool_result = result.get(
                            "tool_result",
                            ""
                        )


                        if (
                            selected_tool
                            and
                            "razorpay"
                            in selected_tool.lower()
                            and
                            tool_result
                        ):

                            with st.expander(
                                "💳 Razorpay MCP Result"
                            ):

                                st.code(
                                    str(tool_result),
                                    language="json"
                                )


                    except Exception as e:

                        log_event(
                            request_id,
                            "ERROR",
                            f"Agent request failed: {e}"
                        )

                        answer = (
                            "❌ Something went wrong.\n\n"
                            f"`{str(e)}`"
                        )

                        selected_tool = ""

                        st.error(
                            str(e)
                        )


            save_message(
                "assistant",
                answer,
                selected_tool
            )