from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"]
)


@router.get("", response_class=PlainTextResponse)
async def metrics():
   return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )