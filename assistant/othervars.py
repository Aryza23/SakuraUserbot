# Sakura - UserBot

import re
from glob import glob
from os import remove
from random import choices

import requests
from telegraph import Telegraph
from telegraph import upload_file as upl

from . import *

# --------------------------------------------------------------------#
telegraph = Telegraph()
r = telegraph.create_account(short_name="Sakura")
auth_url = r["auth_url"]
# --------------------------------------------------------------------#


TOKEN_FILE = "resources/auths/auth_token.txt"


@callback(
    re.compile("sndplug_(.*)"),
)
async def send(eve):
    name = (eve.data_match.group(1)).decode("UTF-8")
    thumb = ""
    for m in choices(sorted(glob("resources/extras/*.jpg"))):
        thumb += m
    if name.startswith("def"):
        plug_name = name.replace(f"def_plugin_", "")
        plugin = f"plugins/{plug_name}.py"
        buttons = [
            [
                Button.inline(
                    "« ᴘᴀsᴛᴇ »",
                    data=f"pasta-{plugin}",
                )
            ],
            [
                Button.inline("« ʙᴀᴄᴋ", data="back"),
                Button.inline("🗑 ᴄʟᴏsᴇ", data="close"),
            ],
        ]
    else:
        plug_name = name.replace(f"add_plugin_", "")
        plugin = f"addons/{plug_name}.py"
        buttons = [
            [
                Button.inline(
                    "« ᴘᴀsᴛᴇ »",
                    data=f"pasta-{plugin}",
                )
            ],
            [
                Button.inline("« ʙᴀᴄᴋ", data="buck"),
                Button.inline("🗑 ᴄʟᴏsᴇ", data="close"),
            ],
        ]
    await eve.edit(file=plugin, thumb=thumb, buttons=buttons)


@callback("updatenow")
@owner
async def update(eve):
    repo = Repo()
    ac_br = repo.active_branch
    ups_rem = repo.remote("upstream")
    if Var.HEROKU_API:
        import heroku3

        try:
            heroku = heroku3.from_key(Var.HEROKU_API)
            heroku_app = None
            heroku_applications = heroku.apps()
        except BaseException:
            return await eve.edit("`ada kesalahan di HEROKU_API.`")
        for app in heroku_applications:
            if app.name == Var.HEROKU_APP_NAME:
                heroku_app = app
        if not heroku_app:
            await eve.edit("`ada kesalahan di HEROKU_APP_NAME.`")
            repo.__del__()
            return
        await eve.edit(
            "`proses pembaruan sakura userbot segera dimulai, mohon tunggu beberapa saat.`"
        )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + Var.HEROKU_API + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eve.edit(f"`here is the error log:\n{error}`")
            repo.__del__()
            return
        await eve.edit("`sakura userbot telah diperbarui!\nmemulai ulang, mohon tunggu...`")
    else:
        await eve.edit(
            "`proses pembaruan sakura userbot segera dimulai, mohon tunggu beberapa saat.`"
        )
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await updateme_requirements()
        await eve.edit(
            "`sakura userbot telah diperbarui!\nmemulai ulang, mohon tunggu...`"
        )
        execl(sys.executable, sys.executable, "-m", "pySakura")


@callback("changes")
@owner
async def changes(okk):
    repo = Repo.init()
    ac_br = repo.active_branch
    changelog, tl_chnglog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    changelog_str = changelog + f"\n\ntekan tombol dibawah untuk memperbarui!"
    if len(changelog_str) > 1024:
        await okk.edit(get_string("upd_4"))
        file = open(f"sakura_updates.txt", "w+")
        file.write(tl_chnglog)
        file.close()
        await okk.edit(
            get_string("upd_5"),
            file="sakura_updates.txt",
            buttons=Button.inline("✨ UPDATE NOW ✨", data="updatenow"),
        )
        remove(f"sakura_updates.txt")
        return
    else:
        await okk.edit(
            changelog_str,
            buttons=Button.inline("✨ UPDATE NOW ✨", data="updatenow"),
            parse_mode="html",
        )


