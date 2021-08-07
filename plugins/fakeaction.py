# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📚 Commands Available -

• `{i}ftyping <time/dalam detik>`
  `lakukan aksi palsu mengetik didalam grup. `

• `{i}faudio <time/in secs>`
  `lakukan aksi palsu merekam voice note didalam grup. `

• `{i}fvideo <time/in secs>`
  `lakukan aksi palsu merekam video didalam grup. `

• `{i}fgame <time/in secs>`
  `lakukan aksi palsu bermain game didalam grup. `
"""

from . import *


@ultroid_cmd(pattern="ftyping ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"memulai aksi mengetik palsu dalam {t} detik.")
    async with e.client.action(e.chat_id, "typing"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="faudio ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"memulai aksi merekam audio palsu dalam {t} detik.")
    async with e.client.action(e.chat_id, "record-audio"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="fvideo ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"memulai aksi merekam video palsu dalam {t} detik.")
    async with e.client.action(e.chat_id, "record-video"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="fgame ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"memulai aksi bermain game palsu dalam {t} detik.")
    async with e.client.action(e.chat_id, "game"):
        await asyncio.sleep(t)
