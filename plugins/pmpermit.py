# veez project

"""
📚 Commands Available -

• `{i}a` or `{i}approve`
   untuk menyetujui orang yang ingin melakukan pm.

• `{i}da` or `{i}disapprove`
   untuk menolak orang yang ingin melakukan pm.

• `{i}block`
   untuk memblokir orang yang pm kamu.

• `{i}unblock`
   untuk unblokir orang yang pm kamu.

• `{i}nologpm`
   untuk mengentikan log dari pengguna tersebut.

• `{i}logpm`
   mulai logging kembali dari pengguna tersebut.

• `{i}startarchive`
   saya akan mulai menambahkan pm baru ke arsip.

• `{i}stoparchive`
   saya akan berhenti menambahkan pm baru ke arsip.

• `{i}cleararchive`
   mengeluarkan semua obrolan dari arsip.
"""

import re

from pySakura.functions.logusers_db import *
from pySakura.functions.pmpermit_db import *
from telethon import events
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.utils import get_display_name

from . import *

# ========================= CONSTANTS =============================
COUNT_PM = {}
LASTMSG = {}
if Redis("PMPIC"):
    PMPIC = Redis("PMPIC")
else:
    PMPIC = "resources/extras/teamsakura.jpg"

UND = get_string("pmperm_1")

if not Redis("PM_TEXT"):
    UNAPPROVED_MSG = """
**𝐏𝐌 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 𝐌𝐈𝐋𝐈𝐊 {ON}!**\n
{UND}
\nkamu memiliki {warn}/{twarn} peringatan!"""
else:
    UNAPPROVED_MSG = (
        """
**𝐏𝐌 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 𝐌𝐈𝐋𝐈𝐊 {ON}!**\n"""
        f"""
{Redis("PM_TEXT")}
"""
        """
\nkamu memiliki {warn}/{twarn} peringatan!"""
    )

UNS = get_string("pmperm_2")
# 1
if Redis("PMWARNS"):
    try:
        WARNS = int(Redis("PMWARNS"))
    except BaseException:
        WARNS = 4
else:
    WARNS = 4
NO_REPLY = get_string("pmperm_3")
PMCMDS = [
    f"{hndlr}a",
    f"{hndlr}approve",
    f"{hndlr}da",
    f"{hndlr}disapprove",
    f"{hndlr}block",
    f"{hndlr}unblock",
]

_not_approved = {}
# =================================================================


@ultroid_cmd(
    pattern="logpm$",
)
async def _(e):
    if not e.is_private:
        return await eod(e, "`gunakan saya di private chat.`", time=3)
    if is_logger(str(e.chat_id)):
        nolog_user(str(e.chat_id))
        return await eod(e, "`mulai sekarang saya akan mencatat log pesan disini.`", time=3)
    else:
        return await eod(e, "`mulai sekarang saya tidak akan mencatat log pesan disini.`", time=3)


@ultroid_cmd(
    pattern="nologpm$",
)
async def _(e):
    if not e.is_private:
        return await eod(e, "`gunakan saya di private chat.`", time=3)
    if not is_logger(str(e.chat_id)):
        log_user(str(e.chat_id))
        return await eod(e, "`sekarang saya tidak akan mencatat log pesan disini.`", time=3)
    else:
        return await eod(e, "`tidak akan lagi mencatat log pesan disini.`", time=3)


@ultroid_bot.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: e.is_private,
    ),
)
async def permitpm(event):
    user = await event.get_chat()
    if user.bot or user.is_self or user.verified:
        return
    if is_logger(user.id):
        return
    if Redis("PMLOG") == "True":
        pl = udB.get("PMLOGGROUP")
        if pl is not None:
            return await event.forward_to(int(pl))
        await event.forward_to(int(udB.get("LOG_CHANNEL")))


sett = Redis("PMSETTING")
if sett is None:
    sett = True
