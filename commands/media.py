import io
import os
import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.types import DocumentAttributeFilename
from commands import register
from commands.utils import fmt, safe_edit, get_moscow_time
from config import TEMP_DIR
from logger import exception

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import qrcode
except ImportError:
    qrcode = None


MESSAGE_CACHE = {}


def compress_image(image_bytes):
    if not Image:
        return image_bytes
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("RGB")
        img.thumbnail((500, 500), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=85)
        return out.getvalue()
    except Exception:
        return image_bytes


def _get_ttl(obj):
    return getattr(obj, "ttl_seconds", None)


async def save_self_destruct_photo(client, event):
    try:
        if not event.is_private:
            return False
        ttl = _get_ttl(event) or _get_ttl(getattr(event, "media", None))
        if not ttl or ttl <= 0:
            return False
        if not hasattr(event.media, "photo"):
            return False

        data = await client.download_media(event.media, file=bytes)
        if not data:
            return False

        data = compress_image(data)

        sender = await event.get_sender()
        username = getattr(sender, "username", None) or getattr(sender, "first_name", "unknown")

        caption = (
            f"**✦ сохранено**\n\n"
            f"**✧** от — `{username}`\n"
            f"**✧** время — `{get_moscow_time()}`\n"
            f"**✧** id — `{event.id}`\n\n"
            f"**HURObot** // @hurodev"
        )

        await client.send_file(
            "me",
            data,
            caption=caption,
            force_document=False,
            attributes=[DocumentAttributeFilename(file_name=f"self_destruct_{event.id}.jpg")],
            parse_mode="md",
        )
        return True
    except Exception:
        exception("save_self_destruct_photo")
        return False


async def save_deleted_message(client, event):
    try:
        if not event.is_private:
            return
        for msg_id in event.deleted_ids:
            try:
                cached = MESSAGE_CACHE.get(event.chat_id, {}).get(msg_id)
                msg = await client.get_messages(event.chat_id, ids=msg_id)

                if msg is None and not cached:
                    continue

                sender_name = "unknown"
                sender_username = ""
                date_str = get_moscow_time()

                if msg is not None:
                    sender = await msg.get_sender()
                    if sender:
                        sender_name = getattr(sender, "first_name", None) or "unknown"
                        sender_username = getattr(sender, "username", None) or ""
                    if msg.date:
                        date_str = msg.date.astimezone(
                            __import__("pytz").timezone("Europe/Moscow")
                        ).strftime("%d.%m.%Y %H:%M:%S")

                caption = (
                    f"**✦ удалённое сообщение**\n\n"
                    f"**✧** от — `{sender_name}`"
                    + (f" (@{sender_username})" if sender_username else "") + "\n"
                    f"**✧** отправлено — `{date_str}`\n"
                    f"**✧** удалено — `{get_moscow_time()}`\n"
                )

                text_content = ""
                if msg is not None and msg.text:
                    text_content = f"\n**✧** текст — `{msg.text}`\n"
                elif cached and cached.get("text"):
                    text_content = f"\n**✧** текст — `{cached['text']}`\n"

                full_caption = caption + text_content + "\n**HURObot** // @hurodev"

                if msg is not None and msg.media:
                    media = await client.download_media(msg.media)
                    if media:
                        await client.send_file("me", media, caption=full_caption, force_document=True, parse_mode="md")
                        try:
                            os.remove(media)
                        except Exception:
                            pass
                        continue

                await client.send_message("me", full_caption, parse_mode="md")
            except Exception:
                continue
    except Exception:
        exception("save_deleted_message")


async def cache_message_handler(event):
    try:
        if not event.is_private:
            return
        chat_id = event.chat_id
        if chat_id not in MESSAGE_CACHE:
            MESSAGE_CACHE[chat_id] = {}
        if len(MESSAGE_CACHE[chat_id]) > 100:
            oldest = min(MESSAGE_CACHE[chat_id].keys())
            del MESSAGE_CACHE[chat_id][oldest]
        msg = event.message
        MESSAGE_CACHE[chat_id][msg.id] = {
            "text": msg.text,
            "date": msg.date,
            "has_media": bool(msg.media),
            "sender_id": msg.sender_id,
        }
    except Exception:
        pass


@register
def register_media(client, state):
    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def auto_save_media(event):
        await cache_message_handler(event)
        await save_self_destruct_photo(client, event)

    @client.on(events.MessageDeleted())
    async def deleted_handler(event):
        await save_deleted_message(client, event)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.save$'))
    async def manual_save(event):
        try:
            await event.delete()
        except Exception:
            pass

        if not event.is_reply:
            return

        reply = await event.get_reply_message()
        if not reply or not reply.media:
            return

        try:
            data = await client.download_media(reply.media, file=bytes)
            if not data:
                return

            if hasattr(reply.media, "photo"):
                data = compress_image(data)

            sender = await reply.get_sender()
            username = getattr(sender, "username", None) or getattr(sender, "first_name", "unknown")

            caption = (
                f"**✦ сохранено**\n\n"
                f"**✧** от — `{username}`\n"
                f"**✧** время — `{get_moscow_time()}`\n"
                f"**✧** id — `{reply.id}`\n\n"
                f"**HURObot** // @hurodev"
            )

            await client.send_file(
                "me",
                data,
                caption=caption,
                force_document=False,
                attributes=[DocumentAttributeFilename(file_name=f"saved_{reply.id}.jpg")],
                parse_mode="md",
            )
        except Exception:
            exception("manual_save")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.clone(?:\s+(.+))?$'))
    async def clone_handler(event):
        post_link = event.pattern_match.group(1)
        if not post_link:
            from commands.utils import get_usage_instructions
            await safe_edit(event, get_usage_instructions("clone"))
            return
        if not post_link.startswith("https://t.me/"):
            await safe_edit(event, fmt("ошибка", ["формат: `.clone https://t.me/канал/123`"]))
            return
        try:
            parts = post_link.split("/")
            channel = parts[-2]
            post_id = int(parts[-1])
            entity = await client.get_entity(channel)
            message = await client.get_messages(entity, ids=post_id)
            if message is None:
                await safe_edit(event, fmt("ошибка", ["пост не найден"]))
                return
            if message.media:
                await client.send_file("me", message.media, caption=message.text or "")
            else:
                await client.send_message("me", message.text or "пустой пост")
            await safe_edit(event, fmt("клонирование выполнено", ["сохранено в избранное"]))
        except Exception as e:
            await safe_edit(event, fmt("ошибка", [f"`{e}`"]))

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.qr(?:\s+(.+))?$'))
    async def qr_handler(event):
        try:
            await event.delete()
        except Exception:
            pass

        text = event.pattern_match.group(1)
        if not text:
            return
        if not qrcode:
            return

        try:
            img = qrcode.make(text)
            path = TEMP_DIR / f"qr_{event.id}.png"
            img.save(str(path))
            await client.send_file(
                "me",
                str(path),
                caption=(
                    f"**✦ qr готов**\n\n"
                    f"**✧** текст — `{text[:60]}`\n\n"
                    f"**HURObot** // @hurodev"
                ),
                parse_mode="md",
            )
            path.unlink(missing_ok=True)
        except Exception:
            exception("qr_handler")