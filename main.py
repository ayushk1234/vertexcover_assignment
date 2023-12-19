from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from coupon_service import CouponService

app = FastAPI()
coupon_service = CouponService()


class CouponConfig(BaseModel):
    user_total: int
    user_daily: int
    user_weekly: int
    global_total: int


@app.post("/add_repeat_counts")
async def add_repeat_counts(coupon_config: CouponConfig):
    try:
        coupon_service.add_repeat_counts(
            "DISCOUNT50",
            coupon_config.user_total,
            coupon_config.user_daily,
            coupon_config.user_weekly,
            coupon_config.global_total,
        )
        return {"result": True, "message": "Repeat counts added successfully."}
    except HTTPException as e:
        return JSONResponse(content={"result": False, "message": e.detail}, status_code=e.status_code)
    except Exception as e:
        return {"result": False, "message": str(e)}


class VerifyCouponRequest(BaseModel):
    coupon_code: str
    user_id: str = None


@app.post("/verify_coupon_validity")
async def verify_coupon_validity(request: VerifyCouponRequest):
    try:
        valid, message = coupon_service.verify_coupon_validity(
            request.coupon_code, request.user_id
        )
        return {"result": valid, "message": message}
    except HTTPException as e:
        return JSONResponse(content={"result": False, "message": e.detail}, status_code=e.status_code)
    except Exception as e:
        return {"result": False, "message": str(e)}


class ApplyCouponRequest(BaseModel):
    coupon_code: str
    user_id: str = None


@app.post("/apply_coupon_code")
async def apply_coupon_code(request: ApplyCouponRequest):
    try:
        result, message = coupon_service.apply_coupon_code(
            request.coupon_code, request.user_id
        )
        return {"result": result, "message": message}
    except HTTPException as e:
        return JSONResponse(content={"result": False, "message": e.detail}, status_code=e.status_code)
    except Exception as e:
        return {"result": False, "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
