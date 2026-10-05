import asyncio
import time
from datetime import datetime
import pytz
from telethon import events
from telethon.errors import MessageNotModifiedError
from commands import register
from config import VERSION, GITHUB_RAW_URL
from logger import exception


def fmt(title, rows=None):
    lines = [f"**✦ {title}**"]
    if rows:
        lines.append("")
        for row in rows:
            lines.append(f"**✧** {row}")
    lines.append("")
    lines.append("**HURObot** // @hurodev")
    return "\n".join(lines)


def get_moscow_time():
    return datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")


COMMAND_INFO = {
    "help": {
        "description": "Показывает список всех команд или справку по конкретной.",
        "syntax": "`.help` [команда]",
        "example": "`.help save`",
    },
    "save": {
        "description": "Сохраняет самоудаляющееся фото из личного чата в избранное.",
        "syntax": "`.save` (ответом на фото)",
        "example": "`.save`",
    },
    "clone": {
        "description": "Клонирует пост из канала в избранное по ссылке.",
        "syntax": "`.clone` [url]",
        "example": "`.clone https://t.me/channel/123`",
    },
    "short": {
        "description": "Сокращает URL через tinyurl.",
        "syntax": "`.short` [url]",
        "example": "`.short https://example.com`",
    },
    "delme": {
        "description": "Удаляет всю переписку в текущем чате после подтверждения.",
        "syntax": "`.delme` [код]",
        "example": "`.delme 1234`",
    },
    "ani": {
        "description": "Включает или выключает анимацию набора текста.",
        "syntax": "`.ani` [on/off]",
        "example": "`.ani on`",
    },
    "sti": {
        "description": "Отправляет указанное количество стикеров в ответ на стикер.",
        "syntax": "`.sti` [число]",
        "example": "`.sti 10`",
    },
    "tagall": {
        "description": "Упоминает всех участников чата через @username.",
        "syntax": "`.tagall`",
        "example": "`.tagall`",
    },
    "iter": {
        "description": "Экспортирует участников чата в файл и отправляет в избранное.",
        "syntax": "`.iter` [-n]",
        "example": "`.iter -n`",
    },
    "up": {
        "description": "Многократные упоминания пользователя с удалением.",
        "syntax": "`.up` [число]",
        "example": "`.up 5`",
    },
    "data": {
        "description": "Информация о пользователе.",
        "syntax": "`.data` (ответом на сообщение)",
        "example": "`.data`",
    },
    "osint": {
        "description": "Проверка данных по IP / номеру / почте.",
        "syntax": "`.osint` [значение]",
        "example": "`.osint 8.8.8.8`",
    },
    "whois": {
        "description": "Информация о домене.",
        "syntax": "`.whois` [домен]",
        "example": "`.whois google.com`",
    },
    "spam": {
        "description": "Отправляет указанное количество одинаковых сообщений.",
        "syntax": "`.spam` [количество] [текст]",
        "example": "`.spam 10 Привет`",
    },
    "crash": {
        "description": "Отправляет стикеры, нагружающие телефон.",
        "syntax": "`.crash`",
        "example": "`.crash`",
    },
    "bomb": {
        "description": "Спам-атака на номер телефона (5 минут).",
        "syntax": "`.bomb` [номер]",
        "example": "`.bomb +79123456789`",
    },
    "bot": {
        "description": "Информация о боте.",
        "syntax": "`.bot`",
        "example": "`.bot`",
    },
    "ping": {
        "description": "Проверка отклика.",
        "syntax": "`.ping`",
        "example": "`.ping`",
    },
}


def get_usage_instructions(name, status=None):
    info = COMMAND_INFO.get(name)
    if not info:
        return fmt("ошибка", [f"нет справки для `{name}`"])
    rows = []
    if status:
        rows.append(f"статус — `{status}`")
    rows.append(f"описание — {info['description']}")
    rows.append(f"синтаксис — {info['syntax']}")
    rows.append(f"пример — {info['example']}")
    return fmt(name, rows)


async def safe_edit(event, text, parse_mode="md", **kwargs):
    try:
        return await event.edit(text, parse_mode=parse_mode, **kwargs)
    except MessageNotModifiedError:
        pass
    except Exception as e:
        exception(f"safe_edit: {e}")


async def shorten_url(url):
    import requests
    try:
        response = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=10)
        response.raise_for_status()
        return response.text
    except Exception:
        return url


@register
def register_utils(client, state):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ping$'))
    async def ping_handler(event):
        start = time.time()
        await safe_edit(event, "**✦ pong**")
        delta = round((time.time() - start) * 1000)
        await safe_edit(event, fmt("pong", [f"{delta}ms"]))

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.short(?:\s+(.+))?$'))
    async def short_handler(event):
        state.last_user_activity = time.time()
        url = event.pattern_match.group(1)
        if not url:
            await safe_edit(event, get_usage_instructions("short"))
            return
        if not url.startswith("http"):
            await safe_edit(event, fmt("ошибка", ["укажи действительный URL"]))
            return
        short_url = await shorten_url(url)
        await safe_edit(event, fmt("сокращение", [
            f"исходный — `{url}`",
            f"короткий — `{short_url}`",
        ]))

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ani(?:\s+(on|off))?$'))
    async def ani_handler(event):
        state.last_user_activity = time.time()
        action = event.pattern_match.group(1)
        if not action:
            status = "включена" if state.typing_animation else "выключена"
            await safe_edit(event, get_usage_instructions("ani", status=status))
            return
        new_state = action.lower() == "on"
        if new_state == state.typing_animation:
            status = "включена" if state.typing_animation else "выключена"
            await safe_edit(event, fmt("анимация уже " + status))
            return
        state.typing_animation = new_state
        status = "включена" if new_state else "выключена"
        await safe_edit(event, fmt(f"анимация {status}"))
        if not new_state:
            await state.stop_animation()

    @client.on(events.NewMessage(outgoing=True))
    async def animate_message(event):
        state.last_user_activity = time.time()
        if not state.typing_animation or not event.text or event.text.startswith("."):
            return
        try:
            await state.stop_animation()
            current = ""
            await asyncio.sleep(0.1)
            for char in event.text:
                if not state.typing_animation:
                    break
                current += char
                try:
                    await event.edit(current)
                    await asyncio.sleep(0.05)
                except MessageNotModifiedError:
                    continue
                except Exception:
                    break
        except Exception:
            exception("animate_message")