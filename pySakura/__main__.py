# Sakura - UserBot

import asyncio
import multiprocessing
import os
import time
import traceback
import urllib
from pathlib import Path
from random import randint
from urllib.request import urlretrieve

from pyrogram import idle
from pytz import timezone
from telethon.errors.rpcerrorlist import (
    AccessTokenExpiredError,
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
    ChannelsTooMuchError,
    PhoneNumberInvalidError,
)
from telethon.tl.custom import Button
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    EditAdminRequest,
    EditPhotoRequest,
    JoinChannelRequest,
)
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import (
    ChatAdminRights,
    InputChatUploadedPhoto,
    InputMessagesFilterDocument,
)

from . import *
from .dB import DEVLIST
from .dB.database import Var
from .functions.all import updater
from .loader import plugin_loader
from .utils import load_addons

x = ["resources/auths", "resources/downloads", "addons"]
for x in x:
    if not os.path.isdir(x):
        os.mkdir(x)

if udB.get("CUSTOM_THUMBNAIL"):
    urlretrieve(udB.get("CUSTOM_THUMBNAIL"), "resources/extras/sakura.jpg")

if udB.get("GDRIVE_TOKEN"):
    with open("resources/auths/auth_token.txt", "w") as t_file:
        t_file.write(udB.get("GDRIVE_TOKEN"))

if udB.get("MEGA_MAIL") and udB.get("MEGA_PASS"):
    with open(".megarc", "w") as mega:
        mega.write(
            f'[Login]\nUsername = {udB.get("MEGA_MAIL")}\nPassword = {udB.get("MEGA_PASS")}'
        )

if udB.get("TIMEZONE"):
    try:
        timezone(udB.get("TIMEZONE"))
        os.environ["TZ"] = udB.get("TIMEZONE")
        time.tzset()
    except BaseException:
        LOGS.info(
            "Incorrect Timezone ,\nCheck Available Timezone From Here https://telegra.ph/Ultroid-06-18-2\nSo Time is Default UTC"
        )
        os.environ["TZ"] = "UTC"
        time.tzset()


async def autobot():
    await ultroid_bot.start()
    if Var.BOT_TOKEN:
        udB.set("BOT_TOKEN", str(Var.BOT_TOKEN))
        return
    if udB.get("BOT_TOKEN"):
        return
    LOGS.info("membuat bot untuk anda di @BotFather, tunggu sebentar...")
    who = await ultroid_bot.get_me()
    name = who.first_name + "'s assistant bot"
    if who.username:
        username = who.username + "_bot"
    else:
        username = "sakura_" + (str(who.id))[5:] + "_bot"
    bf = "Botfather"
    await ultroid_bot(UnblockRequest(bf))
    await ultroid_bot.send_message(bf, "/cancel")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, "/start")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, "/newbot")
    await asyncio.sleep(1)
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    if isdone.startswith("That I cannot do."):
        LOGS.info(
            "mohon buat bot di @BotFather lalu isi bot token di BOT_TOKEN, dalam bentuk var env lalu restart ulang."
        )
        exit(1)
    await ultroid_bot.send_message(bf, name)
    await asyncio.sleep(1)
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    if not isdone.startswith("Good."):
        await ultroid_bot.send_message(bf, "my assistant bot")
        await asyncio.sleep(1)
        isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
        if not isdone.startswith("Good."):
            LOGS.info(
                "mohon buat bot di @BotFather lalu isi bot token di BOT_TOKEN, dalam bentuk var env lalu restart ulang."
            )
            exit(1)
    await ultroid_bot.send_message(bf, username)
    await asyncio.sleep(1)
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    await ultroid_bot.send_read_acknowledge("botfather")
    if isdone.startswith("Sorry,"):
        ran = randint(1, 100)
        username = "sakura_" + (str(who.id))[6:] + str(ran) + "_bot"
        await ultroid_bot.send_message(bf, username)
        await asyncio.sleep(1)
        nowdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
        if nowdone.startswith("Done!"):
            token = nowdone.split("`")[1]
            udB.set("BOT_TOKEN", token)
            await ultroid_bot.send_message(bf, "/setinline")
            await asyncio.sleep(1)
            await ultroid_bot.send_message(bf, f"@{username}")
            await asyncio.sleep(1)
            await ultroid_bot.send_message(bf, "Search")
            LOGS.info(f"SELESAI, ASSISTANT BOT ANDA SUDAH SELESAI DIBUAT @{username}")
        else:
            LOGS.info(
                f"mohon hapus salah satu bot anda di @Botfather atau set var BOT_TOKEN menggunakan bot token dari bot yang anda buat"
            )
            exit(1)
    elif isdone.startswith("Done!"):
        token = isdone.split("`")[1]
        udB.set("BOT_TOKEN", token)
        await ultroid_bot.send_message(bf, "/setinline")
        await asyncio.sleep(1)
        await ultroid_bot.send_message(bf, f"@{username}")
        await asyncio.sleep(1)
        await ultroid_bot.send_message(bf, "Search")
        LOGS.info(f"SELESAI, ASSISTANT BOT ANDA SUDAH SELESAI DIBUAT @{username}")
    else:
        LOGS.info(
            f"mohon hapus salah satu bot anda di @Botfather atau set var BOT_TOKEN menggunakan bot token dari bot yang anda buat"
        )
        exit(1)


