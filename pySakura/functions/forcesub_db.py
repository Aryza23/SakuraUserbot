# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import ast

from .. import udB


def get_chats():
    cha = udB.get("FORCESUB")
    if not cha:
        cha = "{}"
    n = [ast.literal_eval(cha)]
    return n[0]


def add_forcesub(chat_id, chattojoin):
    omk = get_chats()
    omk.update({str(chat_id): str(chattojoin)})
    udB.set("FORCESUB", str(omk))
    return True


def get_forcesetting(chat_id):
    omk = get_chats()
    return omk[str(chat_id)] if str(chat_id) in omk.keys() else None


def rem_forcesub(chat_id):
    omk = get_chats()
    if str(chat_id) not in omk.keys():
        return None
    try:
        del omk[str(chat_id)]
        udB.set("FORCESUB", str(omk))
        return True
    except KeyError:
        return False
