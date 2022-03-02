# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from .. import udB


def lss(list):
    return "".join(
        x if z == len(list) else f"{x}$|" for z, x in enumerate(list, start=1)
    )


def get_blacklist(chat):
    fl = udB.get("BLACKLISTS")
    if not fl:
        return None
    y = eval(fl)
    if y.get(chat):
        return y.get(chat)
    return


def list_blacklist(chat):
    fl = udB.get("BLACKLISTS")
    if not fl:
        return None
    y = eval(fl)
    if y.get(chat):
        allword = (y.get(chat)).split("$|")
        if g := "".join(f"👉`{z}`\n" for z in allword):
            return g
    return


def add_blacklist(chat, word):
    try:
        ok = str({chat: word})
        rt = udB.get("BLACKLISTS")
        if not rt:
            udB.set("BLACKLISTS", ok)
        else:
            y = eval(rt)
            if y.get(chat):
                allword = (y.get(chat)).split("$|")
                for z in allword:
                    if word != z:
                        allword.append(word)
                aword = lss(allword)
                y.pop(chat)
                y.update({chat: aword})
            else:
                y.update({chat: word})
            udB.set("BLACKLISTS", str(y))
            return True
    except Exception as e:
        print(e)
        return False


def rem_blacklist(chat, word):
    masala = udB.get("BLACKLISTS")
    if not masala:
        return
    y = eval(masala)
    if y.get(chat):
        allword = (y.get(chat)).split("$|")
        for z in allword:
            if word == z:
                allword.remove(word)
        aword = lss(allword)
        y.pop(chat)
        y.update({chat: aword})
    return udB.set("BLACKLISTS", str(y))
