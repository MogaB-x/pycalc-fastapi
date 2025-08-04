class MathService:
    async def factorial(self, n: int) -> int:
        if n < 0:
            raise ValueError("n must be a non-negative integer")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    async def fibonacci(self, n: int) -> int:
        if n < 0:
            raise ValueError("n must be a non-negative integer")
        elif n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b

    async def power(self, base: float, exponent: float) -> float:
        if exponent < 0:
            raise ValueError("exponent must be a non-negative number")
        return base ** exponent
