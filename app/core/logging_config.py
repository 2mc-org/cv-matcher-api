import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_LEVEL = logging.INFO
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"

_RESET = "\033[0m"
_DIM = "\033[2m"
_LEVEL_COLORS: dict[int, str] = {
    logging.DEBUG: "\033[36m",
    logging.INFO: "\033[32m",
    logging.WARNING: "\033[33m",
    logging.ERROR: "\033[31m",
    logging.CRITICAL: "\033[35m\033[1m",
}


def _color_enabled() -> bool:
    return os.environ.get("NO_COLOR") is None and sys.stderr.isatty()


class CustomFormatter(logging.Formatter):
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        *,
        compact_info: bool = False,
        compact_error: bool = False,
        use_color: bool = False,
    ) -> None:
        super().__init__(fmt, datefmt)
        self.compact_info = compact_info
        self.compact_error = compact_error
        self.use_color = use_color

    def _color(self, text: str, levelno: int) -> str:
        if not self.use_color:
            return text
        return f"{_LEVEL_COLORS.get(levelno, '')}{text}{_RESET}"

    def _dim(self, text: str) -> str:
        if not self.use_color:
            return text
        return f"{_DIM}{text}{_RESET}"

    def format(self, record: logging.LogRecord) -> str:
        levelname = f"{record.levelname}:".ljust(10)

        if self.compact_info and record.levelno == logging.INFO:
            return self._color(levelname, record.levelno) + record.getMessage()

        if self.compact_error and record.levelno >= logging.ERROR:
            error_message = record.getMessage()
            for exc_info in record.exc_info or []:
                if isinstance(exc_info, Exception):
                    error_message += (
                        "\n"
                        + " " * 10
                        + f"{exc_info.__class__.__name__}: {exc_info}"
                    )
            return self._color(levelname, record.levelno) + error_message

        # Format the time
        record.asctime = self.formatTime(record, self.datefmt)

        # Create log header
        record.logheader = (
            f"{self._color(levelname, record.levelno)}"
            f"{self._dim(f'{record.asctime} - {record.name} - [{record.filename}:{record.lineno}]')}"
        )

        # Get formatted message from parent class
        msg = super().format(record)

        # Add padding to message
        lines = msg.split("\n")
        result_lines = []
        for i, line in enumerate(lines):
            if i > 0:  # Skip header line
                result_lines.append(f"{' ' * 2}{line}")
            else:
                result_lines.append(line)
        return "\n".join(result_lines)


def setup_logging() -> None:
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Remove all handlers from the root logger to avoid duplicate logging
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatters
    formatter = CustomFormatter(
        "%(logheader)s\n%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = CustomFormatter(
        "%(logheader)s\n%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        compact_info=True,
        compact_error=False,
        use_color=_color_enabled(),
    )

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Create daily rotating file handler for all logs
    all_logs_handler = TimedRotatingFileHandler(
        LOG_DIR / "app.log",
        when="midnight",
        backupCount=30,  # keep logs for 30 days
        encoding="utf-8",
    )
    all_logs_handler.setFormatter(formatter)

    # Create error log handler
    error_handler = TimedRotatingFileHandler(
        LOG_DIR / "error.log",
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)  # Only ERROR and above

    # Create critical log handler
    critical_handler = TimedRotatingFileHandler(
        LOG_DIR / "critical.log",
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    critical_handler.setFormatter(formatter)
    critical_handler.setLevel(logging.CRITICAL)  # Only CRITICAL

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(all_logs_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(critical_handler)

    # Configure specific loggers
    loggers: dict[str, int] = {
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.INFO,
        "fastapi": logging.INFO,
        "sqlalchemy": logging.WARNING,
        "simulation": logging.DEBUG,
        "pymongo": logging.WARNING,
    }

    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.addHandler(all_logs_handler)
        logger.addHandler(error_handler)
        logger.addHandler(critical_handler)
        # logger.addHandler(console_handler)
        logger.propagate = False
