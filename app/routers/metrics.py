from fastapi import APIRouter

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"]
)


@router.get("")
async def metrics():
    return {
        "requests": 1524,
        "uptime": "12h"
    }