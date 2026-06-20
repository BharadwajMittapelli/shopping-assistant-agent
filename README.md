# 🛍️ Secure Shopping Assistant Agent

A premium, secure AI Shopping Assistant designed for retail stores, built on the **Google Agent Development Kit (ADK) 2.0** and powered by Gemini. 

This agent manages user interactions, displays active/inactive discount codes, processes single-use redemptions, awards loyalty points, and supports administrative status overrides—all governed by strict input validation schemas and Role-Based Access Control (RBAC) boundaries.

---

## 🏗️ Project Architecture

```
shopping-assistant/
├── app/                        # 🔑 Core Agent Code
│   ├── __init__.py             # Exposes the App instance
│   ├── agent.py                # Agent configuration, tools, and state
│   ├── fast_api_app.py         # FastAPI local web service
│   └── app_utils/              # OpenTelemetry & validation utilities
├── tests/                      # 🧪 Test Suites
│   ├── test_agent.py           # Outcome-based security & boundary tests
│   └── integration/            # E2E server checks
├── threat_model.md             # STRIDE Threat Modeling assessment
├── pyproject.toml              # Dependencies & tooling configurations
└── README.md                   # Project documentation
```

---

## ⚡ Key Features & Tools

### 1. Discount Code Redemption (`redeem_discount_code`)
* **Logic:** Resolves single-use discount codes (`WELCOME50` - 50% off, `SUMMER20` - 20% off) for customers.
* **Security Controls:**
  * Checks that the user ID is in the `REGISTERED_USERS` set (**Spoofing Guard**).
  * Enforces that the code is active and has not already been used (**Double Redemption Guard**).

### 2. Loyalty Point Allocation (`award_loyalty_points`)
* **Logic:** Awards points to a registered user account after a successful transaction.
* **Security Controls:**
  * Uses a strict Pydantic model (`AwardPointsRequest`) to enforce type boundaries.
  * Asserts point amounts are strictly positive and capped (`gt=0, le=10000`) to prevent **Integer Overflow** or negative deduction exploits.

### 3. Administrative Override (`update_discount_status`)
* **Logic:** Allows administrators to dynamically activate/deactivate discount codes in-store.
* **Security Controls:**
  * Strictly restricted to the `ADMIN_USERS` set (`admin_001`) via Pydantic model validation (`UpdateDiscountStatusRequest`).
  * Prevents **Elevation of Privilege** by rejecting standard customer user IDs.

---

## 🔒 Security & Threat Modeling (STRIDE)

This repository includes a comprehensive threat assessment mapped out in [`threat_model.md`](./threat_model.md). Key mitigations implemented directly in the code include:
* **Input Validation (Tampering):** Pydantic types constrain parameters before any Python business logic is executed.
* **Role-Based Access Control (Elevation of Privilege):** Administrative commands check requesting identity matches `ADMIN_USERS` prior to modifying memory variables.

---

## 🚀 Getting Started

### 📦 Installation
Ensure you have [uv](https://docs.astral.sh/uv/) installed. Run the following command in the project root to install dependencies and establish the virtual environment:

```bash
uv sync --group dev
```

### 🧪 Running the Tests
Execute the outcome-based Pytest security suite to verify all business rules, bounds, and RBAC rules are passing successfully:

```bash
uv run pytest tests/test_agent.py
```

### 🖥️ Local Playground
To chat with the agent in a local web interface, launch the ADK Web Server:

* **On standard bash/zsh (or CMD):**
  ```bash
  uv run adk web . --host 127.0.0.1 --port 8080 --reload_agents
  ```
* **On Windows PowerShell:**
  *(Omit the unescaped `'*'` wildcard from origins to prevent PowerShell wildcard expansion errors)*
  ```powershell
  uv run adk web . --host 127.0.0.1 --port 8080 --reload_agents
  ```

Once launched, visit **[http://127.0.0.1:8080](http://127.0.0.1:8080)** to chat with the agent.

---

## 📝 Test Scenarios Documented
Our test suite in [`tests/test_agent.py`](./tests/test_agent.py) covers:
1. **Success Cases:** Happy path for discount redemption.
2. **Identity Boundaries:** Unregistered users are rejected.
3. **Replay Protection:** Re-redeeming a code throws an error.
4. **Input Constraints:** Malformed or unrecognized codes return error notifications.
5. **Admin Bounds:** Deactivated discount codes cannot be redeemed.
