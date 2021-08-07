# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📚 Commands Available : Berikut fungsi yg tersedia.

• `{i}airing`
   Dapatkan detail tentang anime yang sedang ditayangkan.

• `{i}anime <anime name>`
   Dapatkan detail anime dari anilist.

• `{i}character <character name>`
   Dapatkan detail karakter anime.
"""

from os import remove

import jikanpy

from . import *


@ultroid_cmd(pattern="airing")
async def airing_anime(event):
    try:
        await eor(event, airing_eps())
    except BaseException:
        info = airing_eps()
        t = info.replace("*", "").replace("`", "")
        with open("animes.txt", "w") as f:
            f.write(t)
        await event.reply(file="animes.txt")
        remove("anime.txt")
        await event.delete()


@ultroid_cmd(pattern="anime ?(.*)")
async def anilist(event):
    name = event.pattern_match.group(1)
    x = await eor(event, get_string("com_1"))
    if not name:
        return await eod(x, "`berikan nama anime!`", time=5)
    banner, title, year, episodes, info = get_anime_src_res(name)
    msg = f"**{title}**\n{year} | {episodes} Episodes.\n\n{info}"
    await event.reply(msg, file=banner, link_preview=True)
    await x.delete()


@ultroid_cmd(pattern="character ?(.*)")
async def anime_char_search(event):
    xx = await eor(event, get_string("com_1"))
    char_name = event.pattern_match.group(1)
    if not char_name:
        await eod(xx, "`berikan nama dari sang karakter juga!`", time=5)
    jikan = jikanpy.jikan.Jikan()
    try:
        s = jikan.search("character", char_name)
    except jikanpy.exceptions.APIException:
        return await eod(xx, "`tidak dapat menemukan karakter!`", time=5)
    a = s["results"][0]["mal_id"]
    char_json = jikan.character(a)
    pic = char_json["image_url"]
    msg = f"**[{char_json['name']}]({char_json['url']})**"
    if char_json["name_kanji"] != "Japanese":
        msg += f" [{char_json['name_kanji']}]\n"
    else:
        msg += "\n"
    if char_json["nicknames"]:
        nicknames_string = ", ".join(char_json["nicknames"])
        msg += f"\n**nicknames** : `{nicknames_string}`\n"
    about = char_json["about"].split("\n", 1)[0].strip().replace("\n", "")
    msg += f"\n**about**: __{about}__"
    await event.reply(msg, file=pic, force_document=False)
    await xx.delete()