if sett == "True":

    @ultroid_bot.on(
        events.NewMessage(
            outgoing=True,
            func=lambda e: e.is_private,
        ),
    )
    async def autoappr(e):
        miss = await e.get_chat()
        if miss.bot or miss.is_self or miss.verified or Redis("AUTOAPPROVE") != "True":
            return
        if str(miss.id) in DEVLIST:
            return
        mssg = e.text
        if mssg.startswith(HNDLR):  # do not approve if outgoing is a command.
            return
        if not is_approved(e.chat_id):
            approve_user(e.chat_id)
            async for message in e.client.iter_messages(e.chat_id, search=UND):
                await message.delete()
            async for message in e.client.iter_messages(e.chat_id, search=UNS):
                await message.delete()
            try:
                await ultroid_bot.edit_folder(e.chat_id, folder=0)
            except BaseException:
                pass
            name = await e.client.get_entity(e.chat_id)
            name0 = str(name.first_name)
            await asst.send_message(
                int(udB.get("LOG_CHANNEL")),
                f"#AutoApproved\n**Pesan Keluar.**\nPengguna - [{name0}](tg://user?id={e.chat_id})",
            )

    @ultroid_bot.on(
        events.NewMessage(
            incoming=True,
            func=lambda e: e.is_private,
        ),
    )
    async def permitpm(event):
        user = await event.get_chat()
        if user.bot or user.is_self or user.verified:
            return
        if str(user.id) in DEVLIST:
            return
        apprv = is_approved(user.id)
        if not apprv and event.text != UND:
            if Redis("MOVE_ARCHIVE") == "True":
                try:
                    await ultroid.edit_folder(user.id, folder=1)
                except BaseException:
                    pass
            if event.media:
                await event.delete()
            name = user.first_name
            if user.last_name:
                fullname = f"{name} {user.last_name}"
            else:
                fullname = name
            username = f"@{user.username}"
            mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
            count = len(get_approved())
            try:
                wrn = COUNT_PM[user.id] + 1
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[user.id],
                    f"pesan masuk dari {mention} dengan {wrn}/{WARNS} peringatan!",
                    buttons=[
                        Button.inline("sᴇᴛᴜᴊᴜɪ ᴘᴍ", data=f"approve_{user.id}"),
                        Button.inline("ᴛᴏʟᴀᴋ ᴘᴍ", data=f"block_{user.id}"),
                    ],
                )
            except KeyError:
                _not_approved[user.id] = await asst.send_message(
                    int(udB.get("LOG_CHANNEL")),
                    f"pesan masuk dari {mention} dengan 1/{WARNS} peringatan!",
                    buttons=[
                        Button.inline("sᴇᴛᴜᴊᴜɪ ᴘᴍ", data=f"approve_{user.id}"),
                        Button.inline("ᴛᴏʟᴀᴋ ᴘᴍ", data=f"block_{user.id}"),
                    ],
                )
                wrn = 1
            if user.id in LASTMSG:
                prevmsg = LASTMSG[user.id]
                if event.text != prevmsg:
                    if "pesan masuk" in event.text:
                        return
                    async for message in ultroid.iter_messages(
                        user.id,
                        search=UND,
                    ):
                        await message.delete()

                    async for message in ultroid.iter_messages(
                        user.id,
                        search=UNS,
                    ):
                        await message.delete()
                    message_ = UNAPPROVED_MSG.format(
                        ON=OWNER_NAME,
                        warn=wrn,
                        twarn=WARNS,
                        UND=UND,
                        name=name,
                        fullname=fullname,
                        username=username,
                        count=count,
                        mention=mention,
                    )
                    await ultroid.send_file(
                        user.id,
                        PMPIC,
                        caption=message_,
                    )
                elif event.text == prevmsg:
                    async for message in ultroid.iter_messages(
                        user.id,
                        search=UND,
                    ):
                        await message.delete()
                    message_ = UNAPPROVED_MSG.format(
                        ON=OWNER_NAME,
                        warn=wrn,
                        twarn=WARNS,
                        UND=UND,
                        name=name,
                        fullname=fullname,
                        username=username,
                        count=count,
                        mention=mention,
                    )
                    await ultroid.send_file(
                        user.id,
                        PMPIC,
                        caption=message_,
                    )
                LASTMSG.update({user.id: event.text})
            else:
                async for message in ultroid.iter_messages(user.id, search=UND):
                    await message.delete()
                message_ = UNAPPROVED_MSG.format(
                    ON=OWNER_NAME,
                    warn=wrn,
                    twarn=WARNS,
                    UND=UND,
                    name=name,
                    fullname=fullname,
                    username=username,
                    count=count,
                    mention=mention,
                )
                await ultroid.send_file(
                    user.id,
                    PMPIC,
                    caption=message_,
                )
                LASTMSG.update({user.id: event.text})
            if user.id not in COUNT_PM:
                COUNT_PM.update({user.id: 1})
            else:
                COUNT_PM[user.id] = COUNT_PM[user.id] + 1
            if COUNT_PM[user.id] >= WARNS:
                async for message in ultroid.iter_messages(user.id, search=UND):
                    await message.delete()
                await event.respond(UNS)
                try:
                    del COUNT_PM[user.id]
                    del LASTMSG[user.id]
                except KeyError:
                    await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        "pmpermit kacau, tolong restart userbot anda!",
                    )
                    return LOGS.info("COUNT_PM is messed.")
                await ultroid(BlockRequest(user.id))
                await ultroid(ReportSpamRequest(peer=user.id))
                name = await ultroid.get_entity(user.id)
                name0 = str(name.first_name)
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[user.id],
                    f"[{name0}](tg://user?id={user.id}) telah diblokir karena melakukan spam ke pm anda.",
                )

    @ultroid_cmd(
        pattern="(start|stop|clear)archive$",
    )
    async def _(e):
        x = e.pattern_match.group(1)
        if x == "start":
            udB.set("MOVE_ARCHIVE", "True")
            await eod(e, "sekarang saya akan memindahkan dm baru yang tidak disetujui ke arsip")
        elif x == "stop":
            udB.set("MOVE_ARCHIVE", "False")
            await eod(e, "sekarang saya tidak akan memindahkan dm baru yang tidak disetujui ke arsip")
        elif x == "clear":
            try:
                await e.client.edit_folder(unpack=1)
                await eod(e, "unarsip semua obrolan.")
            except Exception as mm:
                await eod(e, str(mm))

    @ultroid_cmd(
        pattern="(a|approve)(?: |$)",
    )
    async def approvepm(apprvpm):
        if apprvpm.reply_to_msg_id:
            reply = await apprvpm.get_reply_message()
            replied_user = await apprvpm.client.get_entity(reply.sender_id)
            aname = replied_user.id
            if str(aname) in DEVLIST:
                return await eor(
                    apprvpm,
                    "maaf, dia developer saya.\ndia disetujui secara otomatis untuk pm.",
                )
            name0 = str(replied_user.first_name)
            uid = replied_user.id
            if not is_approved(uid):
                approve_user(uid)
                try:
                    await apprvpm.client.edit_folder(uid, folder=0)
                except BaseException:
                    pass
                await eod(apprvpm, f"[{name0}](tg://user?id={uid}) `disetujui untuk melakukan pm, tolong jangan melakukan spam juga yah!`")
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[uid],
                    f"#APPROVED\n\n`User: `[{name0}](tg://user?id={uid})",
                    buttons=[
                        Button.inline("ᴛᴏʟᴀᴋ ᴘᴍ", data=f"disapprove_{uid}"),
                        Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{uid}"),
                    ],
                )
            else:
                await eod(apprvpm, "`pengguna sudah disetujui untuk melakukan pm.`")
        elif apprvpm.is_private:
            user = await apprvpm.get_chat()
            aname = await apprvpm.client.get_entity(user.id)
            if str(user.id) in DEVLIST:
                return await eor(
                    apprvpm,
                    "maaf, dia developer saya.\ndia disetujui secara otomatis untuk pm.",
                )
            name0 = str(aname.first_name)
            uid = user.id
            if not is_approved(uid):
                approve_user(uid)
                try:
                    await apprvpm.client.edit_folder(uid, folder=0)
                except BaseException:
                    pass
                await eod(apprvpm, f"[{name0}](tg://user?id={uid}) `disetujui untuk melakukan pm, tolong jangan lakukan spam yah!`")
                async for message in apprvpm.client.iter_messages(user.id, search=UND):
                    await message.delete()
                async for message in apprvpm.client.iter_messages(user.id, search=UNS):
                    await message.delete()
                try:
                    await asst.edit_message(
                        int(udB.get("LOG_CHANNEL")),
                        _not_approved[uid],
                        f"#APPROVED\n\n`User: `[{name0}](tg://user?id={uid})",
                        buttons=[
                            Button.inline("ᴛᴏʟᴀᴋ ᴘᴍ", data=f"disapprove_{uid}"),
                            Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{uid}"),
                        ],
                    )
                except KeyError:
                    _not_approved[uid] = await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        f"#APPROVED\n\n`User: `[{name0}](tg://user?id={uid})",
                        buttons=[
                            Button.inline("ᴛᴏʟᴀᴋ ᴘᴍ", data=f"disapprove_{uid}"),
                            Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{uid}"),
                        ],
                    )
            else:
                await eod(apprvpm, "`pengguna sudah disetujui untuk melakukan pm.`")
        else:
            await apprvpm.edit(NO_REPLY)

    @ultroid_cmd(
        pattern="(da|disapprove)(?: |$)",
    )
    async def disapprovepm(e):
        if e.reply_to_msg_id:
            reply = await e.get_reply_message()
            replied_user = await e.client.get_entity(reply.sender_id)
            aname = replied_user.id
            if str(aname) in DEVLIST:
                return await eor(
                    e,
                    "`maaf, dia developer saya.\npesan pm nya tidak dapat ditolak.`",
                )
            name0 = str(replied_user.first_name)
            if is_approved(aname):
                disapprove_user(aname)
                await e.edit(
                    f"[{name0}](tg://user?id={replied_user.id}) `ditolak untuk melakukan pm, jangan spam atau anda akan diblokir!`",
                )
                await asyncio.sleep(5)
                await e.delete()
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[aname],
                    f"#DISAPPROVED\n\n[{name0}](tg://user?id={bbb.id}) `telah ditolak untuk melakukan pm ke kamu.`",
                    buttons=[
                        Button.inline("sᴇᴛᴜᴊᴜɪ ᴘᴍ", data=f"approve_{aname}"),
                        Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{aname}"),
                    ],
                )
            else:
                await e.edit(
                    f"[{name0}](tg://user?id={replied_user.id}) tidak akan pernah disetujui!",
                )
                await asyncio.sleep(5)
                await e.delete()
        elif e.is_private:
            bbb = await e.get_chat()
            aname = await e.client.get_entity(bbb.id)
            if str(bbb.id) in DEVLIST:
                return await eor(
                    e,
                    "`maaf, dia developer saya.\ndia tidak dapat ditolak.`",
                )
            name0 = str(aname.first_name)
            if is_approved(bbb.id):
                disapprove_user(bbb.id)
                await e.edit(f"[{name0}](tg://user?id={bbb.id}) `ditolak untuk melakukan pm!`")
                await asyncio.sleep(5)
                await e.delete()
                try:
                    await asst.edit_message(
                        int(udB.get("LOG_CHANNEL")),
                        _not_approved[bbb.id],
                        f"#DISAPPROVED\n\n[{name0}](tg://user?id={bbb.id}) `telah ditolak untuk melakukan pm ke kamu.`",
                        buttons=[
                            Button.inline("sᴇᴛᴜᴊᴜɪ ᴘᴍ", data=f"approve_{bbb.id}"),
                            Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{bbb.id}"),
                        ],
                    )
                except KeyError:
                    _not_approved[bbb.id] = await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        f"#DISAPPROVED\n\n[{name0}](tg://user?id={bbb.id}) `telah ditolak untuk melakukan pm ke kamu.`",
                        buttons=[
                            Button.inline("sᴇᴛᴜᴊᴜɪ ᴘᴍ", data=f"approve_{bbb.id}"),
                            Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{bbb.id}"),
                        ],
                    )
            else:
                await e.edit(f"[{name0}](tg://user?id={bbb.id}) tidak akan pernah disetujui!")
                await asyncio.sleep(5)
                await e.delete()
        else:
            await e.edit(NO_REPLY)


