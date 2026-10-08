import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

VERSION = "v1.3.0"

GITHUB_API_RELEASES = "https://api.github.com/repos/rud1x/HuroBot_tg/releases/latest"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/hurobot.py"
REQUIREMENTS_URL = "https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt"

DEFAULT_API_ID = 21551581
DEFAULT_API_HASH = "70d80bdf86811654363e45c01c349e98"

_env_api_id = (os.getenv("API_ID") or "").strip()
_env_api_hash = (os.getenv("API_HASH") or "").strip()

if _env_api_id and _env_api_id.isdigit():
    API_ID = int(_env_api_id)
    API_HASH = _env_api_hash or DEFAULT_API_HASH
    USING_DEFAULT_API = False
else:
    API_ID = DEFAULT_API_ID
    API_HASH = DEFAULT_API_HASH
    USING_DEFAULT_API = True


PROXY_TYPE = (os.getenv("PROXY_TYPE") or "").strip().lower()
PROXY_HOST = (os.getenv("PROXY_HOST") or "").strip()
PROXY_PORT = (os.getenv("PROXY_PORT") or "").strip()
PROXY_USER = (os.getenv("PROXY_USER") or "").strip()
PROXY_PASS = (os.getenv("PROXY_PASS") or "").strip()
PROXY_SECRET = (os.getenv("PROXY_SECRET") or "").strip()

PROXY_ENABLED = bool(PROXY_TYPE and PROXY_HOST and PROXY_PORT)


AUTOSTART_RAW = (os.getenv("AUTOSTART") or "").strip()
AUTOSTART_IDS = set()
if AUTOSTART_RAW:
    for part in AUTOSTART_RAW.split(","):
        part = part.strip()
        if part.isdigit():
            AUTOSTART_IDS.add(int(part))


def get_telethon_proxy():
    if not PROXY_ENABLED:
        return None, None
    try:
        port = int(PROXY_PORT)
    except ValueError:
        return None, None

    if PROXY_TYPE == "mtproto":
        from telethon.network import ConnectionTcpMTProxyRandomizedIntermediate
        if not PROXY_SECRET:
            return None, None
        return (PROXY_HOST, port, PROXY_SECRET), ConnectionTcpMTProxyRandomizedIntermediate

    if PROXY_TYPE == "socks5":
        proxy = {"proxy_type": "socks5", "addr": PROXY_HOST, "port": port, "rdns": True}
        if PROXY_USER:
            proxy["username"] = PROXY_USER
        if PROXY_PASS:
            proxy["password"] = PROXY_PASS
        return proxy, None

    if PROXY_TYPE in ("http", "https"):
        proxy = {"proxy_type": "http", "addr": PROXY_HOST, "port": port, "rdns": True}
        if PROXY_USER:
            proxy["username"] = PROXY_USER
        if PROXY_PASS:
            proxy["password"] = PROXY_PASS
        return proxy, None

    return None, None


def detect_system():
    if os.environ.get("TERMUX_VERSION") or Path("/data/data/com.termux").exists():
        return "termux"
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    return "unknown"

SYSTEM = detect_system()

BASE_DIR = Path(__file__).parent.resolve()
DATA_ROOT = BASE_DIR / "HuroBot_data"
DATA_ROOT.mkdir(parents=True, exist_ok=True)

SESSION_DIR = DATA_ROOT / "sessions"
LOG_DIR = DATA_ROOT / "logs"
DATA_DIR = DATA_ROOT / "data"
CACHE_DIR = DATA_ROOT / "cache"
TEMP_DIR = DATA_ROOT / "temp"
AVATAR_DIR = DATA_DIR / "avatars"

for d in (SESSION_DIR, LOG_DIR, DATA_DIR, CACHE_DIR, TEMP_DIR, AVATAR_DIR):
    d.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "hurobot.db"
LOG_PATH = LOG_DIR / "hurobot.log"
PID_PATH = DATA_ROOT / "hurobot.pid"

SESSION_PREFIX = "account_"
TEMP_SESSION = str(TEMP_DIR / "temp.session")

WEB_PORT = int(os.getenv("WEB_PORT", "8080"))

COLORS = {
    "header": "\033[91m",
    "input": "\033[97m",
    "success": "\033[92m",
    "error": "\033[91m",
    "info": "\033[37m",
    "prompt": "\033[97m",
    "accent1": "\033[31m",
    "accent2": "\033[90m",
    "accent3": "\033[97m",
    "accent4": "\033[38;2;255;69;0m",
    "reset": "\033[0m",
}

IS_TERMUX = SYSTEM == "termux"
IS_LINUX = SYSTEM == "linux"
IS_WINDOWS = SYSTEM == "windows"
IS_MACOS = SYSTEM == "macos"


def setup_windows_colors():
    if not IS_WINDOWS:
        return
    try:
        import colorama
        colorama.init()
    except ImportError:
        for key in COLORS:
            COLORS[key] = ""

setup_windows_colors()