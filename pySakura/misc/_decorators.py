import inspect
import os
import re
import sys
from pathlib import Path
from time import gmtime, sleep, strftime
from traceback import format_exc

from plugins import sakura_version as ult_ver
from telethon import __version__ as telever
from telethon import events
from telethon.errors.rpcerrorlist import (
    BotMethodInvalidError,
    ChatSendInlineForbiddenError,
    FloodWaitError,
    MessageIdInvalidError,
    UserIsBotError,
)
from telethon.utils import get_display_name

from .. import HNDLR, LOGS, asst, udB, ultroid_bot
from ..dB import DEVLIST
from ..dB.core import LIST, LOADED
from ..functions.all import bash
from ..functions.all import time_formatter as tf
from ..version import __version__ as pyver
from . import owner_and_sudos, should_allow_sudo, sudoers, ultroid_bot
from ._assistant import admin_check
from ._wrappers import eod

hndlr = "\\" + HNDLR

black_list_chats = eval(udB.get("BLACKLIST_CHATS"))


def compile_pattern(data, hndlr):
    if data.startswith(r"\#"):
        pattern = re.compile(data)
    else:
        pattern = re.compile(hndlr + data)
    return pattern


# decorator


def ultroid_cmd(allow_sudo=should_allow_sudo(), **args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    pattern = args["pattern"]
    ppattern = pattern
    groups_only = args.get("groups_only", False)
    admins_only = args.get("admins_only", False)
    ignore_dual = args.get("ignore_dualmode", False)
    type = args.get("type", ["official"])
    manager = udB.get("MANAGER")
    if udB.get("DUAL_MODE"):
        type.append("dualmode")

    if pattern is not None:
        args["pattern"] = compile_pattern(pattern, hndlr)
        reg = re.compile("(.*)")
        try:
            cmd = re.search(reg, pattern)
            try:
                cmd = (
                    cmd.group(1)
                    .replace("$", "")
                    .replace("?(.*)", "")
                    .replace("(.*)", "")
                    .replace("(?: |)", "")
                    .replace("| ", "")
                    .replace("( |)", "")
                    .replace("?((.|//)*)", "")
                    .replace("?P<shortname>\\w+", "")
                )
            except BaseException:
                pass
            try:
                LIST[file_test].append(cmd)
            except BaseException:
                LIST.update({file_test: [cmd]})
        except BaseException:
            pass
    args["blacklist_chats"] = True
    if len(black_list_chats) > 0:
        args["chats"] = black_list_chats

    if "admins_only" in args:
        del args["admins_only"]
    if "groups_only" in args:
        del args["groups_only"]
    if "type" in args:
        del args["type"]
    if "ignore_dualmode" in args:
        del args["ignore_dualmode"]

    def decorator(func):
        pass

        def doit(mode):
            async def wrapper(ult):
                if ult.fwd_from:
                    return
                chat = ult.chat
                if mode == "official":
                    if not ult.out:
                        if not allow_sudo or (str(ult.sender_id) not in sudoers()):
                            return

                    if hasattr(chat, "title"):
                        if (
                            "#noub" in chat.title.lower()
                            and not (chat.admin_rights or chat.creator)
                            and not (str(ult.sender_id) in DEVLIST)
                        ):
                            return
                    if admins_only:
                        if ult.is_private:
                            return await eod(ult, "`gunakan ini di group/channel.`")
                        if not (chat.admin_rights or chat.creator):
                            return await eod(ult, "`saya bukan admin.`")
                elif mode == "dualmode":
                    if str(ult.sender_id) not in owner_and_sudos():
                        return
                elif mode == "manager":
                    if not (ult.out or await admin_check(ult)):
                        return
                if groups_only and ult.is_private:
                    return await eod(ult, "`gunakan ini di group/channel.`")
                try:
                    await func(ult)
                except FloodWaitError as fwerr:
                    await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        f"`FloodWaitError:\n{str(fwerr)}\n\nSleeping for {tf((fwerr.seconds + 10)*1000)}`",
                    )
                    sleep(fwerr.seconds + 10)
                    await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        "`bot sudah bekerja kembali`",
                    )
                except ChatSendInlineForbiddenError:
                    return await eod(ult, "`inline dikunci di obrolan ini.`")
                except (BotMethodInvalidError, UserIsBotError) as boterror:
                    return await eod(ult, str(boterror))
                except MessageIdInvalidError:
                    pass
                except events.StopPropagation:
                    raise events.StopPropagation
                except KeyboardInterrupt:
                    pass
                except BaseException as e:
                    LOGS.exception(e)
                    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    naam = get_display_name(chat)
                    ftext = "**Sakura Client Error:** `Laporkan ini ke` @VeezSupportGroup\n\n"
                    ftext += "`PySakura Version: " + str(pyver)
                    ftext += "\nSakura Version: " + str(ult_ver)
                    ftext += "\nTelethon Version: " + str(telever) + "\n\n"
                    ftext += "-----START SAKURA CRASH LOG-----"
                    ftext += "\nDate: " + date
                    ftext += "\nGroup: " + str(ult.chat_id) + " " + str(naam)
                    ftext += "\nSender ID: " + str(ult.sender_id)
                    ftext += "\nReplied: " + str(ult.is_reply)
                    ftext += "\n\nEvent Trigger:\n"
                    ftext += str(ult.text)
                    ftext += "\n\nTraceback info:\n"
                    ftext += str(format_exc())
                    ftext += "\n\nError text:\n"
                    ftext += str(sys.exc_info()[1])
                    ftext += "\n\n-----END SAKURA CRASH LOG-----"
                    ftext += "\n\n\n🧰 Last 5 commits:\n"

                    stdout, stderr = await bash('git log --pretty=format:"%an: %s" -5')
                    result = str(stdout.strip()) + str(stderr.strip())

                    ftext += result + "`"

                    if len(ftext) > 4096:
                        with open("logs.txt", "w") as log:
                            log.write(ftext)
                        await asst.send_file(
                            int(udB["LOG_CHANNEL"]),
                            "logs.txt",
                            caption="**sakura client error:** `teruskan pesan ini ke` @VeezSupportGroup\n\n",
                        )
                        os.remove("logs.txt")
                    else:
                        await asst.send_message(
                            int(udB["LOG_CHANNEL"]),
                            ftext,
                        )

            return wrapper

        if "official" in type:
            ultroid_bot.add_event_handler(doit("official"), events.NewMessage(**args))
            wrapper = doit("official")
            try:
                LOADED[file_test].append(wrapper)
            except Exception:
                LOADED.update({file_test: [wrapper]})

        if "assistant" in type:
            args["pattern"] = compile_pattern(pattern, "/")
            asst.add_event_handler(doit("assistant"), events.NewMessage(**args))
        if manager and "manager" in type:
            args["pattern"] = compile_pattern(pattern, "/")
            asst.add_event_handler(doit("manager"), events.NewMessage(**args))
        if not ignore_dual and "dualmode" in type:
            DH = udB.get("DUAL_HNDLR")
            args["pattern"] = compile_pattern(ppattern, "\\" + DH)
            asst.add_event_handler(doit("dualmode"), events.NewMessage(**args))

    return decorator
