# app/agent/razorpay_safety.py

# ---------------------------------------------------------
# Razorpay tool safety / confirmation rules
# ---------------------------------------------------------

READ_ONLY_TOOLS = {
    "fetch_all_payments",
    "fetch_all_orders",
    "fetch_all_payment_links",
    "fetch_all_qr_codes",
    "fetch_all_refunds",
    "fetch_all_settlements",
    "fetch_all_instant_settlements",
    "fetch_all_payouts",

    "fetch_payment",
    "fetch_order",
    "fetch_order_payments",
    "fetch_payment_link",
    "fetch_qr_code",
    "fetch_payout_with_id",
    "fetch_refund",
    "fetch_specific_refund_for_payment",
    "fetch_multiple_refunds_for_payment",
    "fetch_instant_settlement_with_id",
    "fetch_settlement_with_id",
    "fetch_settlement_recon_details",
    "fetch_payment_card_details",
    "fetch_tokens",
    "fetch_qr_codes_by_customer_id",
    "fetch_qr_codes_by_payment_id",
}


ACTION_TOOLS = {
    "create_order",
    "create_payment_link",
    "create_qr_code",
    "create_registration_link",
    "capture_payment",
    "initiate_payment",
    "payment_link_upi_create",
    "payment_link_notify",
    "resend_otp",
    "submit_otp",
    "revoke_token",
    "update_order",
    "update_payment",
    "update_payment_link",
    "update_refund",
}


def normalize_tool_name(tool_name: str) -> str:
    """
    Converts:

        razorpay.create_order

    into:

        create_order
    """

    if not tool_name:
        return ""

    return tool_name.split(".")[-1].strip()


def is_read_only_tool(tool_name: str) -> bool:
    """
    Returns True if the Razorpay tool only reads data.
    """

    name = normalize_tool_name(tool_name)

    return name in READ_ONLY_TOOLS


def requires_confirmation(tool_name: str) -> bool:
    """
    Returns True if executing the tool can modify/create
    financial resources or perform an action.
    """

    name = normalize_tool_name(tool_name)

    return name in ACTION_TOOLS


def format_confirmation(tool_name: str, arguments: dict) -> str:
    """
    Creates a human-readable confirmation message.
    """

    name = normalize_tool_name(tool_name)

    if name == "create_order":

        amount = arguments.get("amount")

        if amount is not None:
            try:
                amount_rupees = float(amount) / 100
                amount_text = f"₹{amount_rupees:,.2f}"
            except Exception:
                amount_text = str(amount)
        else:
            amount_text = "the specified amount"

        return (
            "\n"
            "============================================================\n"
            "                 ACTION CONFIRMATION\n"
            "============================================================\n"
            f"I am about to create a Razorpay order for {amount_text}.\n"
            f"Currency: {arguments.get('currency', 'INR')}\n"
            "\n"
            "Do you want me to continue? (yes/no)\n"
        )

    if name == "create_payment_link":

        amount = arguments.get("amount")

        if amount is not None:
            try:
                amount_rupees = float(amount) / 100
                amount_text = f"₹{amount_rupees:,.2f}"
            except Exception:
                amount_text = str(amount)
        else:
            amount_text = "the specified amount"

        return (
            "\n"
            "============================================================\n"
            "                 ACTION CONFIRMATION\n"
            "============================================================\n"
            f"I am about to create a Razorpay payment link for {amount_text}.\n"
            f"Currency: {arguments.get('currency', 'INR')}\n"
            "\n"
            "Do you want me to continue? (yes/no)\n"
        )

    if name == "create_qr_code":

        amount = arguments.get("amount")

        if amount is not None:
            try:
                amount_rupees = float(amount) / 100
                amount_text = f"₹{amount_rupees:,.2f}"
            except Exception:
                amount_text = str(amount)
        else:
            amount_text = "the specified amount"

        return (
            "\n"
            "============================================================\n"
            "                 ACTION CONFIRMATION\n"
            "============================================================\n"
            f"I am about to create a Razorpay QR code for {amount_text}.\n"
            "\n"
            "Do you want me to continue? (yes/no)\n"
        )

    return (
        "\n"
        "============================================================\n"
        "                 ACTION CONFIRMATION\n"
        "============================================================\n"
        f"The AI wants to execute Razorpay tool: {name}\n"
        f"Arguments: {arguments}\n"
        "\n"
        "This action can modify your Razorpay account.\n"
        "Do you want me to continue? (yes/no)\n"
    )


def ask_confirmation(tool_name: str, arguments: dict) -> bool:
    """
    Ask the user for confirmation before an action tool.
    """

    print(format_confirmation(tool_name, arguments))

    answer = input("> ").strip().lower()

    return answer in {
        "yes",
        "y",
        "confirm",
        "confirmed",
    }