if not udB.get("BOT_TOKEN"):
    ultroid_bot.loop.run_until_complete(autobot())


async def istart():
    ultroid_bot.me = await ultroid_bot.get_me()
    ultroid_bot.uid = ultroid_bot.me.id
    ultroid_bot.first_name = ultroid_bot.me.first_name
    if not ultroid_bot.me.bot:
        udB.set("OWNER_ID", ultroid_bot.uid)


async def autopilot():
    if Var.LOG_CHANNEL and str(Var.LOG_CHANNEL).startswith("-100"):
        udB.set("LOG_CHANNEL", str(Var.LOG_CHANNEL))
    k = []  # To Refresh private ids
    async for x in ultroid_bot.iter_dialogs():
        k.append(x.id)
    if udB.get("LOG_CHANNEL"):
        try:
            await ultroid_bot.get_entity(int(udB.get("LOG_CHANNEL")))
            return
        except BaseException:
            udB.delete("LOG_CHANNEL")
    try:
        r = await ultroid_bot(
            CreateChannelRequest(
                title="🌸 SAKURA LOGS 🌸",
                about="🌸 my sakura logs group\n\n Join @levinachannel",
                megagroup=True,
            ),
        )
    except ChannelsTooMuchError:
        LOGS.info(
            "terlalu banyak channel dan grup, hapus salah satu dan restart lagi"
        )
        exit(1)
    except BaseException:
        LOGS.info(
            "terjadi kesalahan, buat sebuah grup lalu isi id nya di config var LOG_CHANNEL."
        )
        exit(1)
    chat_id = r.chats[0].id
    if not str(chat_id).startswith("-100"):
        udB.set("LOG_CHANNEL", "-100" + str(chat_id))
    else:
        udB.set("LOG_CHANNEL", str(chat_id))
    rights = ChatAdminRights(
        add_admins=True,
        invite_users=True,
        change_info=True,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
        anonymous=False,
        manage_call=True,
    )
    await ultroid_bot(EditAdminRequest(chat_id, asst.me.username, rights, "assistant"))
    pfpa = await ultroid_bot.download_profile_photo(chat_id)
    if not pfpa:
        urllib.request.urlretrieve(
            "https://telegra.ph/file/c43c99a763fe30def0c6f.jpg", "channelphoto.jpg"
        )
        ll = await ultroid_bot.upload_file("channelphoto.jpg")
        await ultroid_bot(EditPhotoRequest(chat_id, InputChatUploadedPhoto(ll)))
        os.remove("channelphoto.jpg")
    else:
        os.remove(pfpa)


async def bot_info():
    asst.me = await asst.get_me()
    return asst.me


LOGS.info("menginialisasi...")


# log in
BOT_TOKEN = udB.get("BOT_TOKEN")
LOGS.info("starting sakura...")
try:
    asst.start(bot_token=BOT_TOKEN)
    ultroid_bot.start()
    ultroid_bot.loop.run_until_complete(istart())
    ultroid_bot.loop.run_until_complete(bot_info())
    LOGS.info("selesai, persiapan selesai")
    LOGS.info("assistant - started")
except (AuthKeyDuplicatedError, PhoneNumberInvalidError, EOFError):
    LOGS.info("String Session expired, mohon buat baru lagi sakura dihentikan...")
    exit(1)
except ApiIdInvalidError:
    LOGS.info("kombinasi API ID & API HASH mu invalid, periksa lagi.")
    exit(1)
except AccessTokenExpiredError:
    udB.delete("BOT_TOKEN")
    LOGS.info(
        "BOT_TOKEN expired , So Quitted The Process, Restart Again To create A new Bot. Or Set BOT_TOKEN env In Vars"
    )
    exit(1)
except BaseException:
    LOGS.info("Error: " + str(traceback.print_exc()))
    exit(1)


if str(ultroid_bot.uid) not in DEVLIST:
    chat = eval(udB.get("BLACKLIST_CHATS"))
    if -1001327032795 not in chat:
        chat.append(-1001327032795)
        udB.set("BLACKLIST_CHATS", str(chat))

ultroid_bot.loop.run_until_complete(autopilot())

pmbot = udB.get("PMBOT")
manager = udB.get("MANAGER")
addons = udB.get("ADDONS") or Var.ADDONS
vcbot = udB.get("VC_SESSION") or Var.VC_SESSION

plugin_loader(addons=addons, pmbot=pmbot, manager=manager, vcbot=vcbot)

