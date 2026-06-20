import pytest
from app.agent import redeem_discount_code, DISCOUNT_CODES, REGISTERED_USERS

@pytest.fixture(autouse=True)
def reset_in_memory_state():
    """Reset the DISCOUNT_CODES and REGISTERED_USERS state before each test."""
    original_codes = {
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
    
    # Clear and update to reset state without changing the dictionary reference
    DISCOUNT_CODES.clear()
    DISCOUNT_CODES.update(original_codes)
    
    # Ensure registered users are in a clean state
    REGISTERED_USERS.clear()
    REGISTERED_USERS.update({"user_001", "user_002", "user_003"})

def test_redeem_discount_code_success():
    """Test a valid discount code redemption."""
    result = redeem_discount_code("WELCOME50", "user_001")
    assert "Success!" in result
    assert "50% off" in result
    assert DISCOUNT_CODES["WELCOME50"]["redeemed"] is True

def test_redeem_discount_code_unregistered_user():
    """Test boundary: User is not in REGISTERED_USERS (Spoofing/EoP guard)."""
    result = redeem_discount_code("WELCOME50", "hacker_999")
    assert "Error:" in result
    assert "not a registered user" in result
    assert DISCOUNT_CODES["WELCOME50"]["redeemed"] is False

def test_redeem_discount_code_already_redeemed():
    """Test boundary: Code can only be redeemed once (Double Redemption guard)."""
    # First redemption should succeed
    success_result = redeem_discount_code("WELCOME50", "user_001")
    assert "Success!" in success_result
    
    # Second redemption attempt should fail
    fail_result = redeem_discount_code("WELCOME50", "user_002")
    assert "Error:" in fail_result
    assert "already been redeemed" in fail_result

def test_redeem_discount_code_invalid_code():
    """Test boundary: Unrecognized code (Input Validation)."""
    result = redeem_discount_code("FAKE_CODE", "user_001")
    assert "Error:" in result
    assert "not recognised" in result

def test_redeem_discount_code_inactive_code():
    """Test boundary: Code is inactive (RBAC/Status guard)."""
    # Simulate an admin deactivating the code
    DISCOUNT_CODES["WELCOME50"]["active"] = False
    
    result = redeem_discount_code("WELCOME50", "user_001")
    assert "Error:" in result
    assert "currently inactive" in result
    assert DISCOUNT_CODES["WELCOME50"]["redeemed"] is False
