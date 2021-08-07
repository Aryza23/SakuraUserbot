# sakura userbot
# copyright 2021 (c) by veez project
# levina-lab

"""
📚 Commands Available -
• `{i}update`
   perintah untuk memeriksa pembaruan userbot dan memperbarui nya ke versi terbaru.
"""

from git import Repo
from telethon.tl.functions.channels import ExportMessageLinkRequest as GetLink

from . import *

ULTPIC = "resources/extras/inline.jpg"
CL = udB.get("INLINE_PIC")
if CL:
    ULTPIC = CL


@ultroid_cmd(pattern="update$")
async def _(e):
    xx = await eor(e, "`memeriksa pembaruan...`")
    m = await updater()
    branch = (Repo.init()).active_branch
    if m:
        x = await asst.send_file(
            int(udB.get("LOG_CHANNEL")),
            ULTPIC,
            caption="✨ **UPDATE TERSEDIA** ✨",
            force_document=False,
            buttons=Button.inline("CHANGE LOGS", data="changes"),
        )
        if not e.client._bot:
            Link = (await e.client(GetLink(x.chat_id, x.id))).link
        else:
            Link = f"https://t.me/c/{x.chat.id}/{x.id}"
        await xx.edit(
            f'<strong><a href="{Link}">[CHANGE-LOGS]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )
    else:
        await xx.edit(
            f'<code>sakura userbot anda </code><strong>sudah versi terbaru</strong><code> dengan </code><strong><a href="https://github.com/levina-lab/SakuraUserbot/tree/{branch}">[{branch}]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )


@callback("updtavail")
@owner
async def updava(event):
    await event.delete()
    await asst.send_file(
        int(udB.get("LOG_CHANNEL")),
        ULTPIC,
        caption="✨ **PEMBARUAN TERSEDIA** ✨",
        force_document=False,
        buttons=Button.inline("CHANGE-LOGS", data="changes"),
    )
