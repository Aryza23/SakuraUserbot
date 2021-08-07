# Sakura - UserBot

"""
📚 Commands Available - Plugin Voice Chat.

• `{i}startvc`
   mulai/nyalakan voice chat group.

• `{i}stopvc`
   stop/matikan voice chat group.

• `{i}playvc`
   mulai bot music voice chat untuk menerima perintah.

• `{i}vcinvite`
   undang semua member kedalam voice chat group.
   (anda harus join terlebih dahulu)

• `{i}vcaccess <id/username/balas ke pesan>`
   berikan seseorang akses untuk menggunakan bot music vcg.

• `{i}rmvcaccess <id/username/reply to msg>`
   hapus akses seseorang dari bot music vcg.

• **Voice Chat - Bot Commands**
   `/play ytsearch : nama lagu`
   `/play link youtube`
   `/current`
   `/skip`
   `/exitVc`
"""

from os import remove

from pySakura.functions.vc_sudos import add_vcsudo, del_vcsudo, get_vcsudos, is_vcsudo
from telethon.tl.functions.channels import GetFullChannelRequest as getchat
from telethon.tl.functions.phone import CreateGroupCallRequest as startvc
from telethon.tl.functions.phone import DiscardGroupCallRequest as stopvc
from telethon.tl.functions.phone import GetGroupCallRequest as getvc
from telethon.tl.functions.phone import InviteToGroupCallRequest as invitetovc

from . import *


async def get_call(event):
    mm = await event.client(getchat(event.chat_id))
    xx = await event.client(getvc(mm.full_chat.call))
    return xx.call


def user_list(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


@ultroid_cmd(
    pattern="stopvc$",
    admins_only=True,
    groups_only=True,
)
async def _(e):
    try:
        await e.client(stopvc(await get_call(e)))
        await eor(e, "`voice chat dimatikan...`")
    except Exception as ex:
        await eor(e, f"`{str(ex)}`")


@ultroid_cmd(
    pattern="playvc$",
)
async def _(e):
    zz = await eor(e, "`vcg music bot dimulai...`")
    er, out = await bash("python vcstarter.py & sleep 10 && npm start")
    LOGS.info(er)
    LOGS.info(out)
    if er:
        msg = f"Failed {er}\n\n{out}"
        if len(msg) > 4096:
            with open("vc-error.txt", "w") as f:
                f.write(msg.replace("`", ""))
            await e.reply(file="vc-error.txt")
            await zz.delete()
            remove("vc-error.txt")
            return
        await zz.edit(msg)


@ultroid_cmd(
    pattern="vcinvite$",
    groups_only=True,
)
async def _(e):
    ok = await eor(e, "`mengundang member ke voice chat grup...`")
    users = []
    z = 0
    async for x in e.client.iter_participants(e.chat_id):
        if not x.bot:
            users.append(x.id)
    hmm = list(user_list(users, 6))
    for p in hmm:
        try:
            await e.client(invitetovc(call=await get_call(e), users=p))
            z += 6
        except BaseException:
            pass
    await ok.edit(f"`mengundang {z} pengguna`")


@ultroid_cmd(
    pattern="startvc$",
    admins_only=True,
    groups_only=True,
)
async def _(e):
    try:
        await e.client(startvc(e.chat_id))
        await eor(e, "`voice chat grup dimulai...`")
    except Exception as ex:
        await eor(e, f"`{str(ex)}`")


@ultroid_cmd(
    pattern="listvcaccess$",
)
async def _(e):
    xx = await eor(e, "`mendapatkan daftar pengguna bot voice chat grup...`")
    mm = get_vcsudos()
    pp = f"**{len(mm)} pengguna yang dapat menggunakan bot vcg.**\n"
    if len(mm) > 0:
        for m in mm:
            try:
                name = (await e.client.get_entity(int(m))).first_name
                pp += f"• [{name}](tg://user?id={int(m)})\n"
            except ValueError:
                pp += f"• `{int(m)} » tidak ada info`\n"
    await xx.edit(pp)


@ultroid_cmd(
    pattern="rmvcaccess ?(.*)",
)
async def _(e):
    xx = await eor(e, "`menghapus akses ke fitur voice chat bot...`")
    input = e.pattern_match.group(1)
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(userid)).first_name
    elif input:
        try:
            userid = await get_user_id(input)
            name = (await e.client.get_entity(userid)).first_name
        except ValueError as ex:
            return await eod(xx, f"`{str(ex)}`", time=5)
    else:
        return await eod(xx, "`balas ke pesan pengguna atau berikan id/username nya...`", time=3)
    if not is_vcsudo(userid):
        return await eod(
            xx,
            f"[{name}](tg://user?id={userid})` tidak diizinkan untuk mengakses bot music vcg saya.`",
            time=5,
        )
    try:
        del_vcsudo(userid)
        await eod(
            xx,
            f"[{name}](tg://user?id={userid})` telah dihapus dari daftar orang yang diizinkan menggunakan bot music vcg.`",
            time=5,
        )
    except Exception as ex:
        return await eod(xx, f"`{str(ex)}`", time=5)


@ultroid_cmd(
    pattern="vcaccess ?(.*)",
)
async def _(e):
    xx = await eor(e, "`memberikan akses ke bot music vcg...`")
    input = e.pattern_match.group(1)
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(userid)).first_name
    elif input:
        try:
            userid = await get_user_id(input)
            name = (await e.client.get_entity(userid)).first_name
        except ValueError as ex:
            return await eod(xx, f"`{str(ex)}`", time=5)
    else:
        return await eod(xx, "`balas ke pesan si pengguna atau berikan id/username nya...`", time=3)
    if is_vcsudo(userid):
        return await eod(
            xx,
            f"[{name}](tg://user?id={userid})` telah disetujui untuk mengakses bot music vcg saya.`",
            time=5,
        )
    try:
        add_vcsudo(userid)
        await eod(
            xx,
            f"[{name}](tg://user?id={userid})` ditambahkan ke daftar pengguna yang diizinkan mengakses bot music vcg.`",
            time=5,
        )
    except Exception as ex:
        return await eod(xx, f"`{str(ex)}`", time=5)
