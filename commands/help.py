from telethon import events
from commands import register
from commands.utils import safe_edit, COMMAND_INFO, fmt


HELP_TEXT = """**✦ помощь**

**✧ основное**
  `.help` — список команд
  `.ping` — проверка
  `.bot` — о боте

**✧ аккаунт**
  `.delme` — очистка переписки

**✧ медиа**
  `.save` — сохранить T-медиа
  `.qr <текст>` — QR-код
  `.clone <url>` — клон поста

**✧ модерация (только в лс)**
  `.mute` — мут в лс / ответом
  `.mute 1h` — на час
  `.unmute` — снять мут
  `.mutes` — список
  `.muteword <слово>` — мут по слову
  `.tagall` — упомянуть всех
  `.up <N>` — переупоминания
  `.iter [-n]` — экспорт участников

**✧ osint**
  `.data` — инфо о юзере
  `.osint <значение>` — IP / телефон / почта
  `.whois <домен>` — WHOIS

**✧ спам**
  `.spam <N> <текст>` — рассылка
  `.sti <N>` — стикеры
  `.crash` — краш-стикеры
  `.bomb <номер>` — бомбер

**✧ утилиты**
  `.short <url>` — сокращение ссылок
  `.ani on/off` — анимация набора
  `.random 1-100` — случайное число
  `.dice` — кубик

**✧ статистика**
  `.stat` — за сегодня
  `.top` — топ чатов
  `.digest` — сводка за день

**HURObot** // @hurodev
"""


@register
def register_help(client, state):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.help(?:\s+([a-zA-Z]+))?$'))
    async def help_handler(event):
        command = event.pattern_match.group(1)
        if not command:
            await safe_edit(event, HELP_TEXT)
            return
        command = command.lower()
        if command not in COMMAND_INFO:
            await safe_edit(event, fmt("ошибка", [f"команда `{command}` не найдена"]))
            return
        info = COMMAND_INFO[command]
        text = (
            f"**✦ команда: {command}**\n\n"
            f"**✧** описание — {info['description']}\n"
            f"**✧** синтаксис — {info['syntax']}\n"
            f"**✧** пример — {info['example']}\n\n"
            f"**HURObot** // @hurodev"
        )
        await safe_edit(event, text)