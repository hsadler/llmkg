import logging
import sys

from pythonjsonlogger import jsonlogger

from app.settings import settings


def setup_logging() -> None:
    root_logger = logging.getLogger()
    log_fmt = "%(asctime)s %(levelname)s %(message)s"

    # handler for INFO and DEBUG logs to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_fmt = jsonlogger.JsonFormatter(log_fmt)  # type: ignore
    stdout_handler.setFormatter(stdout_fmt)
    # level for stdout logs
    stdout_handler.setLevel(logging.DEBUG)
    # stout should only receive INFO and DEBUG
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    root_logger.addHandler(stdout_handler)

    # handler for WARNING, ERROR, and CRITICAL to stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_fmt = jsonlogger.JsonFormatter(log_fmt)  # type: ignore
    stderr_handler.setFormatter(stderr_fmt)
    # level for stderr logs
    stderr_handler.setLevel(logging.WARNING)
    root_logger.addHandler(stderr_handler)

    # log level for the root logger (will apply to both handlers)
    level = logging.DEBUG if settings.debug else logging.INFO
    root_logger.setLevel(level)
    root_logger.info("Set up logging", extra={"level": level})
