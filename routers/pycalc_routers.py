from datetime import datetime
from streaming.kafka_consumer import stats
from fastapi import APIRouter, Depends, HTTPException
from models.pycalc_models import MathResult
from routers.auth_router import verify_token
from services.pycalc_service import MathService
from db.db_repository import insert_operation
from cache.redis_cache import get_cached_result, set_cached_result
import time

from streaming.kafka_producer import send_message

router = APIRouter()


@router.get("/fibonacci/{n}", response_model=MathResult)
async def get_fibonacci(
        n: int, current_user: str = Depends(verify_token),
        service: MathService = Depends()
):
    if n > 500:
        raise HTTPException(
            status_code=400,
            detail="Input too large. Please use a value <= 500."
        )

    # Check cache first
    cached_result = await get_cached_result(f"fibonacci:{n}")
    if cached_result:
        print(f"Cache hit for fibonacci({n})")
        return MathResult(operation="fibonacci", input=n, result=int(cached_result))

    start = time.perf_counter()

    result = await service.fibonacci(n)

    # Cache the result for future requests
    await set_cached_result(f"fibonacci:{n}", str(result), expire=3600)

    await insert_operation("fibonacci", str(n), str(result), current_user)

    end = time.perf_counter()
    print(f"Fibonacci calculation took {end - start:.4f} seconds")

    await send_message("operation_stream", {
        "operation": "fibonacci",
        "input": str(n),
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user
    })

    return MathResult(operation="fibonacci", input=n, result=result)


@router.get("/factorial/{n}", response_model=MathResult)
async def get_factorial(
        n: int, current_user: str = Depends(verify_token),
        service: MathService = Depends()
):
    if n > 100:
        raise HTTPException(
            status_code=400,
            detail="Input too large. Please use a value <= 100."
        )

    # Check cache first
    cached_result = await get_cached_result(f"factorial:{n}")
    if cached_result:
        print(f"Cache hit for factorial({n})")
        await send_message("operation_stream", {
            "operation": "factorial",
            "input": str(n),
            "result": cached_result,
            "timestamp": datetime.utcnow().isoformat(),
            "user": current_user
        })
        return MathResult(operation="factorial", input=n, result=int(cached_result))

    # If not cached, perform the calculation
    start = time.perf_counter()

    result = await service.factorial(n)

    # Cache the result for future requests
    await set_cached_result(f"factorial:{n}", str(result), expire=3600)

    await insert_operation("factorial", str(n), str(result), current_user)

    end = time.perf_counter()

    await send_message("operation_stream", {
        "operation": "factorial",
        "input": str(n),
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user
    })

    print(f"Factorial calculation took {end - start:.4f} seconds")
    return MathResult(operation="factorial", input=n, result=result)


@router.get("/pow/{x}/{y}", response_model=MathResult)
async def get_power(
        x: float,
        y: float,
        current_user: str = Depends(verify_token),
        service: MathService = Depends()
):
    if abs(x) > 100 or abs(y) > 100:
        raise HTTPException(400, "Base and exponent must be between -100 and 100")

    # Check cache first
    cached_result = await get_cached_result(f"power:{x}:{y}")
    if cached_result:
        print(f"Cache hit for power({x}, {y})")
        return MathResult(operation="power", input={"base": x, "exponent": y}, result=float(cached_result))

    start = time.perf_counter()

    input_data = f"{x}^{y}" if y != 1 else str(x)
    # If not cached, perform the calculation
    result = await service.power(x, y)

    # Cache the result for future requests
    await set_cached_result(f"power:{x}:{y}", str(result), expire=3600)

    await insert_operation("pow", input_data, str(result), current_user)

    end = time.perf_counter()
    print(f"Power calculation took {end - start:.4f} seconds")

    await send_message("operation_stream", {
        "operation": "power",
        "input": input_data,
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user
    })

    return MathResult(
        operation="power",
        input={"base": x, "exponent": y},
        result=result
    )