# for channel plugins
Plug_channel = udB.get("PLUGIN_CHANNEL")
if Plug_channel:

    async def plug():
        try:
            if Plug_channel.startswith("@"):
                chat = Plug_channel
            else:
                try:
                    chat = int(Plug_channel)
                except BaseException:
                    return
            async for x in ultroid_bot.iter_messages(
                chat, search=".py", filter=InputMessagesFilterDocument
            ):
                await asyncio.sleep(0.6)
                files = await ultroid_bot.download_media(x.media, "./addons/")
                file = Path(files)
                plugin = file.stem
                if "(" not in files:
                    try:
                        load_addons(plugin.replace(".py", ""))
                        LOGS.info(f"Sakura - PLUGIN_CHANNEL - Installed - {plugin}")
                    except Exception as e:
                        LOGS.info(f"Sakura - PLUGIN_CHANNEL - ERROR - {plugin}")
                        LOGS.info(str(e))
                else:
                    LOGS.info(f"Plugin {plugin} is Pre Installed")
                    os.remove(files)
        except Exception as e:
            LOGS.info(str(e))


# customize assistant


async def customize():
    try:
        chat_id = int(udB.get("LOG_CHANNEL"))
        xx = await ultroid_bot.get_entity(asst.me.username)
        if xx.photo is None:
            LOGS.info("mengkostumisasi bot anda di @BOTFATHER")
            UL = f"@{asst.me.username}"
            if (ultroid_bot.me.username) is None:
                sir = ultroid_bot.me.first_name
            else:
                sir = f"@{ultroid_bot.me.username}"
            await ultroid_bot.send_message(
                chat_id, "kostumisasi otomatis dimulai di @botfather"
            )
            await asyncio.sleep(1)
            await ultroid_bot.send_message("botfather", "/cancel")
            await asyncio.sleep(1)
            await ultroid_bot.send_message("botfather", "/start")
            await asyncio.sleep(1)
            await ultroid_bot.send_message("botfather", "/setuserpic")
            await asyncio.sleep(1)
            await ultroid_bot.send_message("botfather", UL)
            await asyncio.sleep(1)
            await ultroid_bot.send_file(
                "botfather", "resources/extras/sakura_assistant.jpg"
            )
            await asyncio.sleep(2)
            await ultroid_bot.send_message("botfather", "/setabouttext")
            await asyncio.sleep(1)
            await ultroid_bot.send_message("botfather", UL)
            await asyncio.sleep(1)
            await ultroid_bot.send_message(
                "botfather", f"🌸 Hello, im assistant bot of {sir}"
            )
            await asyncio.sleep(2)
            await ultroid_bot.send_message("botfather", "/setdescription")
            await asyncio.sleep(1)
            await ultroid_bot.send_message("botfather", UL)
            await asyncio.sleep(1)
            await ultroid_bot.send_message(
                "botfather",
                f"🌸 sakura assistant bot 🌸\n\n👩🏻‍💻 master » {sir} ✨\n\n✨ powered by » @levinachannel\n✨ support » @VeezSupportGroup",
            )
            await asyncio.sleep(2)
            await ultroid_bot.send_message(
                chat_id, "**kostumisasi otomatis** selesai dilakukan di @BotFather"
            )
            LOGS.info("kostumisasi selesai")
    except Exception as e:
        LOGS.info(str(e))


# some stuffs
async def ready():
    chat_id = int(udB.get("LOG_CHANNEL"))
    MSG = f"**🌸SAKURA USERBOT AKTIF🌸**\n➖➖➖➖➖➖➖➖➖➖➖\n⚡**pengguna** : [{ultroid_bot.me.first_name}](tg://user?id={ultroid_bot.me.id})\n⚡**assistant** : @{asst.me.username}\n➖➖➖➖➖➖➖➖➖➖➖\n💖**support** : @levinachannel\n➖➖➖➖➖➖➖➖➖➖➖"
    BTTS = [Button.inline("✨ BUKA MENU HELP ✨", "open")]
    updava = await updater()
    try:
        if updava:
            BTTS = [
                [Button.inline("UPDATE TERSEDIA", "updtavail")],
                [Button.inline("✨ MENU HELP ✨", "open")],
            ]
        await asst.send_message(chat_id, MSG, buttons=BTTS)
    except BaseException:
        try:
            await ultroid_bot.send_message(chat_id, MSG)
        except Exception as ef:
            LOGS.info(ef)
    try:
        # To Let Them know About New Updates and Changes
        await ultroid_bot(JoinChannelRequest("@levinachannel"))
    except BaseException:
        pass


def pycli():
    vcasst.start()
    multiprocessing.Process(target=idle).start()
    CallsClient.run()


suc_msg = """
            -----------------------------------
             🌸 Sakura Userbot Sudah Aktif 🌸
            -----------------------------------
"""

ultroid_bot.loop.run_until_complete(customize())
if Plug_channel:
    ultroid_bot.loop.run_until_complete(plug())
ultroid_bot.loop.run_until_complete(ready())


if __name__ == "__main__":
    if vcbot:
        if vcasst and vcClient and CallsClient:
            multiprocessing.Process(target=pycli).start()
        LOGS.info(suc_msg)
        multiprocessing.Process(target=ultroid_bot.run_until_disconnected).start()
    else:
        LOGS.info(suc_msg)
        ultroid_bot.run_until_disconnected()
