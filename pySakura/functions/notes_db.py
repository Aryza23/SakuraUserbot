# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from .. import udB


def ls(list):
    return "".join(
        x if z == len(list) else f"{x}|||" for z, x in enumerate(list, start=1)
    )


def get_reply(chat, word):
    masala = udB.get("NOTE")
    if not masala:
        return
    x = masala.split("|||")
    for i in x:
        x = i.split("$|")
        try:
            if str(x[0]) == str(chat) and str(x[1]) == str(word):
                return eval(x[2])
        except BaseException:
            pass
    return None


def list_note(chat):
    fl = udB.get("NOTE")
    if not fl:
        return None
    rt = fl.split("|||")
    tata = ""
    tar = 0
    for on in rt:
        er = on.split("$|")
        if str(er[0]) == str(chat):
            tata += f"👉 #{er[1]}\n"
            tar += 1
    if tar == 0:
        return None
    return tata


def rem_all_note(chat):
    fl = udB.get("NOTE")
    if not fl:
        return None
    rt = fl.split("|||")
    for on in rt:
        er = on.split("$|")
        if str(er[0]) == str(chat):
            rt.remove(on)
    udB.set("NOTE", ls(rt))
    return


def get_notes(chat):
    fl = udB.get("NOTE")
    if not fl:
        return None
    rt = fl.split("|||")
    k = ""
    for on in rt:
        er = on.split("$|")
        if str(er[0]) == str(chat):
            k += "omk"
    return True if k else None


def add_note(chat, word, msg, media):
    try:
        rr = str({"msg": msg, "media": media})
        the_thing = f"{chat}$|{word}$|{rr}"
        rt = udB.get("NOTE")
        if not rt:
            the_thing = f"{chat}$|{word}$|{rr}"
            udB.set("NOTE", the_thing)
        else:
            xx = rt.split("|||")
            for y in xx:
                yy = y.split("$|")
                if str(yy[0]) == str(chat) and str(yy[1]) == str(word):
                    xx.remove(y)
                if the_thing not in xx:
                    xx.append(the_thing)
            udB.set("NOTE", ls(xx))
        return True
    except Exception as e:
        print(e)
        return False


def rem_note(chat, word):
    masala = udB.get("NOTE")
    if not masala:
        return
    yx = masala.split("|||")
    for i in yx:
        x = i.split("$|")
        if str(x[0]) == str(chat) and str(x[1]) == str(word):
            yx.remove(i)
    return udB.set("NOTE", ls(yx))
