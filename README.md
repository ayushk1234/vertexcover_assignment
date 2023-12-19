# vertexcover_assignment

pip install -r requirements.txt
uvicorn main:app --reload

run unit test
test_coupon_service.py

Coupon Service API Testing

1. Add Repeat Counts to a Coupon Code
curl -X POST http://localhost:8000/add_repeat_counts \
     -H "Content-Type: application/json" \
     -d '{"user_total": 3, "user_daily": 1, "user_weekly": 1, "global_total": 10000}'

2. Verify Coupon Code Validity
   curl -X POST http://localhost:8000/verify_coupon_validity \
     -H "Content-Type: application/json" \
     -d '{"coupon_code": "DISCOUNT50", "user_id": "user123"}'

3.Apply Coupon Code
  curl -X POST http://localhost:8000/apply_coupon_code \
     -H "Content-Type: application/json" \
     -d '{"coupon_code": "DISCOUNT50", "user_id": "user123"}'
