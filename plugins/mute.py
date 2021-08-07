# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📚 Commands Available -

• `{i}mute <balas ke [pesan/id pengguna>`
    bisukan pengguna disebuah obrolan.

• `{i}unmute <balas ke pesan/id pengguna>`
    unmute pengguna disebuah obrolan.

• `{i}dmute <balas ke pesan/id pengguna>`
    hapus pesan dan bisukan pengguna disebuah obrolan.

• `{i}undmute <balas ke pesan/id pengguna>`
    unmute pengguna yang di dmuted di sebuah obrolan.

• `{i}tmute <time> <balas ke pesan/gunakan id>`
    s- detik
    m- menit
    h- jam
    d- hari
    bisukan pengguna disebuah obrolan dengan waktu tertentu.
"""


from pySakura.functions.all import ban_time
from pySakura.functions.mute_db import is_muted, mute, unmute
from telethon import events

from . import *


@ultroid_bot.on(events.NewMessage(incoming=True))
async def watcher(event):
    if is_muted(f"{event.sender_id}_{event.chat_id}"):
        await event.delete()
    if event.via_bot and is_muted(f"{event.via_bot_id}_{event.chat_id}"):
        await event.delete()


@ultroid_cmd(
    pattern="dmute ?(.*)",
)
async def startmute(event):
    xx = await eor(event, "`membisukan...`")
    input = event.pattern_match.group(1)
    private = False
    if event.is_private:
        private = True
    if input:
        if input.isdigit():
            try:
                userid = input
            except ValueError as x:
                return await xx.edit(str(x))
        else:
            userid = (await event.client.get_entity(input)).id
    elif event.reply_to_msg_id:
        userid = (await event.get_reply_message()).sender_id
    elif private is True:
        userid = event.chat_id
    else:
        return await eod(xx, "`balas ke pengguna atau berikan id nya.`", time=5)
    chat_id = event.chat_id
    chat = await event.get_chat()
    if "admin_rights" in vars(chat) and vars(chat)["admin_rights"] is not None:
        if chat.admin_rights.delete_messages is True:
            pass
        else:
            return await eor(xx, "`tidak memiliki izin admin...`", time=5)
    elif "creator" in vars(chat):
        pass
    elif private:
        pass
    else:
        return await eod(xx, "`tidak memiliki izin admin...`", time=5)
    if is_muted(f"{userid}_{chat_id}"):
        return await eod(xx, "`pengguna ini sudah dibisukan di obrolan ini.`", time=5)
    try:
        mute(f"{userid}_{chat_id}")
        await eod(xx, "`berhasil dibisukan.`", time=3)
    except Exception as e:
        await eod(xx, "Error: " + f"`{str(e)}`")


@ultroid_cmd(
    pattern="undmute ?(.*)",
)
async def endmute(event):
    xx = await eor(event, "`membuka mute...`")
    private = False
    input = event.pattern_match.group(1)
    if event.is_private:
        private = True
    if input:
        if input.isdigit():
            try:
                userid = input
            except ValueError as x:
                return await xx.edit(str(x))
        else:
            userid = (await event.client.get_entity(input)).id
    elif event.reply_to_msg_id:
        userid = (await event.get_reply_message()).sender_id
    elif private is True:
        userid = event.chat_id
    else:
        return await eod(xx, "`balas ke pengguna atau berikan id nya.`", time=5)
    chat_id = event.chat_id
    if not is_muted(f"{userid}_{chat_id}"):
        return await eod(xx, "`pengguna ini sudah tidak dibisukan di obrolan ini.`", time=3)
    try:
        unmute(f"{userid}_{chat_id}")
        await eod(xx, "`berhasil di unmute...`", time=3)
    except Exception as e:
        await eod(xx, "Error: " + f"`{str(e)}`")


@ultroid_cmd(
    pattern="tmute",
    groups_only=True,
)
async def _(e):
    xx = await eor(e, "`membisukan...`")
    huh = e.text.split(" ")
    try:
        tme = huh[1]
    except BaseException:
        return await eod(xx, "`tentukan sampai kapan akan dimute ?`", time=5)
    try:
        input = huh[2]
    except BaseException:
        pass
    chat = await e.get_chat()
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(userid)).first_name
    elif input:
        if input.isdigit():
            try:
                userid = input
                name = (await e.client.get_entity(userid)).first_name
            except ValueError as x:
                return await xx.edit(str(x))
        else:
            userid = (await e.client.get_entity(input)).id
            name = (await event.client.get_entity(userid)).first_name
    else:
        return await eod(xx, "`balas ke seseorang atau gunakan id nya...`", time=3)
    if userid == ultroid_bot.uid:
        return await eod(xx, "`tidak dapat membisukan diri sendiri.`", time=3)
    try:
        bun = await ban_time(xx, tme)
        await e.client.edit_permissions(
            chat.id,
            userid,
            until_date=bun,
            send_messages=False,
        )
        await eod(
            xx,
            f"`berhasil membisukan` [{name}](tg://user?id={userid}) `di {chat.title} untuk {tme}`",
            time=5,
        )
    except BaseException as m:
        await eod(xx, f"`{str(m)}`")


@ultroid_cmd(
    pattern="unmute ?(.*)",
    groups_only=True,
)
async def _(e):
    xx = await eor(e, "`membuka mute...`")
    input = e.pattern_match.group(1)
    chat = await e.get_chat()
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(userid)).first_name
    elif input:
        if input.isdigit():
            try:
                userid = input
                name = (await e.client.get_entity(userid)).first_name
            except ValueError as x:
                return await xx.edit(str(x))
        else:
            userid = (await e.client.get_entity(input)).id
            name = (await e.client.get_entity(userid)).first_name
    else:
        return await eod(xx, "`balas ke seseorang atau gunakan id nya...`", time=3)
    try:
        await e.client.edit_permissions(
            chat.id,
            userid,
            until_date=None,
            send_messages=True,
        )
        await eod(
            xx,
            f"`berhasil di unmute` [{name}](tg://user?id={userid}) `di {chat.title}`",
            time=5,
        )
    except BaseException as m:
        await eod(xx, f"`{str(m)}`")


@ultroid_cmd(
    pattern="mute ?(.*)",
    groups_only=True,
)
async def _(e):
    xx = await eor(e, "`membisukan...`")
    input = e.pattern_match.group(1)
    chat = await e.get_chat()
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(userid)).first_name
    elif input:
        if input.isdigit():
            try:
                userid = input
                name = (await e.client.get_entity(userid)).first_name
            except ValueError as x:
                return await xx.edit(str(x))
        else:
            userid = (await e.client.get_entity(input)).id
            name = (await e.client.get_entity(userid)).first_name
    else:
        return await eod(xx, "`balas ke seseorang atau gunakan id nya...`", time=3)
    if userid == ultroid_bot.uid:
        return await eod(xx, "`tidak dapat membisukan diri sendiri.`", time=3)
    try:
        await e.client.edit_permissions(
            chat.id,
            userid,
            until_date=None,
            send_messages=False,
        )
        await eod(
            xx,
            f"`berhasil membisukan` [{name}](tg://user?id={userid}) `di {chat.title}`",
            time=5,
        )
    except BaseException as m:
        await eod(xx, f"`{str(m)}`")
