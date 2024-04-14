import logging

import httpx
from fastapi import APIRouter, HTTPException, Path, Response

logger = logging.getLogger(__name__)


router: APIRouter = APIRouter(prefix="/api/example", tags=["examples"])


def fibonacci(n: int) -> int:
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


@router.get(
    "/long-running/fibonacci/{n}",
    description="Calculate the nth fibonacci number.",
    responses={},
)
async def get_fibonacci(n: int = Path(example=10)) -> Response:
    logger.info("Calculating fibonacci number", extra={"n": n})
    try:
        res = fibonacci(n)
    except Exception as e:
        logger.exception("Error calculating fibonacci number", extra={"n": n, "error": e})
        raise HTTPException(status_code=500)
    logger.info("Calculated fibonacci number successfully", extra={"n": n, "result": res})
    return Response(content=str(res), media_type="text/plain")


@router.get(
    "/external_call/weather/{city}",
    description="Fetch weather by city name.",
    responses={},
)
async def get_weather(city: str = Path(example="stockholm")) -> Response:
    logger.info("Fetching weather by city", extra={"city": city})
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"https://wttr.in/{city}?format=3")
    except Exception as e:
        logger.exception("Error fetching weather by city", extra={"city": city, "error": e})
        raise HTTPException(status_code=500)
    logger.info("Fetched weather data successfully", extra={"city": city, "weather": res.text})
    return Response(content=res.text, media_type="text/plain")
