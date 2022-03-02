from .. import asst, udB, ultroid_bot  # pylint ignore

CMD_HELP = {}


def sudoers():
    return udB["SUDOS"].split()


def should_allow_sudo():
    return udB["SUDO"] == "True"


def owner_and_sudos():
    return [str(ultroid_bot.uid), *sudoers()]
