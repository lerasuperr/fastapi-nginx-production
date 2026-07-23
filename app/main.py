from fastapi import FastAPI

from app.config import settings
from app.routers.health import router as health_router
from app.routers.users import router as users_router
from app.routers.metrics import router as metrics_router
from app.middleware import log_requests


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-oriented FastAPI service behind Nginx."
)

app.middleware("http")(log_requests)

app.include_router(health_router)
app.include_router(users_router)
app.include_router(metrics_router)