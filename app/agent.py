# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from pydantic import BaseModel, Field

# ──────────────────────────────────────────────────────────────────────────────
# In-memory discount code store
# Each code maps to its discount description and a "redeemed" flag.
# ──────────────────────────────────────────────────────────────────────────────
DISCOUNT_CODES: dict[str, dict] = {
    "WELCOME50": {
        "description": "50% off your first purchase",
        "discount_pct": 50,
        "redeemed": False,
        "active": True,
    },
    "SUMMER20": {
        "description": "20% off summer collection",
        "discount_pct": 20,
        "redeemed": False,
        "active": True,
    },
}

# Simple set of known registered user IDs
REGISTERED_USERS: set[str] = {"user_001", "user_002", "user_003"}

# Simple set of known administrative user IDs
ADMIN_USERS: set[str] = {"admin_001"}

# In-memory store for user loyalty points
USER_POINTS: dict[str, int] = {user: 0 for user in REGISTERED_USERS}


def redeem_discount_code(code: str, user_id: str) -> str:
    """Redeem a single-use discount code for a registered user.

    Validates the user is registered, checks the code exists in the in-memory
    store, and ensures it has not already been redeemed or deactivated.
    """
    if user_id not in REGISTERED_USERS:
        return f"Error: User '{user_id}' is not a registered user."

    code_upper = code.strip().upper()
    if code_upper not in DISCOUNT_CODES:
        return f"Error: Discount code '{code_upper}' is not recognised."

    entry = DISCOUNT_CODES[code_upper]

    # Active status guard
    if not entry.get("active", True):
        return (
            f"Error: Discount code '{code_upper}' is currently inactive. "
            "Please try another code."
        )

    # Single-use guard
    if entry["redeemed"]:
        return (
            f"Error: Discount code '{code_upper}' has already been redeemed."
        )

    # Mark as redeemed
    entry["redeemed"] = True
    return f"Success! Code '{code_upper}' redeemed for user '{user_id}'. You get {entry['discount_pct']}% off your purchase."


def list_available_codes() -> str:
    """List available discount codes and their status.

    Returns a string detailing each available discount code, its description,
    and whether it has already been redeemed or is inactive.
    """
    lines = ["Available discount codes:"]
    for code, info in DISCOUNT_CODES.items():
        if not info.get("active", True):
            status = "INACTIVE"
        else:
            status = "REDEEMED" if info["redeemed"] else "AVAILABLE"
        lines.append(f"  • {code}: {info['description']} [{status}]")
    return "\n".join(lines)


class AwardPointsRequest(BaseModel):
    user_id: str = Field(..., description="The registered user ID.")
    amount: int = Field(..., gt=0, le=10000, description="The number of points to award (1-10000).")


def award_loyalty_points(request: AwardPointsRequest) -> str:
    """Award loyalty points to a registered user's account after a purchase.

    This tool validates the user ID and strictly enforces point limits.
    """
    if request.user_id not in REGISTERED_USERS:
        return f"Error: User '{request.user_id}' is not a registered user."

    USER_POINTS[request.user_id] += request.amount
    return f"Success! Awarded {request.amount} points to '{request.user_id}'. New balance is {USER_POINTS[request.user_id]} points."


class UpdateDiscountStatusRequest(BaseModel):
    admin_id: str = Field(..., description="The ID of the admin performing the action.")
    discount_code: str = Field(..., description="The discount code to update.")
    active: bool = Field(..., description="True to activate the code, False to deactivate.")


def update_discount_status(request: UpdateDiscountStatusRequest) -> str:
    """Administratively activate or deactivate a discount code.

    This tool requires administrator authorization.
    """
    if request.admin_id not in ADMIN_USERS:
        return f"Error: Unauthorized. User '{request.admin_id}' is not an administrator."

    code_upper = request.discount_code.strip().upper()
    if code_upper not in DISCOUNT_CODES:
        return f"Error: Discount code '{code_upper}' not found."

    DISCOUNT_CODES[code_upper]["active"] = request.active
    status = "activated" if request.active else "deactivated"
    return f"Success: Discount code '{code_upper}' has been {status}."


# ──────────────────────────────────────────────────────────────────────────────
# Agent definition
# NOTE: The api_key below is a *simulated* hardcoded key placed here
#       intentionally to demonstrate pre-commit security gating in a later step.
# ──────────────────────────────────────────────────────────────────────────────
root_agent = Agent(
    name="shopping_assistant",
    model=Gemini(
        model="gemini-flash-latest",
        api_key="AIzaSyD-mock-key-value-12345",  # type: ignore
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a friendly AI shopping assistant for a retail store. "
        "You can help customers browse products, answer questions about the store, "
        "and redeem single-use discount codes or award loyalty points. "
        "When a customer wants to redeem a code or receive points, always ask for "
        "their registered user ID first. "
        "You can also list available discount codes upon request. "
        "Administrators can ask you to activate or deactivate discount codes, "
        "always ask for their admin ID before calling the update tool."
    ),
    tools=[redeem_discount_code, list_available_codes, award_loyalty_points, update_discount_status],
)

app = App(
    root_agent=root_agent,
    name="shopping-assistant",
)
