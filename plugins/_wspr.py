# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from telethon import Button
from telethon.errors.rpcerrorlist import BotInlineDisabledError as dis
from telethon.errors.rpcerrorlist import BotResponseTimeoutError as rep
from telethon.errors.rpcerrorlist import MessageNotModifiedError as np
from telethon.tl.functions.users import GetFullUserRequest as gu
from telethon.tl.types import UserStatusEmpty as mt
from telethon.tl.types import UserStatusLastMonth as lm
from telethon.tl.types import UserStatusLastWeek as lw
from telethon.tl.types import UserStatusOffline as off
from telethon.tl.types import UserStatusOnline as on
from telethon.tl.types import UserStatusRecently as rec

from . import *

snap = {}
buddhhu = {}


@ultroid_cmd(
    pattern="wspr ?(.*)",
)
async def _(e):
    if e.reply_to_msg_id:
        okk = (await e.get_reply_message()).sender_id
        try:
            put = okk
        except ValueError as ex:
            return await eor(e, str(ex))
        except AttributeError:
            return await eor(e, "`tidak ada username dari pengguna yang diminta.`")
    else:
        put = e.pattern_match.group(1)
    if put:
        try:
            results = await ultroid_bot.inline_query(asst.me.username, f"msg {put}")
        except rep:
            return await eor(
                e,
                get_string("help_2").format(HNDLR),
            )
        except dis:
            return await eor(e, get_string("help_3"))
        await results[0].click(e.chat_id, reply_to=e.reply_to_msg_id, hide_via=True)
        await e.delete()
    else:
        await eor(e, "`berikan juga id atau username nya`")


@in_pattern("msg")
@in_owner
async def _(e):
    vvv = e.text
    zzz = vvv.split(" ", maxsplit=1)
    try:
        ggg = zzz[1]
        sed = ggg.split(" wspr ", maxsplit=1)
        query = sed[0].replace(" ", "")
        if query.isdigit():
            query = int(query)
    except IndexError:
        return
    iuser = e.query.user_id
    try:
        desc = sed[1]
    except IndexError:
        desc = "tekan saya"
    if "wspr" not in vvv:
        try:
            logi = await ultroid_bot(gu(id=query))
            name = logi.user.first_name
            ids = logi.user.id
            username = logi.user.username
            mention = f"[{name}](tg://user?id={ids})"
            x = logi.user.status
            bio = logi.about
            if isinstance(x, on):
                status = "online"
            if isinstance(x, off):
                status = "offline"
            if isinstance(x, rec):
                status = "baru saja terlihat belakangan ini"
            if isinstance(x, lm):
                status = "terakhir terlihat beberapa bulan yang lalu"
            if isinstance(x, lw):
                status = "terakhir terlihat beberapa minggu yang lalu"
            if isinstance(x, mt):
                status = "tidak diketahui"
            text = f"**nama:**    `{name}`\n"
            text += f"**id:**    `{ids}`\n"
            if username:
                text += f"**username:**    `{username}`\n"
                url = f"https://t.me/{username}"
            else:
                text += f"**mention:**    `{mention}`\n"
                url = f"tg://user?id={ids}"
            text += f"**status:**    `{status}`\n"
            text += f"**tentang:**    `{bio}`"
            button = [
                Button.url("private", url=url),
                Button.switch_inline(
                    "secret msg",
                    query=f"msg {query} wspr haii 👋",
                    same_peer=True,
                ),
            ]
            sur = e.builder.article(
                title=f"{name}",
                description=desc,
                text=text,
                buttons=button,
            )
        except BaseException:
            name = f"pengguna {query} tidak ditemukan\ncari lagi."
            sur = e.builder.article(
                title=name,
                text=name,
            )
    else:
        try:
            logi = await ultroid_bot.get_entity(query)
            button = [
                Button.inline("PESAN RAHASIA", data=f"dd_{e.id}"),
                Button.inline("HAPUS PESAN", data=f"del_{e.id}"),
            ]
            us = logi.username
            sur = e.builder.article(
                title=f"{logi.first_name}",
                description=desc,
                text=get_string("wspr_1").format(us),
                buttons=button,
            )
            buddhhu.update({e.id: [logi.id, iuser]})
            snap.update({e.id: desc})
        except ValueError:
            sur = e.builder.article(
                title="ketikkan pesan mu",
                text=f"anda tidak mengetik pesan apapun.",
            )
    await e.answer([sur])


@callback(
    re.compile(
        "dd_(.*)",
    ),
)
async def _(e):
    ids = int(e.pattern_match.group(1).decode("UTF-8"))
    if buddhhu.get(ids):
        if e.sender_id in buddhhu[ids]:
            await e.answer(snap[ids], alert=True)
        else:
            await e.answer("🌸 pesan ini bukan untukmu 🌸", alert=True)
    else:
        await e.answer("pesan telah dihapus", alert=True)


@callback(re.compile("del_(.*)"))
async def _(e):
    ids = int(e.pattern_match.group(1).decode("UTF-8"))
    if buddhhu.get(ids):
        if e.sender_id in buddhhu[ids]:
            buddhhu.pop(ids)
            snap.pop(ids)
            try:
                await e.edit(get_string("wspr_2"))
            except np:
                pass
    else:
        await e.answer("anda tidak dapat melakukan ini !!", alert=True)
