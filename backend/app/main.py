from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import insurance
from app.config import get_settings
from app.loggers.auth_logger import get_auth_logger
from app.middleware.auth_logging import AuthLoggingMiddleware


app = FastAPI(title="Insurance Service", version="0.1.0")

settings = get_settings()
origins = [item.strip() for item in settings.CORS_ORIGINS.split(",") if item.strip()]
allow_all = len(origins) == 1 and origins[0] == "*"

auth_logger = get_auth_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthLoggingMiddleware, logger=auth_logger)

app.include_router(insurance.router, prefix="/api")

# Serve frontend static files if present
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


def run_server() -> None:
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000, reload=True)
