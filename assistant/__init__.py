# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from pySakura import *
from pySakura.dB.database import Var
from pySakura.functions.all import *
from telethon import Button, custom

from strings import get_languages, get_string

OWNER_NAME = ultroid_bot.me.first_name
OWNER_ID = ultroid_bot.me.id


async def setit(event, name, value):
    try:
        udB.set(name, value)
    except BaseException:
        return await event.edit("`terjadi kesalahan.`")


def get_back_button(name):
    button = [Button.inline("« ʙᴀᴄᴋ", data=f"{name}")]
    return button
