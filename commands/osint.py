import re
import subprocess
import requests
import whois as whois_lib
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from commands import register
from commands.utils import safe_edit, fmt


@register
def register_osint(client, state):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.data$'))
    async def data_handler(event):
        if not event.is_reply:
            from commands.utils import get_usage_instructions
            await safe_edit(event, get_usage_instructions("data"))
            return
        try:
            reply = await event.get_reply_message()
            user = await reply.get_sender()
            full_user = await client(GetFullUserRequest(user))

            rows = [f"id — `{user.id}`", f"имя — `{user.first_name or 'нет'}`"]
            if getattr(user, "phone", None):
                rows.append(f"телефон — `{user.phone}`")
            status = getattr(user, "status", None)
            if status:
                if hasattr(status, "was_online"):
                    rows.append(f"был онлайн — `{status.was_online.strftime('%Y-%m-%d %H:%M:%S')}`")
                if hasattr(status, "created"):
                    rows.append(f"регистрация — `{status.created.strftime('%Y-%m-%d %H:%M:%S')}`")
            about = getattr(full_user, "about", None)
            if about:
                rows.append(f"о себе — `{about[:100]}`")
            await safe_edit(event, fmt("данные пользователя", rows))
        except Exception as e:
            await safe_edit(event, fmt("ошибка", [f"`{e}`"]))

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.osint(?:\s+(.+))?$'))
    async def osint_handler(event):
        args = event.text.split(" ", 1)
        if len(args) < 2:
            from commands.utils import get_usage_instructions
            await safe_edit(event, get_usage_instructions("osint"))
            return
        target = args[1].strip()
        try:
            if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', target):
                await _ip_lookup(event, target)
            elif "@" in target:
                await _mail_lookup(event, target)
            elif re.match(r'^\+?[\d\s\-()]{7,}$', target):
                await _phone_lookup(event, target)
            else:
                await safe_edit(event, fmt("ошибка", ["неверный формат данных"]))
        except Exception as e:
            await safe_edit(event, fmt("ошибка", [f"`{e}`"]))

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.whois(?:\s+(.+))?$'))
    async def whois_handler(event):
        args = event.text.split(" ", 1)
        if len(args) < 2:
            from commands.utils import get_usage_instructions
            await safe_edit(event, get_usage_instructions("whois"))
            return
        domain = args[1].strip()
        try:
            info = whois_lib.whois(domain)
            rows = [
                f"домен — `{info.domain_name}`",
                f"создан — `{info.creation_date}`",
                f"истекает — `{info.expiration_date}`",
                f"регистратор — `{info.registrar}`",
            ]
            ns = info.name_servers
            if ns:
                rows.append(f"ns — `{', '.join(ns) if isinstance(ns, list) else ns}`")
            await safe_edit(event, fmt("whois", rows))
        except Exception as e:
            await safe_edit(event, fmt("ошибка", [f"`{e}`"]))


async def _ip_lookup(event, ip):
    try:
        data = requests.get(f"http://ipwho.is/{ip}", timeout=10).json()
        if not data.get("success"):
            await safe_edit(event, fmt("ошибка", ["не удалось получить данные"]))
            return
        rows = [
            f"ip — `{ip}`",
            f"провайдер — `{data['connection']['isp']}`",
            f"страна — `{data['country']}`",
            f"город — `{data['city']}`",
            f"координаты — `{data['latitude']}, {data['longitude']}`",
        ]
        await safe_edit(event, fmt("ip", rows))
    except Exception as e:
        await safe_edit(event, fmt("ошибка", [f"`{e}`"]))


async def _phone_lookup(event, phone):
    try:
        r = requests.get(
            f"https://htmlweb.ru/geo/api.php?json&telcod={phone}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        data = r.json()
        if data.get("limit") == 0:
            await safe_edit(event, fmt("ошибка", ["лимит запросов, включи vpn"]))
            return
        rows = [
            f"номер — `{phone}`",
            f"страна — `{data.get('country', {}).get('name', 'N/A')}`",
            f"оператор — `{data.get('0', {}).get('oper', 'N/A')}`",
        ]
        await safe_edit(event, fmt("номер", rows))
    except Exception as e:
        await safe_edit(event, fmt("ошибка", [f"`{e}`"]))


async def _mail_lookup(event, mail):
    try:
        result = subprocess.run(
            f"holehe {mail}",
            capture_output=True, text=True, shell=True, check=True, timeout=120,
        )
        lines = result.stdout.split("\n")[4:-4]
        output = "\n".join(
            line.replace("[x]", "✖").replace("[-]", "—").replace("[+]", "✔")
            for line in lines
        )
        await safe_edit(event, fmt("почта", [f"`{mail}`", output[:900]]))
    except Exception as e:
        await safe_edit(event, fmt("ошибка", [f"`{e}`"]))