@ultroid_cmd(
    pattern="block ?(.*)",
)
async def blockpm(block):
    match = block.pattern_match.group(1)
    if block.is_reply:
        reply = await block.get_reply_message()
        user = reply.sender_id
    elif match:
        user = await get_user_id(match)
    elif block.is_private:
        user = block.chat_id
    else:
        return await eod(block, NO_REPLY)
    if str(user) in DEVLIST:
        return await eor(
            block,
            "`maaf, dia developer saya.\ndia tidak dapat diblokir!`",
        )
    await block.client(BlockRequest(user))
    aname = await block.client.get_entity(user)
    await eor(block, f"`{aname.first_name} telah diblokir!`")
    try:
        disapprove_user(user)
    except AttributeError:
        pass
    try:
        await asst.edit_message(
            int(udB.get("LOG_CHANNEL")),
            _not_approved[user],
            f"#BLOCKED\n\n[{aname.first_name}](tg://user?id={user}) telah di **blokir**.",
            buttons=Button.inline("UNBLOKIR", data=f"unblock_{user}"),
        )
    except KeyError:
        _not_approved[user] = await asst.send_message(
            int(udB.get("LOG_CHANNEL")),
            f"#BLOCKED\n\n[{aname.first_name}](tg://user?id={user}) telah di **blokir**.",
            buttons=Button.inline("UNBLOKIR", data=f"unblock_{user}"),
        )