@callback(
    re.compile(
        "pasta-(.*)",
    ),
)
@owner
async def _(e):
    ok = (e.data_match.group(1)).decode("UTF-8")
    hmm = open(ok)
    hmmm = hmm.read()
    hmm.close()
    key = (
        requests.post("https://nekobin.com/api/documents", json={"content": hmmm})
        .json()
        .get("result")
        .get("key")
    )
    if ok.startswith("plugins"):
        buttons = [
            Button.inline("« ʙᴀᴄᴋ", data="back"),
            Button.inline("🗑 ᴄʟᴏsᴇ", data="close"),
        ]
    else:
        buttons = [
            Button.inline("« ʙᴀᴄᴋ", data="buck"),
            Button.inline("🗑 ᴄʟᴏsᴇ", data="close"),
        ]
    await e.edit(
        f"pasted to nekobin!\n     👉[Link](https://nekobin.com/{key})\n     👉[Raw Link](https://nekobin.com/raw/{key})",
        buttons=buttons,
        link_preview=False,
    )


@callback("authorise")
@owner
async def _(e):
    if not e.is_private:
        return
    if not udB.get("GDRIVE_CLIENT_ID"):
        return await e.edit(
            "Client ID and Secret is Empty.\nFill it First.",
            buttons=Button.inline("🗑 ʙᴀᴄᴋ", data="gdrive"),
        )
    storage = await create_token_file(TOKEN_FILE, e)
    authorize(TOKEN_FILE, storage)
    f = open(TOKEN_FILE)
    token_file_data = f.read()
    udB.set("GDRIVE_TOKEN", token_file_data)
    await e.reply(
        "`Success!\nYou are all set to use Google Drive with Sakura Userbot.`",
        buttons=Button.inline("ᴍᴇɴᴜ ᴜᴛᴀᴍᴀ", data="setter"),
    )


@callback("folderid")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Send your FOLDER ID\n\n"
        + "For FOLDER ID:\n"
        + "1. Open Google Drive App.\n"
        + "2. Create Folder.\n"
        + "3. Make that folder public.\n"
        + "4. Copy link of that folder.\n"
        + "5. Send all characters which is after id= .",
    )
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_FOLDER_ID", repl.text)
        await repl.reply(
            "Success Now You Can Authorise.",
            buttons=get_back_button("gdrive"),
        )


@callback("clientsec")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit("Send your CLIENT SECRET")
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        udB.set("GDRIVE_CLIENT_SECRET", repl.text)
        await repl.reply(
            "Success!\nNow You Can Authorise or add FOLDER ID.",
            buttons=get_back_button("gdrive"),
        )


@callback("clientid")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit("Send your CLIENT ID ending with .com")
    async with ultroid_bot.asst.conversation(e.sender_id) as conv:
        reply = conv.wait_event(events.NewMessage(from_users=e.sender_id))
        repl = await reply
        if not repl.text.endswith(".com"):
            return await repl.reply("`Wrong CLIENT ID`")
        udB.set("GDRIVE_CLIENT_ID", repl.text)
        await repl.reply(
            "Success now set CLIENT SECRET",
            buttons=get_back_button("gdrive"),
        )


@callback("gdrive")
@owner
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Go [here](https://console.developers.google.com/flows/enableapi?apiid=drive) and get your CLIENT ID and CLIENT SECRET",
        buttons=[
            [
                Button.inline("Cʟɪᴇɴᴛ Iᴅ", data="clientid"),
                Button.inline("Cʟɪᴇɴᴛ Sᴇᴄʀᴇᴛ", data="clientsec"),
            ],
            [
                Button.inline("Fᴏʟᴅᴇʀ Iᴅ", data="folderid"),
                Button.inline("Aᴜᴛʜᴏʀɪsᴇ", data="authorise"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="otvars")],
        ],
        link_preview=False,
    )


