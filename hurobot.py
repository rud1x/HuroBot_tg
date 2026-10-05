import asyncio
import sys
import re
import importlib
import hashlib
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

from telethon import TelegramClient, events
from telethon.errors import (
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
    FloodWaitError,
    PasswordHashInvalidError,
)
from telethon.errors.rpcerrorlist import TimedOutError

from config import (
    API_ID, API_HASH, VERSION, COLORS, SESSION_DIR, SESSION_PREFIX,
    TEMP_SESSION, USING_DEFAULT_API, PROXY_ENABLED, PROXY_TYPE, PROXY_HOST,
    WEB_PORT, AVATAR_DIR, AUTOSTART_IDS, GITHUB_RAW_URL, REQUIREMENTS_URL,
    get_telethon_proxy,
)
from logger import info, success, error, warning, exception, log
from database import init_db, cleanup_old_data


VERSION_PATTERN = re.compile(r'VERSION\s*=\s*[\'"](v\d+\.\d+\.\d+)[\'"]')
PHONE_RE = re.compile(r'^\+\d{8,15}$')

def load_command_modules():
    commands_dir = Path(__file__).parent / "commands"
    if not commands_dir.exists():
        return
    loaded = 0
    for f in commands_dir.iterdir():
        if f.suffix != ".py" or f.name.startswith("_"):
            continue
        module_name = f"commands.{f.stem}"
        try:
            importlib.import_module(module_name)
            loaded += 1
        except Exception as e:
            log.exception(f"загрузка {module_name}: {e}")
    log.info(f"загружено модулей команд: {loaded}")

load_command_modules()

from commands import get_all
from web import WebPanel


def print_block(title, icon="●", color=None):
    color = color or COLORS["accent1"]
    width = 54
    print(f"{COLORS['accent2']}┏{'━' * width}┓{COLORS['reset']}")
    padding = width - len(title) - 4
    print(f"{COLORS['accent2']}┃{COLORS['reset']} {color}{icon}{COLORS['reset']} {COLORS['header']}{title}{COLORS['reset']}"
          f"{' ' * padding}{COLORS['accent2']}┃{COLORS['reset']}")
    print(f"{COLORS['accent2']}┗{'━' * width}┛{COLORS['reset']}")


def print_kv(key, value, color=None):
    color = color or COLORS["input"]
    print(f"  {COLORS['accent2']}›{COLORS['reset']} {COLORS['info']}{key}:{COLORS['reset']} {color}{value}{COLORS['reset']}")


def banner():
    print(f"""{COLORS['accent1']}                __    ___  {COLORS['accent3']}___    ___  _____ {COLORS['reset']}
{COLORS['accent1']}  /\\  /\\/\\ /\\  /__\\  /___\\{COLORS['accent3']}/ __\\  /___\\/__   \\ {COLORS['reset']}
{COLORS['accent1']} / /_/ / / \\ \\/ \\// //  /{COLORS['accent3']}/__\\// //  //  / /\\/ {COLORS['reset']}
{COLORS['accent1']}/ __  /\\ \\_/ / _  \\/ \\_/{COLORS['accent3']}/ \\/  \\/ \\_//  / /    {COLORS['reset']}
{COLORS['accent1']}\\/ /_/  \\___/\\/ \\_/\\___/{COLORS['accent3']}\\_____/\\___/   \\/     {COLORS['reset']}

{COLORS['header']}                    {VERSION} {COLORS['accent2']}//{COLORS['accent3']} @hurodev{COLORS['reset']}""")