@ultroid_cmd(
    pattern="unblock ?(.*)",
)
async def unblockpm(unblock):
    match = unblock.pattern_match.group(1)
    if unblock.is_reply:
        reply = await unblock.get_reply_message()
        user = reply.sender_id
    elif match:
        user = await get_user_id(match)
    else:
        return await eod(unblock, NO_REPLY)
    try:
        await unblock.client(UnblockRequest(user))
        aname = await unblock.client.get_entity(user)
        await eor(unblock, f"`{aname.first_name} telah di unblokir!`")
    except Exception as et:
        await eod(unblock, f"ERROR - {str(et)}")
    try:
        await asst.edit_message(
            int(udB.get("LOG_CHANNEL")),
            _not_approved[user],
            f"#UNBLOCKED\n\n[{aname.first_name}](tg://user?id={user}) telah di **unblokir**.",
            buttons=[
                Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{user}"),
                Button.inline("ᴛᴜᴛᴜᴘ", data="deletedissht"),
            ],
        )
    except KeyError:
        _not_approved[user] = await asst.send_message(
            int(udB.get("LOG_CHANNEL")),
            f"#UNBLOCKED\n\n[{aname.first_name}](tg://user?id={user}) telah di **unblokir**.",
            buttons=[
                Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{user}"),
                Button.inline("ᴛᴜᴛᴜᴘ", data="deletedissht"),
            ],
        )


