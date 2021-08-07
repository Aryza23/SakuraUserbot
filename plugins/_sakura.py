# Sakura - UserBot

from telethon.errors import ChatSendInlineForbiddenError
from telethon.errors.rpcerrorlist import BotMethodInvalidError as bmi

from . import *

REPOMSG = (
    "🌸 **SAKURA USERBOT** 🌸\n\n",
    "• REPO - [KLIK DISINI](https://github.com/levina-lab/SakuraUserbot)\n",
    "• ADDONS - [KLIK DISINI](https://github.com/levina-lab/scyaddons)\n",
    "• SUPPORT - @levinachannel",
)


@ultroid_cmd(pattern="repo$")
async def repify(e):
    try:
        q = await ultroid_bot.inline_query(asst.me.username, "repo")
        await q[0].click(e.chat_id)
        if e.sender_id == ultroid_bot.uid:
            await e.delete()
    except (ChatSendInlineForbiddenError, bmi):
        await eor(e, REPOMSG)
