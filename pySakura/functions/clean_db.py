# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from .. import udB


def is_clean_added(chat):
    if k := udB.get("CLEANCHAT"):
        if str(chat) in k:
            return True
        return
    return


def add_clean(chat):
    if not is_clean_added(chat):
        if k := udB.get("CLEANCHAT"):
            return udB.set("CLEANCHAT", f'{k} {str(chat)}')
        return udB.set("CLEANCHAT", str(chat))
    return


def rem_clean(chat):
    if is_clean_added(chat):
        k = udB.get("CLEANCHAT")
        udB.set("CLEANCHAT", k.replace(str(chat), ""))
        return True
    return