@callback("otvars")
@owner
async def otvaar(event):
    await event.edit(
        "variabel lain untuk ditetapkan untuk @levinachannel:",
        buttons=[
            [
                Button.inline("ᴛᴀɢ ʟᴏɢɢᴇʀ", data="taglog"),
                Button.inline("sᴜᴘᴇʀ ғʙᴀɴ", data="sfban"),
            ],
            [
                Button.inline("sᴜᴅᴏ ᴍᴏᴅᴇ", data="sudo"),
                Button.inline("ʜᴀɴᴅʟᴇʀ", data="hhndlr"),
            ],
            [
                Button.inline("ᴇxᴛʀᴀ ᴘʟᴜɢɪɴs", data="plg"),
                Button.inline("ᴀᴅᴅᴏɴs", data="eaddon"),
            ],
            [
                Button.inline("ᴇᴍᴏᴊɪ ʜᴇʟᴘ", data="emoj"),
                Button.inline("sᴇᴛ ɢᴅʀɪᴠᴇ", data="gdrive"),
            ],
            [Button.inline("ɪɴʟɪɴᴇ ᴘɪᴄ", data="inli_pic")],
            [Button.inline("« ʙᴀᴄᴋ", data="setter")],
        ],
    )


@callback("emoj")
@owner
async def emoji(event):
    await event.delete()
    pru = event.sender_id
    var = "EMOJI_IN_HELP"
    name = f"emoji in `{HNDLR}help` menu"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("🌸 kirim emoji untuk di set di menu help.\n\ntekan /cancel untuk membatalkan.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message(
                "emoji salah",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} diubah ke {themssg}\n",
                buttons=get_back_button("otvars"),
            )


@callback("plg")
@owner
async def pluginch(event):
    await event.delete()
    pru = event.sender_id
    var = "PLUGIN_CHANNEL"
    name = "Plugin Channel"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "kirim id atau username channel dari mana anda ingin menginstal semua plugin.\n\natur ke ~ @ultroidplugin jika ingin mendapatkan 1300+ plugins.\n\nklik /cancel untuk membatalkan.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            return await conv.send_message(
                "channel tidak valid.",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} diatur ke {}\n sekarang ketik restart agar plugins terinstall.".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("otvars"),
            )


