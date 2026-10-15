import logging
from collections import deque
from logging.handlers import RotatingFileHandler
from config import LOG_PATH, COLORS

LOG_BUFFER = deque(maxlen=500)

NOISE_SUBSTRINGS = (
    "Server closed the connection",
    "Connection to Telegram failed",
    "Attempt ",
    "Task was destroyed but it is pending",
    "Task exception was never retrieved",
    "Future exception was never retrieved",
    "SSL handshake failed",
    "socket.send() raised exception",
    "Connection reset by peer",
    "Broken pipe",
)

QUIET_LOGGERS = (
    "telethon",
    "telethon.client",
    "telethon.client.telegrambaseclient",
    "telethon.client.updates",
    "telethon.network",
    "telethon.network.mtprotosender",
    "telethon.network.connection",
    "telethon.extensions",
    "aiohttp",
    "aiohttp.access",
    "aiohttp.server",
    "aiohttp.client",
    "asyncio",
)


def _is_noise(msg: str) -> bool:
    return any(s in msg for s in NOISE_SUBSTRINGS)


class BufferHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            if _is_noise(msg):
                return
            LOG_BUFFER.append(msg)
        except Exception:
            pass


class PlainConsoleHandler(logging.Handler):
    def emit(self, record):
        try:
            raw = record.getMessage()
            if _is_noise(raw):
                return
            level = record.levelname
            color = {
                "INFO": COLORS["info"],
                "WARNING": COLORS["header"],
                "ERROR": COLORS["error"],
                "CRITICAL": COLORS["error"],
                "DEBUG": COLORS["accent2"],
            }.get(level, COLORS["info"])
            mark = {
                "INFO": "·",
                "WARNING": "!",
                "ERROR": "×",
                "CRITICAL": "×",
                "DEBUG": "·",
            }.get(level, "·")
            print(f"{color}{mark} {raw}{COLORS['reset']}")
        except Exception:
            pass


def setup_logger(name="hurobot"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(file_handler)

    console_handler = PlainConsoleHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    buffer_handler = BufferHandler()
    buffer_handler.setLevel(logging.INFO)
    buffer_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(buffer_handler)

    for noisy in QUIET_LOGGERS:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logger

log = setup_logger()


def info(msg):
    log.info(f"{COLORS['info']}{msg}{COLORS['reset']}")


def success(msg):
    log.info(f"{COLORS['success']}{msg}{COLORS['reset']}")


def error(msg):
    log.error(f"{COLORS['error']}{msg}{COLORS['reset']}")


def warning(msg):
    log.warning(f"{COLORS['header']}{msg}{COLORS['reset']}")


def debug(msg):
    log.debug(msg)


def exception(msg):
    log.exception(f"{COLORS['error']}{msg}{COLORS['reset']}")