def check_updates():
    """Проверка новой версии на GitHub."""
    try:
        req = urllib.request.Request(
            GITHUB_RAW_URL,
            headers={"User-Agent": "HuroBot-Updater"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            remote = resp.read().decode("utf-8")

        m = VERSION_PATTERN.search(remote)
        if not m:
            return

        remote_version = m.group(1)
        if remote_version == VERSION:
            info(f"Обновлений нет ({VERSION})")
            return

        print()
        print_block(f"Доступно обновление: {remote_version}", icon="⬆", color=COLORS["success"])
        print_kv("Текущая", VERSION)
        print_kv("Новая", remote_version, COLORS["success"])
        print()

        answer = input(f"{COLORS['header']}Обновить сейчас? (y/N): {COLORS['reset']}").strip().lower()
        if answer not in ("y", "yes", "д", "да"):
            info("Обновление отложено")
            return

        script_path = Path(__file__).resolve()
        temp_path = script_path.with_suffix(".py.new")

        temp_path.write_text(remote, encoding="utf-8")

        try:
            compile(temp_path.read_text(encoding="utf-8"), str(temp_path), "exec")
        except SyntaxError as e:
            error(f"Синтаксическая ошибка в новой версии: {e}")
            temp_path.unlink()
            return

        backup = script_path.with_suffix(".py.bak")
        if backup.exists():
            backup.unlink()
        script_path.rename(backup)
        temp_path.rename(script_path)

        success("Обновлено. Перезапусти бота вручную.")
        input(f"{COLORS['input']}Нажми Enter для выхода...{COLORS['reset']}")
        sys.exit(0)

    except Exception as e:
        warning(f"Проверка обновлений не удалась: {e}")


def fmt_uptime(seconds):
    if seconds < 60:
        return f"{seconds}с"
    m, s = divmod(seconds, 60)
    if m < 60:
        return f"{m}м {s}с"
    h, m = divmod(m, 60)
    if h < 24:
        return f"{h}ч {m}м"
    d, h = divmod(h, 24)
    return f"{d}д {h}ч"


class HuroBot:
    def __init__(self):
        self.accounts = {}
        self.running = set()
        self.clients = {}
        self.pending_auth = {}
        self.autostart = set(AUTOSTART_IDS)
        self.started_at = {}
        self.starting = set()

    async def load_accounts(self):
        self.accounts = {}
        for f in SESSION_DIR.iterdir():
            if not f.name.startswith(SESSION_PREFIX) or f.suffix != ".session":
                continue
            try:
                client = make_client(str(f))
                async with client:
                    if await client.is_user_authorized():
                        me = await client.get_me()
                        account_id = int(f.stem.split("_")[1])
                        self.accounts[account_id] = {
                            "phone": me.phone,
                            "name": me.username or me.first_name or f"Аккаунт {account_id}",
                            "session": str(f),
                        }
            except Exception:
                exception(f"Загрузка сессии {f.name}")

    async def refresh_avatar(self, num):
        acc = self.accounts.get(num)
        if not acc:
            return {"ok": False, "error": "аккаунт не найден"}

        try:
            client = make_client(acc["session"])
            async with client:
                if not await client.is_user_authorized():
                    return {"ok": False, "error": "сессия не авторизована"}
                me = await client.get_me()
                path = AVATAR_DIR / f"{num}.jpg"
                downloaded = await client.download_profile_photo(me, file=str(path))
                if not downloaded:
                    return {"ok": False, "error": "у аккаунта нет аватарки"}
            success(f"Аватарка #{num} обновлена")
            return {"ok": True}
        except Exception as e:
            exception(f"refresh_avatar {num}")
            return {"ok": False, "error": str(e)}

    async def start_account(self, num):
        if num in self.running:
            return {"ok": True, "message": "уже запущен"}
        if num in self.starting:
            return {"ok": False, "error": "запуск уже идёт"}

        acc = self.accounts.get(num)
        if not acc:
            return {"ok": False, "error": "аккаунт не найден"}
        self.starting.add(num)
        try:
            name = acc["name"]
            phone = acc["phone"]
            info(f"аккаунт #{num} — {name} (+{phone})")

            client = make_client(acc["session"])

            try:
                await asyncio.wait_for(client.connect(), timeout=15)
            except asyncio.TimeoutError:
                print_kv("Статус", "таймаут подключения", COLORS["error"])
                return {"ok": False, "error": "таймаут подключения"}
            except Exception as e:
                exception("start_account.connect")
                print_kv("Статус", f"ошибка: {e}", COLORS["error"])
                return {"ok": False, "error": str(e)}

            if not await client.is_user_authorized():
                print_kv("Статус", "сессия не авторизована", COLORS["error"])
                await client.disconnect()
                return {"ok": False, "error": "сессия не авторизована"}

            state = ClientState()
            client._hurobot_state = state

            @client.on(events.NewMessage(incoming=True))
            async def _stats(event):
                await stats_collector(event)

            loaded = 0
            for register_fn in get_all():
                try:
                    register_fn(client, state)
                    loaded += 1
                except Exception:
                    exception(f"Загрузка {register_fn.__name__}")

            self.clients[num] = client
            self.running.add(num)
            self.started_at[num] = asyncio.get_event_loop().time()

            if not (AVATAR_DIR / f"{num}.jpg").exists():
                asyncio.create_task(self.refresh_avatar(num))

            print_kv("Команд", str(loaded))
            print_kv("Статус", "запущен", COLORS["success"])
            log.info(f"Аккаунт #{num} ({name}) запущен")
            print()

            asyncio.create_task(self._run_client(num, client))

            return {"ok": True, "message": f"аккаунт {name} запущен"}

        finally:
            self.starting.discard(num)

    async def _run_client(self, num, client):
        acc = self.accounts.get(num, {})
        name = acc.get("name", f"#{num}")
        try:
            while num in self.running:
                try:
                    await client.run_until_disconnected()
                    break
                except (ConnectionError, TimeoutError, TimedOutError):
                    warning(f"Аккаунт {name}: соединение потеряно, переподключение...")
                    await asyncio.sleep(5)
                    try:
                        await client.connect()
                    except Exception:
                        await asyncio.sleep(30)
        except Exception:
            exception(f"_run_client {num}")
        finally:
            self.running.discard(num)
            self.clients.pop(num, None)
            self.started_at.pop(num, None)
            self.starting.discard(num)
            warning(f"Аккаунт {name}: остановлен")

    async def stop_account(self, num):
        acc = self.accounts.get(num, {})
        name = acc.get("name", f"#{num}")
        self.starting.discard(num)
        if num in self.running:
            self.running.discard(num)
        client = self.clients.pop(num, None)
        if client:
            try:
                if client.is_connected():
                    await client.disconnect()
            except Exception:
                pass
        self.started_at.pop(num, None)

        print()
        print_block(f"Остановка аккаунта #{num}", icon="🛑", color=COLORS["error"])
        print_kv("Имя", name)
        print_kv("Статус", "остановлен", COLORS["error"])
        print()
        return {"ok": True}

    async def delete_account(self, num):
        acc = self.accounts.get(num)
        if not acc:
            return {"ok": False, "error": "аккаунт не найден"}

        await self.stop_account(num)

        try:
            p = Path(acc["session"])
            if p.exists():
                p.unlink()
        except Exception:
            exception(f"Удаление {acc['session']}")

        avatar = AVATAR_DIR / f"{num}.jpg"
        if avatar.exists():
            avatar.unlink()

        self.accounts.pop(num, None)
        self.autostart.discard(num)

        print_kv("Удалён", f"аккаунт #{num}", COLORS["error"])
        return {"ok": True}

    async def start_add_account(self, phone):
        clean = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not clean.startswith("+"):
            clean = "+" + clean.lstrip("+")
        if not PHONE_RE.match(clean):
            return {"ok": False, "error": "неверный формат номера. пример: +79123456789"}
        phone = clean

        p = Path(TEMP_SESSION)
        for suffix in ("", "-journal", "-wal", "-shm"):
            fp = Path(str(p) + suffix)
            if fp.exists():
                try:
                    fp.unlink()
                except PermissionError:
                    pass

        client = None
        try:
            print()
            print_block("Добавление аккаунта", icon="➕")
            print_kv("Телефон", phone)

            client = make_client(TEMP_SESSION)
            await asyncio.wait_for(client.connect(), timeout=15)
            sent = await client.send_code_request(phone)

            self.pending_auth[phone] = {
                "client": client,
                "phone_code_hash": sent.phone_code_hash,
                "stage": "code",
            }

            print_kv("Статус", "код отправлен", COLORS["success"])
            return {"ok": True, "stage": "code"}

        except PhoneNumberInvalidError:
            if client and client.is_connected():
                await client.disconnect()
            return {"ok": False, "error": "неверный номер"}
        except asyncio.TimeoutError:
            if client and client.is_connected():
                await client.disconnect()
            return {"ok": False, "error": "таймаут подключения"}
        except Exception as e:
            exception("start_add_account")
            if client and client.is_connected():
                try:
                    await client.disconnect()
                except Exception:
                    pass
            return {"ok": False, "error": str(e)}

    async def complete_add_account(self, phone, code=None, password=None):
        pending = self.pending_auth.get(phone)
        if not pending:
            return {"ok": False, "error": "сессия истекла"}

        client = pending["client"]

        try:
            if password is None:
                try:
                    await client.sign_in(phone, code=code, phone_code_hash=pending["phone_code_hash"])
                except SessionPasswordNeededError:
                    print_kv("2FA", "требуется пароль")
                    return {"ok": False, "need_password": True}
            else:
                try:
                    await client.sign_in(password=password)
                except PasswordHashInvalidError:
                    print_kv("2FA", "неверный пароль", COLORS["error"])
                    return {"ok": False, "error": "неверный пароль"}

            me = await client.get_me()
            account_id = max(self.accounts.keys(), default=0) + 1
            new_session = SESSION_DIR / f"{SESSION_PREFIX}{account_id}.session"

            try:
                path = AVATAR_DIR / f"{account_id}.jpg"
                await client.download_profile_photo(me, file=str(path))
            except Exception:
                pass

            await client.disconnect()
            await asyncio.sleep(1)

            p = Path(TEMP_SESSION)
            if p.exists():
                if new_session.exists():
                    new_session.unlink()
                p.rename(new_session)

            self.accounts[account_id] = {
                "phone": phone,
                "name": me.first_name or me.username or f"Аккаунт {account_id}",
                "session": str(new_session),
            }

            self.pending_auth.pop(phone, None)
            print_kv("Аккаунт", f"{me.first_name} добавлен", COLORS["success"])
            print()
            log.info(f"Добавлен аккаунт: {me.first_name}")
            return {"ok": True}

        except PhoneCodeInvalidError:
            return {"ok": False, "error": "неверный код"}
        except Exception as e:
            exception("complete_add_account")
            return {"ok": False, "error": str(e)}

    async def autostart_accounts(self):
        for num in sorted(self.autostart):
            if num in self.accounts and num not in self.running and num not in self.starting:
                info(f"Автостарт аккаунта #{num}")
                await self.start_account(num)
                await asyncio.sleep(1)


class ClientState:
    def __init__(self):
        self.typing_animation = False
        self.active_animation = None
        self.animation_lock = asyncio.Lock()
        self.pending_confirmation = {}
        self.current_message_id = None
        self.last_user_activity = 0

    async def stop_animation(self):
        async with self.animation_lock:
            if self.active_animation:
                self.active_animation.cancel()
                try:
                    await self.active_animation
                except Exception:
                    pass
                self.active_animation = None
            self.current_message_id = None


def make_client(session_path):
    proxy, connection = get_telethon_proxy()
    kwargs = {"proxy": proxy} if proxy else {}
    if connection:
        kwargs["connection"] = connection
    return TelegramClient(session_path, API_ID, API_HASH, **kwargs)


async def stats_collector(event):
    from database import db
    try:
        if not event.is_private:
            return
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with db() as conn:
            conn.execute(
                """INSERT INTO stats (user_id, chat_id, date, msg_count) VALUES (?, ?, ?, 1)
                   ON CONFLICT(user_id, chat_id, date) DO UPDATE SET msg_count = msg_count + 1""",
                (event.sender_id, event.chat_id, today),
            )
    except Exception:
        pass

async def main():
    banner()
    print()

    if USING_DEFAULT_API:
        warning("используются публичные api-ключи, лучше ввести свои через .env")
    if PROXY_ENABLED:
        info(f"прокси: {PROXY_TYPE}://{PROXY_HOST}")
    else:
        info("прокси не задан")

    init_db()
    cleanup_old_data(days=30)

    check_updates()

    bot = HuroBot()
    await bot.load_accounts()

    panel = WebPanel(bot, host="127.0.0.1", port=WEB_PORT)
    await panel.start()

    print()
    print(f"{COLORS['accent1']}●{COLORS['reset']} {COLORS['header']}управление — только через веб-панель{COLORS['reset']}")
    print(f"{COLORS['accent2']}  →{COLORS['reset']} {COLORS['accent4']}http://127.0.0.1:{WEB_PORT}{COLORS['reset']}")
    print()
    print(f"{COLORS['accent1']}●{COLORS['reset']} {COLORS['info']}аккаунтов загружено:{COLORS['reset']} {COLORS['accent3']}{len(bot.accounts)}{COLORS['reset']}")
    print(f"{COLORS['accent1']}●{COLORS['reset']} {COLORS['info']}запущено сейчас:{COLORS['reset']} {COLORS['accent3']}{len(bot.running)}{COLORS['reset']}")
    print()
    print(f"{COLORS['accent2']}  →{COLORS['reset']} {COLORS['info']}Ctrl+C — остановить бота{COLORS['reset']}")
    print()

    if bot.autostart:
        asyncio.create_task(bot.autostart_accounts())

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        for num in list(bot.running):
            await bot.stop_account(num)
        await panel.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        info("Завершено")
        sys.exit(0)
    except Exception:
        exception("main")
        sys.exit(1)