import os
import json
import requests
from dotenv import load_dotenv

from app.agent.razorpay_tools import execute_razorpay_tool


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Use the model that already worked with your test_openrouter.py.
# If your test_openrouter.py uses another model, put that same
# model name here.
OPENROUTER_MODEL = "openai/gpt-chat-latest"


if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found in .env"
    )


# ============================================================
# OPENROUTER
# ============================================================

def ask_openrouter(
    prompt: str,
    max_tokens: int = 800
) -> str:

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Razorpay MCP AI Agent",
    }

    payload = {
        "model": OPENROUTER_MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        # IMPORTANT:
        # Do NOT use 65536 here.
        "max_tokens": max_tokens,

        "temperature": 0.1,
    }

    print("\n[OPENROUTER] Sending request...")
    print("[OPENROUTER] Model:", OPENROUTER_MODEL)
    print("[OPENROUTER] Max tokens:", max_tokens)

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )

    if not response.ok:

        print("\n[OPENROUTER ERROR]")
        print("STATUS:", response.status_code)
        print("BODY:")
        print(response.text)

        response.raise_for_status()

    data = response.json()

    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):

        print("\n[OPENROUTER INVALID RESPONSE]")
        print(json.dumps(data, indent=2))

        raise RuntimeError(
            "OpenRouter returned an unexpected response."
        )

    return answer


# ============================================================
# RAZORPAY TOOL LIST
# ============================================================

RAZORPAY_TOOLS = {

    "fetch_all_payments": {
        "description": (
            "Fetch all Razorpay payments. "
            "Useful for latest payments and payment history."
        ),
        "arguments": {
            "count": "number of payments"
        },
    },

    "fetch_all_orders": {
        "description": "Fetch Razorpay orders.",
        "arguments": {
            "count": "number of orders"
        },
    },

    "fetch_all_refunds": {
        "description": "Fetch Razorpay refunds.",
        "arguments": {
            "count": "number of refunds"
        },
    },

    "fetch_all_payment_links": {
        "description": "Fetch Razorpay payment links.",
        "arguments": {
            "count": "number of payment links"
        },
    },

    "fetch_all_qr_codes": {
        "description": "Fetch Razorpay QR codes.",
        "arguments": {
            "count": "number of QR codes"
        },
    },

    "fetch_all_settlements": {
        "description": "Fetch Razorpay settlements.",
        "arguments": {
            "count": "number of settlements"
        },
    },

    "create_order": {
        "description": "Create a Razorpay order.",
        "arguments": {
            "amount": "amount in paise",
            "currency": "currency such as INR",
            "receipt": "optional receipt",
        },
    },

    "create_payment_link": {
        "description": "Create a Razorpay payment link.",
        "arguments": {
            "amount": "amount in paise",
            "currency": "currency",
        },
    },

    "create_qr_code": {
        "description": "Create a Razorpay QR code.",
        "arguments": {},
    },

    "fetch_payment": {
        "description": "Fetch a specific Razorpay payment.",
        "arguments": {
            "payment_id": "Razorpay payment ID",
        },
    },

    "fetch_order": {
        "description": "Fetch a specific Razorpay order.",
        "arguments": {
            "order_id": "Razorpay order ID",
        },
    },

    "fetch_refund": {
        "description": "Fetch a specific Razorpay refund.",
        "arguments": {
            "refund_id": "Razorpay refund ID",
        },
    },
}


# ============================================================
# FORMAT TOOLS FOR AI
# ============================================================

def build_tool_description():

    text = ""

    for name, info in RAZORPAY_TOOLS.items():

        text += f"""
Tool:
{name}

Description:
{info["description"]}

Arguments:
{json.dumps(info["arguments"], indent=2)}

----------------------------------------
"""

    return text


# ============================================================
# AI TOOL SELECTION
# ============================================================

