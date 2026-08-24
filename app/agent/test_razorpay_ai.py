from app.agent.razorpay_ai import razorpay_agent


print("============================================================")
print("             RAZORPAY AI AGENT TEST")
print("============================================================")


question = input(
    "\nEnter your question: "
)


try:

    answer = razorpay_agent(
        question
    )

    print("\n============================================================")
    print("FINAL ANSWER")
    print("============================================================")

    print(answer)

except Exception as e:

    print("\n============================================================")
    print("AGENT ERROR")
    print("============================================================")

    print(
        type(e).__name__
    )

    print(e)