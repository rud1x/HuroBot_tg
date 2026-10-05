import random
import asyncio
from telethon import events
from telethon.errors import FloodWaitError
from commands import register
from commands.utils import safe_edit, fmt, get_usage_instructions


@register
def register_accounts(client, state):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.delme(?:\s+(\d+))?$'))
    async def delme_handler(event):
        state.last_user_activity = __import__("time").time()
        code = event.pattern_match.group(1)

        if not code:
            confirm_code = "".join(random.choices("0123456789", k=4))
            state.pending_confirmation[event.chat_id] = confirm_code
            await safe_edit(event, fmt("подтверждение удаления", [
                "будет удалена вся переписка в этом чате",
                f"введи `.delme {confirm_code}`",
            ]))
            return

        if state.pending_confirmation.get(event.chat_id) != code:
            await safe_edit(event, fmt("ошибка", ["неверный код"]))
            return

        try:
            all_messages = []
            async for message in client.iter_messages(event.chat_id, from_user="me", reverse=True):
                all_messages.append(message)

            total = len(all_messages)
            if total == 0:
                await safe_edit(event, fmt("сообщений не найдено"))
                return

            deleted = 0
            progress = await event.edit(f"**✦ удаление**\n\n**✧** 0/{total}")

            for idx, msg in enumerate(all_messages, 1):
                try:
                    await msg.delete()
                    deleted += 1
                    if idx % 3 == 0:
                        await progress.edit(f"**✦ удаление**\n\n**✧** {deleted}/{total}")
                    await asyncio.sleep(1)
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds + 2)
                except Exception:
                    continue

            await progress.delete()
            result = await client.send_message(
                event.chat_id,
                fmt("удалено", [f"`{deleted}/{total}` сообщений"]),
                parse_mode="md",
            )
            await asyncio.sleep(5)
            await result.delete()
        except Exception as e:
            await safe_edit(event, fmt("ошибка", [f"`{e}`"]))
        finally:
            state.pending_confirmation.pop(event.chat_id, None)