def select_razorpay_tool(question: str):

    tools = build_tool_description()

    prompt = f"""
You are the tool-selection component of a Razorpay AI agent.

USER QUESTION:
{question}

AVAILABLE RAZORPAY MCP TOOLS:

{tools}

Decide whether a Razorpay MCP tool should be called.

Return ONLY valid JSON.

If a tool is required:

{{
  "use_tool": true,
  "tool": "fetch_all_payments",
  "arguments": {{
    "count": 5
  }}
}}

If no tool is required:

{{
  "use_tool": false,
  "tool": null,
  "arguments": {{}}
}}

RULES:

1. "latest payments" means fetch_all_payments.

2. "latest 5 payments" means:
   fetch_all_payments
   with:
   {{
       "count": 5
   }}

3. "latest 10 payments" means:
   fetch_all_payments
   with:
   {{
       "count": 10
   }}

4. If the user asks for payments and does not specify
   a number, use count 10.

5. Never invent a tool name.

6. Return JSON only.
"""

    print("\n[OPENROUTER] Thinking...")

    result = ask_openrouter(
        prompt,
        max_tokens=500
    )

    print("\n[OPENROUTER RAW]")
    print(result)

    result = result.strip()

    # Remove markdown code fences if model adds them.
    if result.startswith("```"):

        result = result.replace(
            "```json",
            ""
        )

        result = result.replace(
            "```",
            ""
        )

        result = result.strip()

    try:

        decision = json.loads(result)

    except json.JSONDecodeError:

        print("\n[OPENROUTER] Invalid JSON.")
        print(result)

        raise RuntimeError(
            "OpenRouter did not return valid tool-selection JSON."
        )

    return decision


# ============================================================
# FINAL ANSWER
# ============================================================

def generate_final_answer(
    question: str,
    tool_name: str,
    tool_result: str,
):

    prompt = f"""
You are a Razorpay AI assistant.

USER QUESTION:
{question}

RAZORPAY MCP TOOL:
{tool_name}

MCP RESULT:
{tool_result}

Answer the user's question using ONLY the MCP result.

Rules:

1. Do not invent information.

2. Do not invent payment IDs.

3. Do not invent amounts.

4. Do not invent transaction statuses.

5. If there are zero records, clearly say that no records
   were found.

6. If payments exist, summarize them clearly.

7. Razorpay amounts may be in paise.
   Convert INR amounts to rupees when appropriate.

8. Keep the answer concise and easy to understand.
"""

    print("\n[OPENROUTER] Generating final answer...")

    return ask_openrouter(
        prompt,
        max_tokens=800
    )


# ============================================================
# MAIN AGENT
# ============================================================

def razorpay_agent(question: str):

    print("\n============================================================")
    print("             RAZORPAY AI AGENT")
    print("============================================================")

    # --------------------------------------------------------
    # STEP 1
    # Ask AI which MCP tool is required
    # --------------------------------------------------------

    decision = select_razorpay_tool(question)

    use_tool = decision.get(
        "use_tool",
        False
    )

    tool_name = decision.get(
        "tool"
    )

    arguments = decision.get(
        "arguments",
        {}
    )

    # --------------------------------------------------------
    # No tool
    # --------------------------------------------------------

    if not use_tool:

        print("\n[AI] No Razorpay MCP tool required.")

        return ask_openrouter(
            question,
            max_tokens=800
        )

    # --------------------------------------------------------
    # Validate tool
    # --------------------------------------------------------

    if tool_name not in RAZORPAY_TOOLS:

        raise ValueError(
            f"AI selected unknown Razorpay tool: {tool_name}"
        )

    # --------------------------------------------------------
    # Fix latest payment count
    # --------------------------------------------------------

    if tool_name == "fetch_all_payments":

        if "count" not in arguments:

            question_lower = question.lower()

            if "latest 5" in question_lower:
                arguments["count"] = 5

            elif "latest 10" in question_lower:
                arguments["count"] = 10

            else:
                arguments["count"] = 10

    # --------------------------------------------------------
    # STEP 2
    # Execute MCP tool
    # --------------------------------------------------------

    print("\n[AI SELECTED RAZORPAY TOOL]")
    print("Tool:", tool_name)
    print("Arguments:", arguments)

    result = execute_razorpay_tool(
        tool_name,
        arguments
    )

    print("\n[MCP RESULT]")
    print(result)

    # --------------------------------------------------------
    # STEP 3
    # Send MCP result back to AI
    # --------------------------------------------------------

    final_answer = generate_final_answer(
        question,
        tool_name,
        result
    )

    return final_answer