@callback(
    re.compile(
        b"approve_(.*)",
    ),
)
@owner
async def apr_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if str(uid) in DEVLIST:
        await event.edit("dia adalah developer, disetujui!")
    if not is_approved(uid):
        approve_user(uid)
        try:
            await ultroid_bot.edit_folder(uid, folder=0)
        except BaseException:
            pass
        try:
            user_name = (await ultroid.get_entity(uid)).first_name
        except BaseException:
            user_name = ""
        await event.edit(
            f"#APPROVED\n\n[{user_name}](tg://user?id={uid}) `disetujui untuk pm!`",
            buttons=[
                Button.inline("TOLAK PM", data=f"disapprove_{uid}"),
                Button.inline("BLOKIR", data=f"block_{uid}"),
            ],
        )
        async for message in ultroid.iter_messages(uid, search=UND):
            await message.delete()
        async for message in ultroid.iter_messages(uid, search=UNS):
            await message.delete()
        await event.answer("disetujui.")
        x = await ultroid.send_message(uid, "anda telah disetujui untuk melakukan pm ke saya!")
        await asyncio.sleep(5)
        await x.delete()
    else:
        await event.edit(
            "`pengguna telah disetujui.`",
            buttons=[
                Button.inline("TOLAK PM", data=f"disapprove_{uid}"),
                Button.inline("BLOKIR", data=f"block_{uid}"),
            ],
        )


@callback(
    re.compile(
        b"disapprove_(.*)",
    ),
)
@owner
async def disapr_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if is_approved(uid):
        disapprove_user(uid)
        try:
            user_name = (await ultroid.get_entity(uid)).first_name
        except BaseException:
            user_name = ""
        await event.edit(
            f"#DISAPPROVED\n\n[{user_name}](tg://user?id={uid}) `ditolak untuk melakukan pm!`",
            buttons=[
                Button.inline("sᴇᴛᴜᴊᴜɪ ᴘᴍ", data=f"approve_{uid}"),
                Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{uid}"),
            ],
        )
        await event.answer("ditolak !!.")
        x = await ultroid.send_message(uid, "anda telah ditolak untuk melakukan pm ke saya!")
        await asyncio.sleep(5)
        await x.delete()
    else:
        await event.edit(
            "`pengguna tidak akan pernah disetujui!`",
            buttons=[
                Button.inline("ᴛᴏʟᴀᴋ ᴘᴍ", data=f"disapprove_{uid}"),
                Button.inline("ʙʟᴏᴋɪʀ", data=f"block_{uid}"),
            ],
        )


@callback(
    re.compile(
        b"block_(.*)",
    ),
)
@owner
async def blck_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    await ultroid(BlockRequest(uid))
    try:
        user_name = (await ultroid.get_entity(uid)).first_name
    except BaseException:
        user_name = ""
    await event.answer("Blocked.")
    await event.edit(
        f"#BLOCKED\n\n[{user_name}](tg://user?id={uid}) pengguna telah **diblokir!**",
        buttons=Button.inline("UNBLOKIR", data=f"unblock_{uid}"),
    )


@callback(
    re.compile(
        b"unblock_(.*)",
    ),
)
@owner
async def unblck_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    await ultroid(UnblockRequest(uid))
    try:
        user_name = (await ultroid.get_entity(uid)).first_name
    except BaseException:
        user_name = ""
    await event.answer("di unblokir.")
    await event.edit(
        f"#UNBLOCKED\n\n[{user_name}](tg://user?id={uid}) telah di **unblokir!**",
        buttons=[
            Button.inline("BLOKIR", data=f"block_{uid}"),
            Button.inline("TUTUP", data="deletedissht"),
        ],
    )


@callback("deletedissht")
async def ytfuxist(e):
    await e.answer("dihapus.")
    await e.delete()
