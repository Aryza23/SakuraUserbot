# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from .. import udB


def ls(list):
    z = 0
    xx = ""
    for x in list:
        z += 1
        if z == len(list):
            xx += x
        else:
            xx += f"{x}|||"
    return xx


def get_reply(word):
    masala = udB.get("SNIP")
    if not masala:
        return
    x = masala.split("|||")
    for i in x:
        x = i.split("$|")
        if str(x[0]) == str(word):
            return eval(x[1])
    return None


def list_snip():
    fl = udB.get("SNIP")
    if not fl:
        return None
    rt = fl.split("|||")
    tata = ""
    tar = 0
    for on in rt:
        er = on.split("$|")
        tata += f"👉 `${er[0]}`\n"
        tar += 1
    if tar == 0:
        return None
    return tata


def get_snips():
    if udB.get("SNIP"):
        return True
    else:
        return


def add_snip(word, msg, media):
    try:
        rr = str({"msg": msg, "media": media})
        the_thing = f"{word}$|{rr}"
        rt = udB.get("SNIP")
        if not rt:
            udB.set("SNIP", the_thing)
        else:
            xx = rt.split("|||")
            for y in xx:
                yy = y.split("$|")
                if str(yy[0]) == str(word):
                    xx.remove(y)
                    if the_thing not in xx:
                        xx.append(the_thing)
                else:
                    if the_thing not in xx:
                        xx.append(the_thing)
            udB.set("SNIP", ls(xx))
        return True
    except Exception as e:
        print(e)
        return False


def rem_snip(word):
    masala = udB.get("SNIP")
    if not masala:
        return
    yx = masala.split("|||")
    for i in yx:
        x = i.split("$|")
        if str(x[0]) == str(word):
            yx.remove(i)
    return udB.set("SNIP", ls(yx))
