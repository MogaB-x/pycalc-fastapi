from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from models.pycalc_models import MathResult
from routers.auth_router import verify_token
from services.pycalc_service import MathService
from db.db_repository import insert_operation
from cache.redis_cache import get_cached_result, set_cached_result
import time

from streaming.pubsub_producer import send_message

router = APIRouter()


@router.get("/fibonacci/{n}", response_model=MathResult)
async def get_fibonacci(
        n: int, current_user: str = Depends(verify_token),
        service: MathService = Depends()
):
    """
        Compute the n-th number in the Fibonacci sequence.

        - **n**: integer from 0 to 500
        - **Returns**: Fibonacci result
        - **Uses**: Redis cache, Pub/Sub, JWT Auth
        """
    if n > 500:
        raise HTTPException(
            status_code=400,
            detail="Input too large. Please use a value <= 500."
        )

    # Check cache first
    cached_result = await get_cached_result(f"fibonacci:{n}")
    if cached_result:
        print(f"Cache hit for fibonacci({n})")
        send_message({
            "operation": "fibonacci",
            "input": str(n),
            "cached_result": cached_result,
            "timestamp": datetime.utcnow().isoformat(),
            "user": current_user
        })
        return MathResult(operation="fibonacci", input=n, result=int(cached_result))

    start = time.perf_counter()
    result = await service.fibonacci(n)
    end = time.perf_counter()
    print(f"Fibonacci calculation took {end - start:.4f} seconds")
    # Cache the result for future requests
    await set_cached_result(f"fibonacci:{n}", str(result), expire=3600)
    await insert_operation("fibonacci", str(n), str(result), current_user)

    send_message( {
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
    """
        Calculate the factorial of a given number.

        - **n**: non-negative integer (max 100)
        - **Returns**: result of `n!` and operation metadata
        - **Requires**: JWT access token
    """
    if n > 100:
        raise HTTPException(
            status_code=400,
            detail="Input too large. Please use a value <= 100."
        )

    # Check cache first
    cached_result = await get_cached_result(f"factorial:{n}")
    if cached_result:
        print(f"Cache hit for factorial({n})")
        send_message({
            "operation": "factorial",
            "input": str(n),
            "cached_result": cached_result,
            "timestamp": datetime.utcnow().isoformat(),
            "user": current_user
        })
        return MathResult(operation="factorial", input=n, result=int(cached_result))

    # If not cached, perform the calculation
    start = time.perf_counter()
    result = await service.factorial(n)
    end = time.perf_counter()
    print(f"Factorial calculation took {end - start:.4f} seconds")
    # Cache the result for future requests
    await set_cached_result(f"factorial:{n}", str(result), expire=3600)
    await insert_operation("factorial", str(n), str(result), current_user)

    send_message({
        "operation": "factorial",
        "input": str(n),
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user
    })

    return MathResult(operation="factorial", input=n, result=result)


@router.get("/pow/{x}/{y}", response_model=MathResult)
async def get_power(
        x: float,
        y: float,
        current_user: str = Depends(verify_token),
        service: MathService = Depends()
):
    """
        Compute x raised to the power y.

        - **x**: base number (float, max 100)
        - **y**: exponent (float, max 100)
        - **Returns**: x ** y
        - **Cached**: result saved in Redis for faster lookup
    """
    if abs(x) > 100 or abs(y) > 100:
        raise HTTPException(400, "Base and exponent must be between -100 and 100")

    input_data = f"{x}^{y}" if y != 1 else str(x)
    # Check cache first
    cached_result = await get_cached_result(f"power:{x}:{y}")
    if cached_result:
        print(f"Cache hit for power({x}, {y})")
        send_message({
            "operation": "power",
            "input": input_data,
            "cached_result": cached_result,
            "timestamp": datetime.utcnow().isoformat(),
            "user": current_user
        })
        return MathResult(operation="power", input={"base": x, "exponent": y}, result=float(cached_result))

    start = time.perf_counter()
    # If not cached, perform the calculation
    result = await service.power(x, y)
    end = time.perf_counter()
    print(f"Power calculation took {end - start:.4f} seconds")

    # Cache the result for future requests
    await set_cached_result(f"power:{x}:{y}", str(result), expire=3600)
    await insert_operation("pow", input_data, str(result), current_user)

    send_message({
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
