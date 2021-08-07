# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst_cmd("ban")
@owner
async def banhammer(event):
    if not event.is_private:
        return
    x = await event.get_reply_message()
    if x is None:
        return await event.edit("balas ke pesan untuk melakukan banned.")
    target = get_who(x.id)
    if not is_blacklisted(target):
        blacklist_user(target)
        await asst.send_message(event.chat_id, f"#BAN\npengguna - {target}")
        await asst.send_message(
            target,
            "`woi asu! lu udah dibanned yah.`\n**jadi, pesan yang lu kirim ke sini gak bakal terkirim lagi.**",
        )
    else:
        return await asst.send_message(event.chat_id, f"manusia tolol telah dibanned!")


@asst_cmd("unban")
@owner
async def banhammer(event):
    if not event.is_private:
        return
    x = await event.get_reply_message()
    if x is None:
        return await event.edit("balas ke pesan untuk melakukan unbanned.")
    target = get_who(x.id)
    if is_blacklisted(target):
        rem_blacklist(target)
        await asst.send_message(event.chat_id, f"#UNBAN\npengguna - {target}")
        await asst.send_message(target, "`selamat ya! lu udah di unbanned sama tuan gua.`")
    else:
        return await asst.send_message(event.chat_id, f"pengguna sudah di unbanned!")
