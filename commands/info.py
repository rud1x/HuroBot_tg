from telethon import events
from commands import register
from commands.utils import safe_edit, fmt, get_moscow_time
from config import VERSION, GITHUB_RAW_URL


@register
def register_info(client, state):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.bot$'))
    async def bot_info_handler(event):
        repo_url = GITHUB_RAW_URL.rsplit("/", 2)[0]
        await safe_edit(event, fmt("hurobot", [
            f"версия — `{VERSION}`",
            f"разработчик — @therudix",
            f"github — [исходник]({repo_url})",
            f"канал — @hurodev",
            f"лицензия — MIT",
            f"время — `{get_moscow_time()}`",
        ]))