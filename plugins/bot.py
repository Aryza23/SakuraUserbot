# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📚 Commands Available

• `{i}alive`
   untuk mengetahui apakah bot bekerja atau tidak.

• `{i}ping`
   cek kecepatan respon sakura ubot.

• `{i}cmds`
   lihat semua nama plugins.

• `{i}restart`
   untuk memulai ulang bot anda.

• `{i}logs (sys)`
   dapatkan full logs terminal.

• `{i}logs heroku`
   Get the latest 100 lines of heroku logs.

• `{i}shutdown`
   matikan sakura userbot mu.
"""

import time
from datetime import datetime as dt
from platform import python_version as pyver

from git import Repo
from pySakura.version import __version__ as UltVer
from telethon import __version__, events
from telethon.errors.rpcerrorlist import ChatSendMediaForbiddenError

from . import *


@ultroid_cmd(
    pattern="alive$",
)
async def lol(ult):
    pic = udB.get("ALIVE_PIC")
    uptime = grt(time.time() - start_time)
    header = (
        udB.get("ALIVE_TEXT")
        or "minasan kon'nichiwa, sakura userbot is alive boss 👩🏻‍🎤."
    )

    y = Repo().active_branch
    xx = Repo().remotes[0].config_reader.get("url")
    rep = xx.replace(".git", f"/tree/{y}")
    kk = f" `[{y}]({rep})` "
    als = (get_string("alive_1")).format(
        header,
        OWNER_NAME,
        sakura_version,
        UltVer,
        uptime,
        pyver(),
        __version__,
        kk,
    )
    if pic is None:
        return await eor(ult, als)
    elif "telegra" in pic:
        try:
            await ultroid_bot.send_message(
                ult.chat_id, als, file=pic, link_preview=False
            )
            await ult.delete()
        except ChatSendMediaForbiddenError:
            await eor(ult, als, link_preview=False)
    else:
        try:
            await ultroid_bot.send_message(ult.chat_id, file=pic)
            await ultroid_bot.send_message(ult.chat_id, als, link_preview=False)
            await ult.delete()
        except ChatSendMediaForbiddenError:
            await eor(ult, als, link_preview=False)


@ultroid_bot.on(events.NewMessage(pattern=f"\\{HNDLR}ping$"))
async def _(event):
    if event.fwd_from:
        return
    if not event.out and not is_sudo(event.sender_id):
        return
    start = dt.now()
    x = await eor(event, "`🏓 pong`")
    end = dt.now()
    ms = (end - start).microseconds / 1000
    uptime = grt(time.time() - start_time)
    await x.edit(get_string("ping").format(ms, uptime))


@ultroid_cmd(
    pattern="cmds$",
)
async def cmds(event):
    await allcmds(event)


@ultroid_cmd(
    pattern="restart$",
)
async def restartbt(ult):
    ok = await eor(ult, "`restarting sakura userbot...`")
    if Var.HEROKU_API:
        await restart(ok)
    else:
        await bash("pkill python3 && python3 -m pySakura")


@ultroid_cmd(pattern="shutdown$")
async def shutdownbot(ult):
    if not ult.out and not is_fullsudo(ult.sender_id):
        return await eod(ult, "`perintah ini dibatasi untuk anggota sudo.`")
    await shutdown(ult)


@ultroid_bot.on(events.NewMessage(pattern=f"\\{HNDLR}logs ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    if not event.out and not is_sudo(event.sender_id):
        return
    try:
        opt = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await def_logs(event)
    if opt == "heroku":
        await heroku_logs(event)
    else:
        await def_logs(event)
