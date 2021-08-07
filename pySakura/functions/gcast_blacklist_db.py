# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from .. import udB


def str_to_list(text):  # Returns List
    return text.split(" ")


def list_to_str(list):  # Returns String
    str = "".join(f"{x} " for x in list)
    return str.strip()


def are_all_nums(list):  # Takes List , Returns Boolean
    return all(item.isdigit() for item in list)


def get_gblacklists():  # Returns List
    gblack = udB.get("GBLACKLISTS")
    if gblack is None or gblack == "":
        return [""]
    else:
        return str_to_list(gblack)


def is_gblacklisted(id):  # Take int or str with numbers only , Returns Boolean
    if not str(id).isdigit():
        return False
    gblack = get_gblacklists()
    return str(id) in gblack


def add_gblacklist(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    try:
        gblack = get_gblacklists()
        gblack.append(id)
        udB.set("GBLACKLISTS", list_to_str(gblack))
        return True
    except Exception as e:
        print(f"Ultroid LOG : // functions/gcast_blacklist_db/add_gblacklist : {e}")
        return False


def rem_gblacklist(id):  # Take int or str with numbers only , Returns Boolean
    id = str(id)
    try:
        gblack = get_gblacklists()
        gblack.remove(id)
        udB.set("GBLACKLISTS", list_to_str(gblack))
        return True
    except Exception as e:
        print(f"Ultroid LOG : // functions/gcast_blacklist_db/rem_gblacklist : {e}")
        return False
