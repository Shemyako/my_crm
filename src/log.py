import logging

from config import settings

log_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "notset": logging.NOTSET,
}
LOG_LEVEL = log_levels.get(settings.log_level.lower(), logging.INFO)

LOG_FORMAT = "[%(levelname) -3s %(asctime)s] %(message)s"
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)
