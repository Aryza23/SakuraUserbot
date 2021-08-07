# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
📚 Commands Available -

• `{i}dm <username/id> <reply/type>`
    kirim pesan secara langsung ke seseorang.
"""

from . import *


@ultroid_cmd(pattern="dm ?(.*)")
async def dm(e):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eor(e, "`perintah ini dibatasi secara penuh untuk anggota sudo.`")
    if len(e.text) > 3:
        if not e.text[3] == " ":  # weird fix
            return
    d = e.pattern_match.group(1)
    c = d.split(" ")
    try:
        chat_id = await get_user_id(c[0])
    except Exception as ex:
        return await eod(e, "`" + str(ex) + "`", time=5)
    msg = ""
    masg = await e.get_reply_message()
    if e.reply_to_msg_id:
        await ultroid_bot.send_message(chat_id, masg)
        await eod(e, "`⚜️ ᴘᴇsᴀɴ ᴛᴇʀᴋɪʀɪᴍ ⚜️`", time=4)
    for i in c[1:]:
        msg += i + " "
    if msg == "":
        return
    try:
        await ultroid_bot.send_message(chat_id, msg)
        await eod(e, "`⚜️ ᴘᴇsᴀɴ ᴛᴇʀᴋɪʀɪᴍ ⚜️`", time=4)
    except BaseException:
        await eod(
            e,
            "`{i}help dm`",
            time=4,
        )
