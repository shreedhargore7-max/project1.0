# AI Revenue Recovery Agent for Razorpay

An agentic AI system that helps merchants identify payment failures and revenue at risk, understand why transactions are risky, prioritize recovery opportunities, select bounded recovery strategies, obtain explicit human approval, safely execute approved actions through Razorpay MCP, and track recovery outcomes.

## Problem

Failed or risky payments can be buried inside large payment datasets. Identifying a failed transaction is only the beginning of the recovery process.

A useful revenue-recovery system should answer:

* Which payments are putting revenue at risk?
* Why is a payment considered risky?
* Which transactions should be handled first?
* What recovery action is appropriate?
* Does the action require human approval?
* Is the action permitted by recovery policy?
* Can the action be executed safely?
* Was revenue actually recovered?
* Can the complete decision and execution process be audited?

This project addresses that workflow end to end.

## What the Agent Does

The system combines:

* AI reasoning
* PDF RAG
* Long-term memory
* Chat history
* Razorpay MCP
* Payment normalization
* Historical payment enrichment
* Risk analysis
* Root-cause analysis
* Recovery decisioning
* Recovery policy and stopping rules
* Recovery strategy selection
* Human approval
* Production execution guardrails
* Safe Razorpay MCP execution
* Recovery outcome tracking
* Batch recovery metrics
* Held-out evaluation
* Audit logging

## End-to-End Architecture

```text
Payment Data
     ↓
Normalization
     ↓
Historical Enrichment
     ↓
Risk Detection
     ↓
Root Cause Analysis
     ↓
Decision Engine
     ↓
Recovery Policy
     ↓
Recovery Strategy
     ↓
Prioritization
     ↓
Human Approval
     ↓
Production Guardrails
     ↓
Razorpay MCP
     ↓
Recovery Action
     ↓
Outcome Tracking
     ↓
Batch Recovery Metrics
     ↓
Audit Log
```

## Recovery Decision Flow

The system does not treat every risky payment as an automatic recovery opportunity.

```text
Risk Detected
      ↓
Is Recovery Allowed?
      ↓
Check Amount
      ↓
Check Risk
      ↓
Check Failed-Attempt Threshold
      ↓
Select Strategy
      ↓
Approval Required?
   ↙           ↘
 YES            NO
  ↓              ↓
Human Review   Controlled Path
  ↓              ↓
Guardrails
      ↓
Razorpay MCP
      ↓
Execution Outcome
```

## Risk and Root-Cause Analysis

For each payment, the system can consider signals such as:

* Current payment status
* Failed payment attempts
* Repeated failures
* Transaction value
* Previous successful payment history
* Historical customer behavior

Example:

```text
Payment: pay_DEMO007
Amount: ₹25,000
Risk Score: 100
Risk Level: HIGH

Reasons:
- Payment is currently unsuccessful
- 5 failed payment attempts
- Continued recovery difficulty
- High-value transaction
- Strong previous successful payment history
```

## Recovery Policy

A separate policy layer constrains what the agent is allowed to do.

Examples of policy controls include:

```text
Already successful
        → STOP

Maximum failed attempts reached
        → STOP

Low-risk payment
        → MONITOR

High-risk payment
        → REVIEW

High-value recovery
        → HUMAN APPROVAL

Invalid payment/action
        → BLOCK
```

This keeps recovery decisions bounded and prevents the reasoning layer from being the only control over financial actions.

## Recovery Strategy

After policy evaluation, the system selects an appropriate recovery strategy:

```text
LOW risk
   → MONITOR

MEDIUM risk
   → RETRY

HIGH risk
   → PAYMENT_LINK

HIGH + high value
   → MANUAL_REVIEW

Policy / attempt limit reached
   → STOP
```

## Human Approval

Financial recovery actions are not executed automatically.

For approval-required actions:

```text
Recovery Recommendation
        ↓
Approval Request
        ↓
YES → Continue
NO  → Cancel
```

A rejected operation does not reach the external execution layer.

## Production Guardrails

Before an external recovery operation is executed, the system applies additional safety checks:

* Approval validation
* Recovery amount limits
* Allowed-action validation
* Duplicate-operation prevention
* Idempotency checks
* Execution-attempt limits
* Invalid-input protection

Conceptually:

```text
AI Decision
    ↓
Recovery Policy
    ↓
Recovery Strategy
    ↓
Human Approval
    ↓
Execution Guardrails
    ↓
Razorpay MCP
```

## Razorpay MCP Integration

Approved recovery actions can be executed through Razorpay MCP.

The application supports controlled Razorpay operations while keeping write operations behind explicit confirmation.

Example recovery flow:

