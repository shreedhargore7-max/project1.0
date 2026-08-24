from app.agent.razorpay_tools import (
    execute_razorpay_tool,
)


print("=" * 60)
print("RAZORPAY MCP TOOL EXECUTION TEST")
print("=" * 60)


result = execute_razorpay_tool(
    "fetch_all_payments",
    {
        "count": 5
    }
)


print()
print("=" * 60)
print("RESULT")
print("=" * 60)

print(result)