@callback("hhndlr")
@owner
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "HNDLR"
    name = "Handler / Trigger"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"kirimkan simbol yang mau kamu atur sebagai Handler/Trigger untuk mengakses bot.\nhandler default mu [ `{HNDLR}` ]\n\n klik /cancel untuk batal.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("otvars"),
            )
        elif len(themssg) > 1:
            return await conv.send_message(
                "handler tidak valid.",
                buttons=get_back_button("otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            return await conv.send_message(
                "simbol ini tidak bisa diatur sebagai handler.",
                buttons=get_back_button("otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} diatur ke {themssg}",
                buttons=get_back_button("otvars"),
            )


@callback("taglog")
@owner
async def tagloggrr(e):
    await e.edit(
        "pilih pengaturan",
        buttons=[
            [Button.inline("sᴇᴛ ᴛᴀɢ ʟᴏɢ", data="settag")],
            [Button.inline("ᴅᴇʟᴇᴛᴇ ᴛᴀɢ ʟᴏɢ", data="deltag")],
            [Button.inline("« ʙᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("deltag")
@owner
async def delfuk(e):
    udB.delete("TAG_LOG")
    await e.answer("selesai, tag log dimatikan !")


@callback("settag")
@owner
async def taglogerr(event):
    await event.delete()
    pru = event.sender_id
    var = "TAG_LOG"
    name = "Tag Log Group"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"buat sebuah grup, tambahkan asisstant bot mu dan jadikan admin.\nambil `{hndlr}id` grup itu dan kirim kesini untuk diatur di tag logs.\n\nklik /cancel untuk membatalkan.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("taglog"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} diatur ke {themssg}",
                buttons=get_back_button("taglog"),
            )


@callback("eaddon")
@owner
async def pmset(event):
    await event.edit(
        "Addons ~ Extra Plugins:",
        buttons=[
            [Button.inline("ᴀᴅᴅᴏɴs ᴏɴ", data="edon")],
            [Button.inline("ᴀᴅᴅᴏɴs ᴏғғ", data="edof")],
            [Button.inline("« ʙᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("edon")
@owner
async def eddon(event):
    var = "ADDONS"
    await setit(event, var, "True")
    await event.edit(
        "Baik !!, Addons sudah dinyalakan.\n\n sekarang ketik restart agar perubahan disimpan.",
        buttons=get_back_button("eaddon"),
    )


@callback("edof")
@owner
async def eddof(event):
    var = "ADDONS"
    await setit(event, var, "False")
    await event.edit(
        "Baik !!, Addons sudah dinonaktifkan.\n\n sekarang ketik restart agar perubahan disimpan.",
        buttons=get_back_button("eaddon"),
    )


@callback("sudo")
@owner
async def pmset(event):
    await event.edit(
        f"mode sudo ~ untuk mengizinkan orang lain mengakses userbot mu. info lengkap ketik `{HNDLR}help sudo`",
        buttons=[
            [Button.inline("ᴍᴏᴅᴇ sᴜᴅᴏ ᴏɴ", data="onsudo")],
            [Button.inline("ᴍᴏᴅᴇ sᴜᴅᴏ ᴏғғ", data="ofsudo")],
            [Button.inline("« ʙᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("onsudo")
@owner
async def eddon(event):
    var = "SUDO"
    await setit(event, var, "True")
    await event.edit(
        "selesai !, mode sudo sudah diaktifkan.\n\n sekarang ketik restart agar perubahan tersimpan.",
        buttons=get_back_button("sudo"),
    )


@callback("ofsudo")
@owner
async def eddof(event):
    var = "SUDO"
    await setit(event, var, "False")
    await event.edit(
        "selesai !, mode sudo sudah dinon-aktifkan.\n\n sekarang ketik restart agar perubahan tersimpan.",
        buttons=get_back_button("sudo"),
    )


@callback("sfban")
@owner
async def sfban(event):
    await event.edit(
        "pengaturan super fban:",
        buttons=[
            [Button.inline("ғʙᴀɴ ɢʀᴏᴜᴘ", data="sfgrp")],
            [Button.inline("ᴇxᴄʟᴜᴅᴇ ғᴇᴅs", data="sfexf")],
            [Button.inline("« ʙᴀᴄᴋ", data="otvars")],
        ],
    )


@callback("sfgrp")
@owner
async def sfgrp(event):
    await event.delete()
    name = "FBAN GROUP ID"
    var = "FBAN_GROUP_ID"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"buat sebuah grup, tambahkan @MissRose_Bot, ketik `{hndlr}id`, salin lalu kirim ke sini.\nklik /cancel untuk membatalkan proses.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("sfban"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} diubah ke {themssg}",
                buttons=get_back_button("sfban"),
            )


@callback("sfexf")
@owner
async def sfexf(event):
    await event.delete()
    name = "Excluded Feds"
    var = "EXCLUDE_FED"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Send the Fed IDs you want to exclude in the ban. Split by a space.\neg`id1 id2 id3`\nSet is as `None` if you dont want any.\nUse /cancel to go back.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("sfban"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} diubah ke {themssg}",
                buttons=get_back_button("sfban"),
            )


@callback("alvcstm")
@owner
async def alvcs(event):
    await event.edit(
        f"kostumisasi tampilan {HNDLR}alive mu. pilih pengaturan dibawah ini 👇🏻",
        buttons=[
            [Button.inline("ᴀʟɪᴠᴇ ᴛᴇxᴛ", data="alvtx")],
            [Button.inline("ᴀʟɪᴠᴇ ᴍᴇᴅɪᴀ", data="alvmed")],
            [Button.inline("ʜᴀᴘᴜs ᴀʟɪᴠᴇ ᴍᴇᴅɪᴀ", data="delmed")],
            [Button.inline("« ʙᴀᴄᴋ", data="setter")],
        ],
    )


@callback("alvtx")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_TEXT"
    name = "Alive Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**alive text**\nkirimkan pesan baru untuk alive text.\n\nklik /cancel untuk membatalkan.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("alvcstm"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} diatur ke {}\n\nsekarang ketik restart agar perubahan tersimpan.".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("alvcstm"),
            )


@callback("alvmed")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_PIC"
    name = "Alive Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**alive media**\nkirimkan saya gambar/gif/bot api id dari sticker untuk diatur sebagai alive media.\n\nklik /cancel untuk membatalkan.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "dibatalkan !!",
                    buttons=get_back_button("alvcstm"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "alvpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "TERMINATED.",
                    buttons=get_back_button("alvcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} telah diatur.",
            buttons=get_back_button("alvcstm"),
        )


@callback("delmed")
@owner
async def dell(event):
    try:
        udB.delete("ALIVE_PIC")
        return await event.edit("selesai !", buttons=get_back_button("alvcstm"))
    except BaseException:
        return await event.edit(
            "terjadi kesalahan.",
            buttons=get_back_button("alvcstm"),
        )


@callback("pmcstm")
@owner
async def alvcs(event):
    await event.edit(
        "kostumisasi pengaturan pmpermit anda 👇🏻",
        buttons=[
            [
                Button.inline("ᴘᴍ ᴛᴇxᴛ", data="pmtxt"),
                Button.inline("ᴘᴍ ᴍᴇᴅɪᴀ", data="pmmed"),
            ],
            [
                Button.inline("ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇ", data="apauto"),
                Button.inline("ᴘᴍ ʟᴏɢɢᴇʀ", data="pml"),
            ],
            [
                Button.inline("sᴇᴛ ᴡᴀʀɴs", data="swarn"),
                Button.inline("ʜᴀᴘᴜs ᴘᴍ ᴍᴇᴅɪᴀ", data="delpmmed"),
            ],
            [Button.inline("« ʙᴀᴄᴋ", data="ppmset")],
        ],
    )


@callback("pmtxt")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "PM_TEXT"
    name = "PM Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**pm text**\nkirimkan pesan baru untuk pmpermit.\n\nanda bisa menggunakan `{name}` `{fullname}` `{count}` `{mention}` `{username}` untuk mendapatkan ini dari pengguna juga\n\nklik /cancel untuk membatalkan.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("pmcstm"),
            )
        else:
            if len(themssg) > 4090:
                return await conv.send_message(
                    "pesan terlalu panjang!\nmohon berikan pesan yang sedikit pendek!",
                    buttons=get_back_button("pmcstm"),
                )
            await setit(event, var, themssg)
            await conv.send_message(
                "{} diatur ke {}\n\nsekarang ketik restart agar perubahan tersimpan.".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("pmcstm"),
            )


@callback("swarn")
@owner
async def name(event):
    m = range(1, 10)
    tultd = [Button.inline(f"{x}", data=f"wrns_{x}") for x in m]
    lst = list(zip(tultd[::3], tultd[1::3], tultd[2::3]))
    lst.append([Button.inline("« Bᴀᴄᴋ", data="pmcstm")])
    await event.edit(
        "atur jumlah peringatan untuk pengguna yang melakukan pm ke anda.",
        buttons=lst,
    )


@callback(re.compile(b"wrns_(.*)"))
@owner
async def set_wrns(event):
    value = int(event.data_match.group(1).decode("UTF-8"))
    dn = udB.set("PMWARNS", value)
    if dn:
        await event.edit(
            f"pm warn diatur ke {value}.\npengguna baru akan mendapat {value} peringatan di pm sebelum diblokir otomatis.",
            buttons=get_back_button("pmcstm"),
        )
    else:
        await event.edit(
            f"terjadi kesalahan, mohon periksa {hndlr}logs anda!",
            buttons=get_back_button("pmcstm"),
        )


@callback("pmmed")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "PMPIC"
    name = "PM Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**pm media**\nkirimkan saya foto/gif/ atau link untuk diatur sebagai media pmpermit anda.\n\nklik /cancel untuk membatalkan.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "dibatalkan !!",
                    buttons=get_back_button("pmcstm"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "pmpc")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "terminated.",
                    buttons=get_back_button("pmcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} telah diatur.",
            buttons=get_back_button("pmcstm"),
        )


@callback("delpmmed")
@owner
async def dell(event):
    try:
        udB.delete("PMPIC")
        return await event.edit("selesai !", buttons=get_back_button("pmcstm"))
    except BaseException:
        return await event.edit(
            "terjadi kesalahan...",
            buttons=[[Button.inline("« sᴇᴛᴛɪɴɢs", data="setter")]],
        )


@callback("apauto")
@owner
async def apauto(event):
    await event.edit(
        "ini adalah menu auto approve untuk pesan masuk.",
        buttons=[
            [Button.inline("ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ᴏɴ", data="apon")],
            [Button.inline("ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ᴏғғ", data="apof")],
            [Button.inline("« ʙᴀᴄᴋ", data="pmcstm")],
        ],
    )


@callback("apon")
@owner
async def apon(event):
    var = "AUTOAPPROVE"
    await setit(event, var, "True")
    await event.edit(
        f"DONE!, AUTOAPPROVE STARTED!",
        buttons=[[Button.inline("« ʙᴀᴄᴋ", data="apauto")]],
    )


@callback("apof")
@owner
async def apof(event):
    try:
        udB.delete("AUTOAPPROVE")
        return await event.edit(
            "selesai!, auto approve dihentikan !",
            buttons=[[Button.inline("« Bᴀᴄᴋ", data="apauto")]],
        )
    except BaseException:
        return await event.edit(
            "terjadi kesalahan...",
            buttons=[[Button.inline("« sᴇᴛᴛɪɴɢs", data="setter")]],
        )


@callback("pml")
@owner
async def alvcs(event):
    await event.edit(
        "pm logger, ini akan meneruskan pesan dari pm ke grup private anda -",
        buttons=[
            [Button.inline("ᴘᴍʟᴏɢɢᴇʀ ᴏɴ", data="pmlog")],
            [Button.inline("ᴘᴍʟᴏɢɢᴇʀ ᴏғғ", data="pmlogof")],
            [Button.inline("« Bᴀᴄᴋ", data="pmcstm")],
        ],
    )


@callback("pmlog")
@owner
async def pmlog(event):
    var = "PMLOG"
    await setit(event, var, "True")
    await event.edit(
        f"selesai!, pm logger diaktifkan!",
        buttons=[[Button.inline("« ʙᴀᴄᴋ", data="pml")]],
    )


@callback("pmlogof")
@owner
async def pmlogof(event):
    try:
        udB.delete("PMLOG")
        return await event.edit(
            "selesai!, pm logger dimatikan!",
            buttons=[[Button.inline("« Bᴀᴄᴋ", data="pml")]],
        )
    except BaseException:
        return await event.edit(
            "terjadi kesalahan...",
            buttons=[[Button.inline("« Sᴇᴛᴛɪɴɢs", data="setter")]],
        )


@callback("ppmset")
@owner
async def pmset(event):
    await event.edit(
        "pengaturan untuk pm-permit:",
        buttons=[
            [Button.inline("ᴀᴋᴛɪғᴋᴀɴ ᴘᴍᴘᴇʀᴍɪᴛ", data="pmon")],
            [Button.inline("ᴍᴀᴛɪᴋᴀɴ ᴘᴍᴘᴇʀᴍɪᴛ", data="pmoff")],
            [Button.inline("ᴋᴏsᴛᴜᴍɪsᴀsɪ ᴘᴍᴘᴇʀᴍɪᴛ", data="pmcstm")],
            [Button.inline("« Bᴀᴄᴋ", data="setter")],
        ],
    )


@callback("pmon")
@owner
async def pmonn(event):
    var = "PMSETTING"
    await setit(event, var, "True")
    await event.edit(
        f"selesai!, pm-permit telah diaktifkan!",
        buttons=[[Button.inline("« ʙᴀᴄᴋ", data="ppmset")]],
    )


@callback("pmoff")
@owner
async def pmofff(event):
    var = "PMSETTING"
    await setit(event, var, "False")
    await event.edit(
        f"selesai!, pm-permit telah dimatikan!",
        buttons=[[Button.inline("« ʙᴀᴄᴋ", data="ppmset")]],
    )


@callback("chatbot")
@owner
async def chbot(event):
    await event.edit(
        f"dengan fitur ini anda dapat bertukar pesan dengan pengguna lain melalui bot ini.\n[info lengkap lihat disini](https://t.me/sakuraupdateschannel/3)",
        buttons=[
            [Button.inline("ᴄʜᴀᴛ ʙᴏᴛ ᴏɴ", data="onchbot")],
            [Button.inline("ᴄʜᴀᴛ ʙᴏᴛ ᴏғғ", data="ofchbot")],
            [Button.inline("ʙᴏᴛ ᴡᴇʟᴄᴏᴍᴇ", data="bwel")],
            [Button.inline("« ʙᴀᴄᴋ", data="setter")],
        ],
        link_preview=False,
    )


@callback("bwel")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "STARTMSG"
    name = "Bot Welcome Message:"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**BOT WELCOME MSG**\nberikan pesan untuk ditampilkan saat orang lain menekan tombol start di bot anda.\n\nklik /cancel untuk membatalkan.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("chatbot"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} diubah ke {}".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("chatbot"),
            )


@callback("onchbot")
@owner
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "True")
    await event.edit(
        "done! kini anda bisa bertukar pesan dengan orang lain melalui bot ini.",
        buttons=[Button.inline("« ʙᴀᴄᴋ", data="chatbot")],
    )


@callback("ofchbot")
@owner
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "False")
    await event.edit(
        "done! bertukar pesan dengan orang melalui bot ini di hentikan.",
        buttons=[Button.inline("« ʙᴀᴄᴋ", data="chatbot")],
    )


@callback("vcb")
@owner
async def vcb(event):
    await event.edit(
        f"dengan fitur ini anda dapat memutar musik di vcg melalui bot ini\n\n[info selengkapya](https://t.me/sakuraupdateschannel/3)",
        buttons=[
            [Button.inline("ᴠᴄ sᴇssɪᴏɴ", data="vcs")],
            [Button.inline("« ʙᴀᴄᴋ", data="setter")],
        ],
        link_preview=False,
    )


@callback("vcs")
@owner
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "VC_SESSION"
    name = "VC SESSION"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Vc session**\nberikan string session baru untuk vc bot.\n\nklik /cancel untuk membatalkan.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("vcb"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                "{} diatur ke {}\n\nsekarang restart untuk menyimpan perubahan".format(
                    name,
                    themssg,
                ),
                buttons=get_back_button("vcb"),
            )


@callback("inli_pic")
@owner
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "INLINE_PIC"
    name = "Inline Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Inline Media**\nkirimkan saya foto/gif/ atau link untuk diatur sebagai inline media.\n\nklik /cancel untuk membatalkan.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "dibatalkan !!",
                    buttons=get_back_button("setter"),
                )
        except BaseException:
            pass
        media = await event.client.download_media(response, "inlpic")
        if (
            not (response.text).startswith("/")
            and not response.text == ""
            and not response.media
        ):
            url = response.text
        else:
            try:
                x = upl(media)
                url = f"https://telegra.ph/{x[0]}"
                remove(media)
            except BaseException:
                return await conv.send_message(
                    "Terminated.",
                    buttons=get_back_button("setter"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} telah diatur.",
            buttons=get_back_button("setter"),
        )
