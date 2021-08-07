# Sakura - UserBot

import re

from . import *


@callback("lang")
@owner
async def setlang(event):
    languages = get_languages()
    tultd = [
        Button.inline(
            f"{languages[ult]['natively']} [{ult.lower()}]",
            data=f"set_{ult}",
        )
        for ult in languages
    ]
    buttons = list(zip(tultd[::2], tultd[1::2]))
    if len(tultd) % 2 == 1:
        buttons.append((tultd[-1],))
    buttons.append([Button.inline("« ʙᴀᴄᴋ", data="mainmenu")])
    await event.edit("🏳️‍🌈 daftar bahasa yang tersedia.", buttons=buttons)


@callback(re.compile(b"set_(.*)"))
@owner
async def settt(event):
    lang = event.data_match.group(1).decode("UTF-8")
    languages = get_languages()
    udB.set("language", f"{lang}")
    await event.edit(
        f"bahasa anda telah diatur ke {languages[lang]['natively']} [{lang}], sekarang restart untuk menyimpan perubahan",
        buttons=get_back_button("lang"),
    )
