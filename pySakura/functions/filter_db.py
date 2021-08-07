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


def get_reply(chat, word):
    masala = udB.get("FILTERS")
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


def list_filter(chat):
    fl = udB.get("FILTERS")
    if not fl:
        return None
    rt = fl.split("|||")
    tata = ""
    tar = 0
    for on in rt:
        er = on.split("$|")
        if str(er[0]) == str(chat):
            tata += f"👉 `{er[1]}`\n"
            tar += 1
    if tar == 0:
        return None
    return tata


def rem_all_filter(chat):
    fl = udB.get("FILTERS")
    if not fl:
        return None
    rt = fl.split("|||")
    for on in rt:
        er = on.split("$|")
        if str(er[0]) == str(chat):
            rt.remove(on)
    udB.set("FILTERS", ls(rt))
    return


def get_filter(chat):
    fl = udB.get("FILTERS")
    if not fl:
        return None
    rt = fl.split("|||")
    k = []
    for on in rt:
        er = on.split("$|")
        if str(er[0]) == str(chat):
            k.append(er[1])
    if k:
        return k
    return


def add_filter(chat, word, msg, media):
    try:
        rr = str({"msg": msg, "media": media})
        the_thing = f"{chat}$|{word}$|{rr}"
        rt = udB.get("FILTERS")
        if not rt:
            the_thing = f"{chat}$|{word}$|{rr}"
            udB.set("FILTERS", the_thing)
        else:
            xx = rt.split("|||")
            for y in xx:
                yy = y.split("$|")
                if str(yy[0]) == str(chat):
                    if str(yy[1]) == str(word):
                        xx.remove(y)
                        if the_thing not in xx:
                            xx.append(the_thing)
                    else:
                        if the_thing not in xx:
                            xx.append(the_thing)
                else:
                    if the_thing not in xx:
                        xx.append(the_thing)
            udB.set("FILTERS", ls(xx))
        return True
    except Exception as e:
        print(e)
        return False


def rem_filter(chat, word):
    masala = udB.get("FILTERS")
    if not masala:
        return
    yx = masala.split("|||")
    for i in yx:
        x = i.split("$|")
        if str(x[0]) == str(chat) and str(x[1]) == str(word):
            yx.remove(i)
    return udB.set("FILTERS", ls(yx))
