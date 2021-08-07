"""
📚 Commands Available -
• `{i}ascii <reply image>`
    konversi gambar menjadi html.
"""
import os

from img2html.converter import Img2HTMLConverter

from . import *


@ultroid_cmd(
    pattern="ascii ?(.*)",
)
async def _(e):
    if not e.reply_to_msg_id:
        return await eor(e, "`balas ke gambar.`")
    m = await eor(e, "`mengkonversi ke html...`")
    img = await (await e.get_reply_message()).download_media()
    char = "■" if not e.pattern_match.group(1) else e.pattern_match.group(1)
    converter = Img2HTMLConverter(char=char)
    html = converter.convert(img)
    with open("html.html", "w") as t:
        t.write(html)
    await e.reply(file="html.html")
    await m.delete()
    os.remove(img)
    os.remove("html.html")
