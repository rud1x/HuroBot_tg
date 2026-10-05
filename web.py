import asyncio
import re
from pathlib import Path
from aiohttp import web
from config import VERSION, AVATAR_DIR
from logger import LOG_BUFFER, info

HTML_PATH = Path(__file__).parent / "templates" / "index.html"
ENV_PATH = Path(__file__).parent / ".env"

ENV_KEYS = [
    "API_ID", "API_HASH",
    "PROXY_TYPE", "PROXY_HOST", "PROXY_PORT", "PROXY_SECRET",
    "PROXY_USER", "PROXY_PASS",
    "WEB_PORT",
    "AUTOSTART",
]

PHONE_RE = re.compile(r'^\+\d{8,15}$')


class WebPanel:
    def __init__(self, bot, host="127.0.0.1", port=8080):
        self.bot = bot
        self.host = host
        self.port = port
        self.app = web.Application()
        self.app.router.add_get("/", self.index)
        self.app.router.add_get("/api/accounts", self.api_accounts)
        self.app.router.add_post("/api/start/{id}", self.api_start)
        self.app.router.add_post("/api/stop/{id}", self.api_stop)
        self.app.router.add_delete("/api/account/{id}", self.api_delete)
        self.app.router.add_post("/api/account/{id}/refresh-avatar", self.api_refresh_avatar)
        self.app.router.add_post("/api/add", self.api_add)
        self.app.router.add_get("/api/avatar/{id}", self.api_avatar)
        self.app.router.add_get("/api/env", self.api_env_get)
        self.app.router.add_post("/api/env", self.api_env_set)
        self.app.router.add_get("/api/logs", self.api_logs)
        self.app.router.add_get("/ws/logs", self.ws_logs)
        self.runner = None

    async def index(self, request):
        html = HTML_PATH.read_text(encoding="utf-8").replace("__VERSION__", VERSION)
        return web.Response(text=html, content_type="text/html")

    async def api_accounts(self, request):
        accounts = []
        for num, acc in self.bot.accounts.items():
            avatar_path = AVATAR_DIR / f"{num}.jpg"
            uptime = 0
            if num in self.bot.running:
                started = self.bot.started_at.get(num)
                if started:
                    uptime = int((asyncio.get_event_loop().time() - started))

            accounts.append({
                "id": num,
                "name": acc["name"],
                "phone": acc["phone"],
                "running": num in self.bot.running,
                "autostart": num in self.bot.autostart,
                "has_avatar": avatar_path.exists(),
                "uptime": uptime,
            })
        return web.json_response({"accounts": accounts})

    async def api_start(self, request):
        num = int(request.match_info["id"])
        try:
            result = await self.bot.start_account(num)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({"ok": False, "error": str(e)}, status=500)

    async def api_stop(self, request):
        num = int(request.match_info["id"])
        try:
            result = await self.bot.stop_account(num)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({"ok": False, "error": str(e)}, status=500)

    async def api_delete(self, request):
        num = int(request.match_info["id"])
        result = await self.bot.delete_account(num)
        return web.json_response(result)

    async def api_refresh_avatar(self, request):
        num = int(request.match_info["id"])
        result = await self.bot.refresh_avatar(num)
        return web.json_response(result)

    async def api_avatar(self, request):
        num = int(request.match_info["id"])
        avatar_path = AVATAR_DIR / f"{num}.jpg"
        if not avatar_path.exists():
            return web.Response(status=404)
        return web.FileResponse(avatar_path)

    async def api_add(self, request):
        data = await request.json()
        phone = (data.get("phone") or "").strip()
        stage = data.get("stage", "phone")
        code = data.get("code")
        password = data.get("password")

        if not phone:
            return web.json_response({"ok": False, "error": "номер пустой"}, status=400)

        if stage == "phone":
            clean = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not clean.startswith("+"):
                clean = "+" + clean.lstrip("+")
            if not PHONE_RE.match(clean):
                return web.json_response({
                    "ok": False,
                    "error": "неверный формат номера. пример: +79123456789"
                })
            phone = clean
            result = await self.bot.start_add_account(phone)
        elif stage == "code":
            result = await self.bot.complete_add_account(phone, code=code)
        elif stage == "password":
            result = await self.bot.complete_add_account(phone, password=password)
        else:
            result = {"ok": False, "error": "неизвестная стадия"}

        return web.json_response(result)

    async def api_env_get(self, request):
        env = {}
        if ENV_PATH.exists():
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    env[key.strip()] = value.strip()

        for key in ENV_KEYS:
            env.setdefault(key, "")

        if not env.get("AUTOSTART"):
            env["AUTOSTART"] = ",".join(str(x) for x in sorted(self.bot.autostart))

        return web.json_response({"env": env})

    async def api_env_set(self, request):
        data = await request.json()

        existing = {}
        if ENV_PATH.exists():
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    key, _, value = line.partition("=")
                    existing[key.strip()] = value.strip()

        for key in ENV_KEYS:
            if key in data:
                value = str(data[key]).strip()
                if value:
                    existing[key] = value
                else:
                    existing.pop(key, None)

        autostart_str = existing.get("AUTOSTART", "")
        new_autostart = set()
        for part in autostart_str.split(","):
            part = part.strip()
            if part.isdigit():
                new_autostart.add(int(part))
        self.bot.autostart = new_autostart

        lines = ["# HuroBot settings", ""]
        for key, value in existing.items():
            lines.append(f"{key}={value}")

        try:
            ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
            info(f".env сохранён ({len(existing)} полей)")
            return web.json_response({"ok": True})
        except Exception as e:
            return web.json_response({"ok": False, "error": str(e)}, status=500)

    async def api_logs(self, request):
        return web.json_response({"logs": list(LOG_BUFFER)})

    async def ws_logs(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        sent_count = 0
        try:
            while not ws.closed:
                logs = list(LOG_BUFFER)
                if len(logs) > sent_count:
                    for line in logs[sent_count:]:
                        await ws.send_str(line)
                    sent_count = len(logs)
                await asyncio.sleep(1)
        except Exception:
            pass
        return ws

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()