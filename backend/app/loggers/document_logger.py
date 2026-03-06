from __future__ import annotations

from pathlib import Path

from app.config import get_settings
from app.loggers.base_logger import BaseRotatingLogger, LoggerConfig


def get_document_logger():
    settings = get_settings()

    # backend_root: корень backend-проекта (там же, где раньше создавалась папка logs)
    backend_root = Path(__file__).resolve().parent.parent.parent
    log_dir = Path(settings.DOCUMENT_LOG_DIR)
    if not log_dir.is_absolute():
        log_dir = backend_root / log_dir

    config = LoggerConfig(
        name="document_events",
        log_dir=log_dir,
        filename=settings.DOCUMENT_LOG_FILENAME,
        max_bytes=settings.DOCUMENT_LOG_MAX_BYTES,
        backup_count=settings.DOCUMENT_LOG_BACKUP_COUNT,
    )
    return BaseRotatingLogger(config).logger

