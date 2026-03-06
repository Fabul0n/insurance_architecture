from __future__ import annotations

import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path


@dataclass(slots=True)
class LoggerConfig:
    name: str
    log_dir: Path
    filename: str
    max_bytes: int
    backup_count: int


class BaseRotatingLogger:
    def __init__(self, config: LoggerConfig) -> None:
        self._config = config
        self._logger = self._configure_logger()

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def _configure_logger(self) -> logging.Logger:
        logger = logging.getLogger(self._config.name)
        if logger.handlers:
            return logger

        self._config.log_dir.mkdir(parents=True, exist_ok=True)
        log_file = self._config.log_dir / self._config.filename

        handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=self._config.max_bytes,
            backupCount=self._config.backup_count,
            encoding="utf-8",
        )
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False
        return logger