```text
Recover the highest-priority payment
        ↓
Recovery approval required
        ↓
Human confirms
        ↓
Razorpay MCP execution
```

## Recovery Outcome Tracking

The system distinguishes between an intervention and actual recovered revenue.

```text
CREATED
   ↓
Recovery intervention created

PENDING
   ↓
Waiting for payment outcome

CAPTURED
   ↓
Actual revenue recovered

FAILED / EXPIRED
   ↓
Recovery unsuccessful

STOPPED
   ↓
Blocked by recovery policy

REJECTED
   ↓
Rejected by merchant
```

Most importantly:

```text
Payment Link Created ≠ Revenue Recovered
```

Revenue is counted as recovered only when a successful/captured outcome is confirmed.

## Batch Recovery Metrics

The system can calculate business-level recovery metrics including:

* Total transactions analyzed
* Total revenue
* Revenue at risk
* High-risk transactions
* Medium-risk transactions
* Recovery-eligible transactions
* Recovery-eligible amount
* Approved transactions
* Approved amount
* Created recovery interventions
* Pending recovery amount
* Failed recovery amount
* Recovered transactions
* Recovered revenue
* Recovery rate
* Unrecovered revenue

Example:

```text
Transactions analyzed: 100
Revenue at risk: ₹150,000
Recovery eligible: ₹110,000
Recovered revenue: ₹72,000
Recovery rate: 65.45%
```

## Evaluation

The project includes a separate held-out evaluation dataset to measure system behavior outside the primary demo dataset.

Evaluation covers:

* Risk accuracy
* Decision accuracy
* Priority accuracy
* Approval safety
* Policy safety
* High-value recovery safety

This separates implementation tests from evaluation of the system's decision behavior.

## Testing

The project is heavily tested across the major recovery components.

Current test status:

```text
184 tests
184 passed
0 failed
```

Test coverage includes:

```text
Agent
Approval
Audit
Batch Recovery
Decision Engine
End-to-End Recovery
Evaluation
Historical Enrichment
MCP Executor
Payment Normalization
Recovery Policy
Recovery Workflow
Revenue Recovery Agent Node
Risk Engine
Root Cause Analysis
Strategy Engine
Outcome Tracking
Production Guardrails
Held-Out Evaluation
```

## Example Demo

### 1. Identify risky payments

```text
User:
Which payments are at risk?
```

Example result:

```text
5 high-risk transactions
₹89,500 potential revenue at risk
```

### 2. Explain a risky payment

```text
User:
Why is pay_DEMO007 risky?
```

The system explains the risk score, failed attempts, transaction value, customer history, and other detected signals.

### 3. Recover the highest-priority payment

```text
User:
Recover the highest-priority payment
```

The agent produces an approval request instead of executing immediately.

### 4. Human decision

```text
YES
```

continues toward the approved Razorpay operation.

```text
NO
```

cancels the operation without making the external change.

## Technology Stack

```text
Python
LangGraph
Streamlit
Razorpay MCP
PDF RAG
ChromaDB
Pytest
```

## Project Structure

```text
PROJECT/
│
├── app/
│   ├── agent/
│   ├── chat/
│   ├── chat_history/
│   ├── live_data/
│   ├── mcp_client/
│   ├── mcp_server/
│   ├── memory/
│   ├── monitoring/
│   ├── rag/
│   ├── revenue_recovery/
│   │   ├── batch_recovery.py
│   │   ├── decision_engine.py
│   │   ├── guardrails.py
│   │   ├── history_enrichment.py
│   │   ├── outcome_tracker.py
│   │   ├── payment_normalizer.py
│   │   ├── recovery_policy.py
│   │   ├── recovery_workflow.py
│   │   ├── root_cause.py
│   │   ├── risk_engine.py
│   │   └── strategy_engine.py
│   └── streamlit/
│       └── streamlit_app.py
│
├── data/
│   └── revenue_recovery/
│
├── tests/
│
├── docs/
│   ├── architecture.md
│   └── demo_script.md
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Running the Project

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the test suite:

```powershell
python -m pytest -v
```

Start the Streamlit application:

```powershell
streamlit run app\streamlit\streamlit_app.py
```

## Safety Principle

The project follows a simple execution principle:

```text
Analyze
  ↓
Decide
  ↓
Constrain
  ↓
Approve
  ↓
Guard
  ↓
Execute
  ↓
Measure
  ↓
Audit
```

The objective is not simply to identify failed payments, but to build a controlled revenue-recovery workflow where every financial action is explainable, bounded, approval-aware, and measurable.

## Repository

GitHub:

`https://github.com/shreedhargore7-max/project1.0`
