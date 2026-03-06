from __future__ import annotations

from pathlib import Path

from app.config import get_settings
from app.loggers.base_logger import BaseRotatingLogger, LoggerConfig


def get_auth_logger():
    settings = get_settings()

    # backend_root: корень backend-проекта (там же, где раньше создавалась папка logs)
    backend_root = Path(__file__).resolve().parent.parent.parent
    log_dir = Path(settings.AUTH_LOG_DIR)
    if not log_dir.is_absolute():
        log_dir = backend_root / log_dir

    config = LoggerConfig(
        name="auth_events",
        log_dir=log_dir,
        filename=settings.AUTH_LOG_FILENAME,
        max_bytes=settings.AUTH_LOG_MAX_BYTES,
        backup_count=settings.AUTH_LOG_BACKUP_COUNT,
    )
    return BaseRotatingLogger(config).logger

