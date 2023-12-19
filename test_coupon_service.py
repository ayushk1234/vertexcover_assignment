import pytest
from fastapi.testclient import TestClient
from main import app
from coupon_service import CouponService

# Test client for FastAPI
client = TestClient(app)

# Initialize CouponService for testing
coupon_service = CouponService()


@pytest.fixture
def setup():
    # Setup: Add a sample coupon for testing
    coupon_service.add_repeat_counts("TESTCOUPON", 2, 1, 1, 10)


def test_add_repeat_counts(setup):
    # Test: Adding repeat counts
    response = client.post(
        "/add_repeat_counts",
        json={"user_total": 5, "user_daily": 2, "user_weekly": 2, "global_total": 100},
    )
    assert response.status_code == 200
    assert response.json() == {"result": True, "message": "Repeat counts added successfully."}


def test_verify_coupon_validity(setup):
    # Test: Verifying coupon validity
    response = client.post(
        "/verify_coupon_validity",
        json={"coupon_code": "TESTCOUPON", "user_id": "user123"},
    )
    assert response.status_code == 200
    assert response.json() == {"result": True, "message": "Coupon code is valid."}


def test_apply_coupon_code(setup):
    # Test: Applying a coupon code
    response = client.post(
        "/apply_coupon_code",
        json={"coupon_code": "TESTCOUPON", "user_id": "user123"},
    )
    assert response.status_code == 200
    assert response.json() == {"result": True, "message": "Coupon code applied successfully."}


def test_apply_coupon_code_invalid(setup):
    # Test: Applying an invalid coupon code
    response = client.post(
        "/apply_coupon_code",
        json={"coupon_code": "INVALIDCOUPON", "user_id": "user123"},
    )
    assert response.status_code == 400
    assert response.json() == {"result": False, "message": "Coupon code not found."}


if __name__ == "__main__":
    pytest.main()
