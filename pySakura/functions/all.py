# Sakura - UserBot

import asyncio
import io
import json
import math
import os
import random
import re
import sys
import time
import traceback
from json import loads
from math import sqrt
from mimetypes import guess_type
from os import execl
from pathlib import Path
from sys import executable

import aiofiles
import aiohttp
import cloudscraper
import heroku3
import httplib2
import requests
from apiclient.http import MediaFileUpload
from bs4 import BeautifulSoup as bs
from emoji import emojize
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from googleapiclient.discovery import build
from html_telegraph_poster import TelegraphPoster
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from PIL import Image, ImageDraw, ImageFont
from telegraph import Telegraph
from telethon import Button, events
from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    ChannelPublicGroupNaError,
)
from telethon.tl import types
from telethon.tl.functions.channels import (
    GetFullChannelRequest,
    GetParticipantRequest,
    GetParticipantsRequest,
)
from telethon.tl.functions.messages import GetFullChatRequest, GetHistoryRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    ChannelParticipantsAdmins,
    MessageActionChannelMigrateFrom,
    MessageEntityMentionName,
)
from telethon.utils import get_input_location
from youtube_dl import YoutubeDL
from youtube_dl.utils import (
    ContentTooShortError,
    DownloadError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)

from .. import *
from ..dB.core import *
from ..dB.database import Var
from ..misc import *
from ..misc._wrappers import *
from ..utils import *
from ..version import sakura_version
from . import DANGER
from ._FastTelethon import download_file as downloadable
from ._FastTelethon import upload_file as uploadable

OAUTH_SCOPE = "https://www.googleapis.com/auth/drive.file"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
parent_id = udB.get("GDRIVE_FOLDER_ID")
G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
chatbot_base = "https://api.affiliateplus.xyz/api/chatbot?message={message}&botname=Ultroid&ownername={owner}&user=20"

telegraph = Telegraph()
telegraph.create_account(short_name="sakura cmd's list")

request = cloudscraper.create_scraper()

CMD_WEB = {
    "anonfiles": 'curl -F "file=@{}" https://api.anonfiles.com/upload',
    "transfer": 'curl --upload-file "{}" https://transfer.sh/',
    "bayfiles": 'curl -F "file=@{}" https://api.bayfiles.com/upload',
    "x0": 'curl -F "file=@{}" https://x0.at/',
    "file.io": 'curl -F "file=@{}" https://file.io',
    "siasky": 'curl -X POST "https://siasky.net/skynet/skyfile" -F "file=@{}"',
}

UPSTREAM_REPO_URL = "https://github.com/levina-lab/SakuraUserbot"

width_ratio = 0.7
reqs = "resources/extras/local-requirements.txt"
base_url = "https://randomuser.me/api/"


# ---------------YouTube Downloader---------------


def get_data(types, data):
    audio = []
    video = []
    try:
        for m in data["formats"]:
            id = m["format_id"]
            note = m["format_note"]
            size = m["filesize"]
            j = f"{id} {note} {humanbytes(size)}"
            if id == "251":
                a_size = m["filesize"]
            if note == "tiny":
                audio.append(j)
            else:
                if m["acodec"] == "none":
                    id = str(m["format_id"]) + "+" + str(audio[-1].split()[0])
                    j = f"{id} {note} {humanbytes(size+a_size)}"
                    video.append(j)
                else:
                    video.append(j)
    except BaseException:
        pass
    if types == "audio":
        return audio
    elif types == "video":
        return video
    else:
        return []


def get_buttons(typee, listt):
    butts = [
        Button.inline(
            str(x.split(" ", maxsplit=2)[1:])
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
            .replace(",", ""),
            data=typee + x.split(" ", maxsplit=2)[0],
        )
        for x in listt
    ]
    buttons = list(zip(butts[::2], butts[1::2]))
    if len(butts) % 2 == 1:
        buttons.append((butts[-1],))
    return buttons


# ---------------Check Admin---------------


async def check_if_admin(message):
    result = await message.client(
        GetParticipantRequest(
            channel=message.chat_id,
            participant=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, ChannelParticipantCreator) or (
        isinstance(p, ChannelParticipantAdmin)
    )


# ---------------Updater---------------


async def updateme_requirements():
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join(
                [sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", reqs]
            ),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


async def gen_chlog(repo, diff):
    ac_br = repo.active_branch.name
    ch_log = tldr_log = ""
    ch = f"<b>Sakura {sakura_version} updates untuk <a href={UPSTREAM_REPO_URL}/tree/{ac_br}>[{ac_br}]</a>:</b>"
    ch_tl = f"Sakura {sakura_version} updates untuk {ac_br}:"
    d_form = "%d/%m/%y || %H:%M"
    for c in repo.iter_commits(diff):
        ch_log += f"\n\n💬 <b>{c.count()}</b> 🗓 <b>[{c.committed_datetime.strftime(d_form)}]</b>\n<b><a href={UPSTREAM_REPO_URL.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> 👨‍💻 <code>{c.author}</code>"
        tldr_log += f"\n\n💬 {c.count()} 🗓 [{c.committed_datetime.strftime(d_form)}]\n[{c.summary}] 👨‍💻 {c.author}"
    if ch_log:
        return str(ch + ch_log), str(ch_tl + tldr_log)
    else:
        return ch_log, tldr_log


async def updater():
    off_repo = UPSTREAM_REPO_URL
    try:
        repo = Repo()
    except NoSuchPathError as error:
        await asst.send_message(
            int(udB.get("LOG_CHANNEL")), f"{txt}\n`directory {error} is not found`"
        )
        repo.__del__()
        return
    except GitCommandError as error:
        await asst.send_message(
            int(udB.get("LOG_CHANNEL")), f"{txt}\n`Early failure! {error}`"
        )
        repo.__del__()
        return
    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        repo.create_head("main", origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)
    ac_br = repo.active_branch.name
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    changelog, tl_chnglog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    if changelog:
        msg = True
    else:
        msg = False
    return msg


# ----------------Fast Upload/Download----------------


async def uploader(file, name, taime, event, msg):
    with open(file, "rb") as f:
        result = await uploadable(
            client=event.client,
            file=f,
            name=name,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    event,
                    taime,
                    msg,
                ),
            ),
        )
    return result


async def downloader(filename, file, event, taime, msg):
    with open(filename, "wb") as fk:
        result = await downloadable(
            client=event.client,
            location=file,
            out=fk,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    event,
                    taime,
                    msg,
                ),
            ),
        )
    return result


async def download_file(link, name):
    async with aiohttp.ClientSession() as ses:
        async with ses.get(link) as re_ses:
            file = await aiofiles.open(name, "wb")
            await file.write(await re_ses.read())
            await file.close()
    return name


def make_html_telegraph(title, author, text):
    client = TelegraphPoster(use_api=True)
    client.create_api_token(title)
    page = client.post(
        title=title,
        author=author,
        author_url="https://t.me/levinachannel",
        text=text,
    )
    return page["url"]


# ------------------Logo Gen Helpers----------------


def get_text_size(text, image, font):
    im = Image.new("RGB", (image.width, image.height))
    draw = ImageDraw.Draw(im)
    return draw.textsize(text, font)


def find_font_size(text, font, image, target_width_ratio):
    tested_font_size = 100
    tested_font = ImageFont.truetype(font, tested_font_size)
    observed_width, observed_height = get_text_size(text, image, tested_font)
    estimated_font_size = (
        tested_font_size / (observed_width / image.width) * target_width_ratio
    )
    return round(estimated_font_size)


# ------------------Logo Gen Helpers----------------


def make_logo(imgpath, text, funt, **args):
    fill = args.get("fill")
    if args.get("width_ratio"):
        width_ratio = args.get("width_ratio")
    else:
        width_ratio = width_ratio
    stroke_width = int(args.get("stroke_width"))
    stroke_fill = args.get("stroke_fill")

    img = Image.open(imgpath)
    width, height = img.size
    draw = ImageDraw.Draw(img)
    font_size = find_font_size(text, funt, img, width_ratio)
    font = ImageFont.truetype(funt, font_size)
    w, h = draw.textsize(text, font=font)
    draw.text(
        ((width - w) / 2, (height - h) / 2),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )
    file_name = "Logo.png"
    img.save(f"./{file_name}", "PNG")
    img.show()
    return f"{file_name} berhasil digenerate!"


async def get_user_id(ids):
    if str(ids).isdigit():
        userid = int(ids)
    else:
        try:
            userid = (await ultroid_bot.get_entity(ids)).id
        except Exception as exc:
            return str(exc)
    return userid


async def dloader(e, host, file):
    selected = CMD_WEB[host].format(file)
    process = await asyncio.create_subprocess_shell(
        selected, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    os.remove(file)
    return await e.edit(f"`{stdout.decode()}`")


def unlucks(unluck):
    if unluck == "msgs":
        rights = types.ChatBannedRights(
            until_date=None,
            send_messages=False,
            invite_users=False,
            pin_messages=False,
            change_info=False,
        )
    if unluck == "media":
        rights = types.ChatBannedRights(
            until_date=None,
            send_media=False,
        )
    if unluck == "sticker":
        rights = types.ChatBannedRights(
            until_date=None,
            send_stickers=False,
        )
    if unluck == "gif":
        rights = types.ChatBannedRights(
            until_date=None,
            send_gifs=False,
        )
    if unluck == "games":
        rights = types.ChatBannedRights(
            until_date=None,
            send_games=False,
        )
    if unluck == "inlines":
        rights = types.ChatBannedRights(
            until_date=None,
            send_inline=False,
        )
    if unluck == "polls":
        rights = types.ChatBannedRights(
            until_date=None,
            send_polls=False,
        )
    if unluck == "invites":
        rights = types.ChatBannedRights(
            until_date=None,
            invite_users=False,
        )
    if unluck == "pin":
        rights = types.ChatBannedRights(
            until_date=None,
            pin_messages=False,
        )
    if unluck == "changeinfo":
        rights = types.ChatBannedRights(
            until_date=None,
            change_info=False,
        )
    return rights


def lucks(luck):
    if luck == "msgs":
        rights = types.ChatBannedRights(
            until_date=None,
            send_messages=True,
            invite_users=True,
            pin_messages=True,
            change_info=True,
        )
    if luck == "media":
        rights = types.ChatBannedRights(
            until_date=None,
            send_media=True,
        )
    if luck == "sticker":
        rights = types.ChatBannedRights(
            until_date=None,
            send_stickers=True,
        )
    if luck == "gif":
        rights = types.ChatBannedRights(
            until_date=None,
            send_gifs=True,
        )
    if luck == "games":
        rights = types.ChatBannedRights(
            until_date=None,
            send_games=True,
        )
    if luck == "inlines":
        rights = types.ChatBannedRights(
            until_date=None,
            send_inline=True,
        )
    if luck == "polls":
        rights = types.ChatBannedRights(
            until_date=None,
            send_polls=True,
        )
    if luck == "invites":
        rights = types.ChatBannedRights(
            until_date=None,
            invite_users=True,
        )
    if luck == "pin":
        rights = types.ChatBannedRights(
            until_date=None,
            pin_messages=True,
        )
    if luck == "changeinfo":
        rights = types.ChatBannedRights(
            until_date=None,
            change_info=True,
        )
    return rights


async def ban_time(event, time_str):
    if any(time_str.endswith(unit) for unit in ("s", "m", "h", "d")):
        unit = time_str[-1]
        time_int = time_str[:-1]
        if not time_int.isdigit():
            return await event.edit("Invalid time amount specified.")
        if unit == "s":
            bantime = int(time.time() + int(time_int))
        elif unit == "m":
            bantime = int(time.time() + int(time_int) * 60)
        elif unit == "h":
            bantime = int(time.time() + int(time_int) * 60 * 60)
        elif unit == "d":
            bantime = int(time.time() + int(time_int) * 24 * 60 * 60)
        else:
            return ""
        return bantime
    else:
        return await event.edit(
            "Invalid time type specified. Expected s, m,h, or d, got: {}".format(
                time_int[-1]
            )
        )


# gdrive


def list_files(http):
    drive = build("drive", "v2", http=http, cache_discovery=False)
    x = drive.files().get(fileId="").execute()
    files = {}
    for m in x["items"]:
        try:
            files.update({f"{m['title']}": f"{m['webContentLink']}"})
        except KeyError:
            pass
    lists = f"**Total files found in Gdrive:** `{len(files.keys())}`\n\n"
    for l in files:
        lists += f"• [{l}]({files[l]})\n"
    return lists


async def gsearch(http, query, filename):
    drive_service = build("drive", "v2", http=http)
    page_token = None
    msg = "**G-Drive Search:**\n`" + filename + "`\n\n**Results**\n"
    while True:
        response = (
            drive_service.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, items(id, title, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )
        for file in response.get("items", []):
            if file.get("mimeType") == "application/vnd.google-apps.folder":
                msg += (
                    "[{}](https://drive.google.com/drive/folders/{}) (folder)".format(
                        file.get("title"), file.get("id")
                    )
                    + "\n"
                )
            else:
                msg += (
                    "[{}](https://drive.google.com/uc?id={}&export=download)".format(
                        file.get("title"), file.get("id")
                    )
                    + "\n"
                )
        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break
    return msg


async def create_directory(http, directory_name, parent_id):
    drive_service = build("drive", "v2", http=http, cache_discovery=False)
    permissions = {
        "role": "reader",
        "type": "anyone",
        "value": None,
        "withLink": True,
    }
    file_metadata = {
        "title": directory_name,
        "mimeType": G_DRIVE_DIR_MIME_TYPE,
    }
    if parent_id is not None:
        file_metadata["parents"] = [{"id": parent_id}]
    file = drive_service.files().insert(body=file_metadata).execute()
    file_id = file.get("id")
    drive_service.permissions().insert(fileId=file_id, body=permissions).execute()
    return file_id


async def DoTeskWithDir(http, input_directory, event, parent_id):
    list_dirs = os.listdir(input_directory)
    if len(list_dirs) == 0:
        return parent_id
    r_p_id = None
    for a_c_f_name in list_dirs:
        current_file_name = os.path.join(input_directory, a_c_f_name)
        if os.path.isdir(current_file_name):
            current_dir_id = await create_directory(http, a_c_f_name, parent_id)
            r_p_id = await DoTeskWithDir(http, current_file_name, event, current_dir_id)
        else:
            file_name, mime_type = file_ops(current_file_name)
            g_drive_link = await upload_file(
                http, current_file_name, file_name, mime_type, event, parent_id
            )
            r_p_id = parent_id
    return r_p_id


def file_ops(file_path):
    mime_type = guess_type(file_path)[0]
    mime_type = mime_type if mime_type else "text/plain"
    file_name = file_path.split("/")[-1]
    return file_name, mime_type


async def create_token_file(token_file, event):
    flow = OAuth2WebServerFlow(
        udB.get("GDRIVE_CLIENT_ID"),
        udB.get("GDRIVE_CLIENT_SECRET"),
        OAUTH_SCOPE,
        redirect_uri=REDIRECT_URI,
    )
    authorize_url = flow.step1_get_authorize_url()
    async with asst.conversation(ultroid_bot.uid) as conv:
        await event.edit(
            f"Go to the following link in your browser: [Authorization Link]({authorize_url}) and reply the code",
            link_preview=False,
        )
        response = conv.wait_event(events.NewMessage(from_users=ultroid_bot.uid))
        response = await response
        code = response.message.message.strip()
        credentials = flow.step2_exchange(code)
        storage = Storage(token_file)
        storage.put(credentials)
        return storage


def authorize(token_file, storage):
    if storage is None:
        storage = Storage(token_file)
    credentials = storage.get()
    http = httplib2.Http()
    credentials.refresh(http)
    http = credentials.authorize(http)
    return http


async def upload_file(http, file_path, file_name, mime_type, event, parent_id):
    drive_service = build("drive", "v2", http=http, cache_discovery=False)
    media_body = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    body = {
        "title": file_name,
        "description": "Uploaded using Sakura Userbot",
        "mimeType": mime_type,
    }
    if parent_id is not None:
        body["parents"] = [{"id": parent_id}]
    permissions = {
        "role": "reader",
        "type": "anyone",
        "value": None,
        "withLink": True,
    }
    os.path.getsize(file_path)
    file = drive_service.files().insert(body=body, media_body=media_body)
    times = time.time()
    response = None
    display_message = ""
    while response is None:
        status, response = file.next_chunk(num_retries=5)
        if status:
            t_size = status.total_size
            diff = time.time() - times
            uploaded = status.resumable_progress
            percentage = uploaded / t_size * 100
            speed = round(uploaded / diff, 2)
            eta = round((t_size - uploaded) / speed)
            progress_str = "`{0}{1} {2}%`".format(
                "".join(["●" for i in range(math.floor(percentage / 5))]),
                "".join(["" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )
            current_message = (
                f"`✦ Uploading to G-Drive`\n\n"
                + f"`✦ File Name:` `{file_name}`\n\n"
                + f"{progress_str}\n\n"
                + f"`✦ Uploaded:` `{humanbytes(uploaded)} of {humanbytes(t_size)}`\n"
                + f"`✦ Speed:` `{humanbytes(speed)}`\n"
                + f"`✦ ETA:` `{time_formatter(eta*1000)}`"
            )
            if display_message != current_message:
                try:
                    await event.edit(current_message)
                    display_message = current_message
                except Exception:
                    pass
    file_id = response.get("id")
    drive_service.permissions().insert(fileId=file_id, body=permissions).execute()
    file = drive_service.files().get(fileId=file_id).execute()
    download_url = file.get("webContentLink")
    return download_url


# Gdrive End


def dani_ck(filroid):
    if os.path.exists(filroid):
        no = 1
        while True:
            ult = "{0}_{2}{1}".format(*os.path.splitext(filroid) + (no,))
            if os.path.exists(ult):
                no += 1
            else:
                return ult
    return filroid


def un_plug(shortname):
    try:
        try:
            for i in LOADED[shortname]:
                ultroid_bot.remove_event_handler(i)
            try:
                del LOADED[shortname]
                del LIST[shortname]
                ADDONS.remove(shortname)
            except BaseException:
                pass

        except BaseException:
            name = f"addons.{shortname}"

            for i in reversed(range(len(ultroid_bot._event_builders))):
                ev, cb = ultroid_bot._event_builders[i]
                if cb.__module__ == name:
                    del ultroid_bot._event_builders[i]
                    try:
                        del LOADED[shortname]
                        del LIST[shortname]
                        ADDONS.remove(shortname)
                    except KeyError:
                        pass
    except BaseException:
        raise ValueError


async def dler(ev, url):
    try:
        await ev.edit("`Fetching data, please wait..`")
        ytdl_data = YoutubeDL().extract_info(url=url, download=False)
    except DownloadError as DE:
        return await ev.edit(f"`{str(DE)}`")
    except ContentTooShortError:
        return await ev.edit("`The download content was too short.`")
    except GeoRestrictedError:
        return await ev.edit(
            "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`",
        )
    except MaxDownloadsReached:
        return await ev.edit("`Max-downloads limit has been reached.`")
    except PostProcessingError:
        return await ev.edit("`There was an error during post processing.`")
    except UnavailableVideoError:
        return await ev.edit("`Media is not available in the requested format.`")
    except XAttrMetadataError as XAME:
        return await ev.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
    except ExtractorError:
        return await ev.edit("`There was an error during info extraction.`")
    except BrokenPipeError as x:
        return await ev.edit(f"`{str(x)}`")
    except Exception as e:
        return await ev.edit(f"{str(type(e))}: {str(e)}")
    return ytdl_data


def time_formatter(milliseconds: int) -> str:
    """Inputs time in milliseconds, to get beautified time,
    as string"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + "w:") if weeks else "")
        + ((str(days) + "d:") if days else "")
        + ((str(hours) + "h:") if hours else "")
        + ((str(minutes) + "m:") if minutes else "")
        + ((str(seconds) + "s:") if seconds else "")
    )
    if tmp.endswith(":"):
        return tmp[:-1]
    else:
        return tmp


def humanbytes(size):
    if size in [None, ""]:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
        if size < 1024:
            break
        size /= 1024
    return f"{size:.2f} {unit}"


async def progress(current, total, event, start, type_of_ps, file_name=None):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        progress_str = "`[{0}{1}] {2}%`\n\n".format(
            "".join(["●" for i in range(math.floor(percentage / 5))]),
            "".join(["" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )
        tmp = (
            progress_str
            + "`{0} of {1}`\n\n`✦ Speed: {2}/s`\n\n`✦ ETA: {3}`\n\n".format(
                humanbytes(current),
                humanbytes(total),
                humanbytes(speed),
                time_formatter(time_to_completion),
            )
        )
        if file_name:
            await event.edit(
                "`✦ {}`\n\n`File Name: {}`\n\n{}".format(type_of_ps, file_name, tmp)
            )
        else:
            await event.edit("`✦ {}`\n\n{}".format(type_of_ps, tmp))


async def restart(ult):
    if Var.HEROKU_APP_NAME and Var.HEROKU_API:
        try:
            Heroku = heroku3.from_key(Var.HEROKU_API)
            app = Heroku.apps()[Var.HEROKU_APP_NAME]
            await ult.edit("`memulai ulang userbot anda, mohon tunggu beberapa menit!`")
            app.restart()
        except BaseException:
            return await eor(
                ult,
                "`HEROKU_API` atau `HEROKU_APP_NAME` invalid! mohon cek ulang di config vars anda.",
            )
    else:
        execl(executable, executable, "-m", "pySakura")


async def shutdown(ult, dynotype="sakura"):
    ult = await eor(ult, "Shutting Down")
    if Var.HEROKU_APP_NAME and Var.HEROKU_API:
        try:
            Heroku = heroku3.from_key(Var.HEROKU_API)
            app = Heroku.apps()[Var.HEROKU_APP_NAME]
        except BaseException:
            return await ult.edit(
                "`HEROKU_API` dan `HEROKU_APP_NAME` invalid! mohon cek ulang di config vars anda."
            )
        await ult.edit("`mematikan userbot anda, mohon tunggu beberapa menit!`")
        app.process_formation()[dynotype].scale(0)
    else:
        sys.exit(0)


async def get_user_info(event):
    args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.sender_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]
        if user.isnumeric():
            user = int(user)
        if not user:
            await event.edit("`balas ke pengguna atau berikan id/nama nya.`")
            return None, None
        if event.message.entities:
            probable_user_mention_entity = event.message.entities[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj, extra
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError):
            return None, None
    return user_obj, extra


def ReTrieveFile(input_file_name):
    RMBG_API = udB.get("RMBG_API")
    headers = {"X-API-Key": RMBG_API}
    files = {"image_file": (input_file_name, open(input_file_name, "rb"))}
    r = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        headers=headers,
        files=files,
        allow_redirects=True,
        stream=True,
    )
    return r


async def resize_photo(photo):
    """Resize the given photo to 512x512"""
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)
    return image


async def get_full_user(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.forward:
            replied_user = await event.client(
                GetFullUserRequest(
                    previous_message.forward.from_id
                    or previous_message.forward.channel_id
                )
            )
            return replied_user, None
        else:
            replied_user = await event.client(
                GetFullUserRequest(previous_message.sender_id)
            )
            return replied_user, None
    else:
        input_str = None
        try:
            input_str = await get_user_id(event.pattern_match.group(1))
        except IndexError as e:
            return None, e
        if event.message.entities is not None:
            mention_entity = event.message.entities
            probable_user_mention_entity = mention_entity[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            else:
                try:
                    user_object = await event.client.get_entity(int(input_str))
                    user_id = user_object.id
                    replied_user = await event.client(GetFullUserRequest(user_id))
                    return replied_user, None
                except Exception as e:
                    return None, e
        elif event.is_private:
            try:
                user_id = event.chat_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
        else:
            try:
                user_object = await event.client.get_entity(int(input_str))
                user_id = user_object.id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e


def make_mention(user):
    if user.username:
        return f"@{user.username}"
    else:
        return inline_mention(user)


def inline_mention(user):
    full_name = user_full_name(user) or "No Name"
    return f"[{full_name}](tg://user?id={user.id})"


def user_full_name(user):
    names = [user.first_name, user.last_name]
    names = [i for i in list(names) if i]
    full_name = " ".join(names)
    return full_name


async def get_chatinfo(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await ultroid_bot(GetFullChatRequest(chat))
    except BaseException:
        try:
            chat_info = await ultroid_bot(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await eor(event, "`invalid channel/group`")
            return None
        except ChannelPrivateError:
            await eor(
                event, "`ini adalah channel/group private atau saya dibanned dari sana`"
            )
            return None
        except ChannelPublicGroupNaError:
            await eor(event, "`channel atau grup tidak tersedia`")
            return None
        except (TypeError, ValueError) as err:
            await eor(event, str(err))
            return None
    return chat_info


async def fetch_info(chat, event):
    chat_obj_info = await ultroid_bot.get_entity(chat.full_chat.id)
    broadcast = (
        chat_obj_info.broadcast if hasattr(chat_obj_info, "broadcast") else False
    )
    chat_type = "Channel" if broadcast else "Group"
    chat_title = chat_obj_info.title
    warn_emoji = emojize(":warning:")
    try:
        msg_info = await ultroid_bot(
            GetHistoryRequest(
                peer=chat_obj_info.id,
                offset_id=0,
                offset_date=None,
                add_offset=-0,
                limit=0,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
    except Exception as e:
        msg_info = None
        print("Exception:", e)
    first_msg_valid = (
        True
        if msg_info and msg_info.messages and msg_info.messages[0].id == 1
        else False
    )
    creator_valid = True if first_msg_valid and msg_info.users else False
    creator_id = msg_info.users[0].id if creator_valid else None
    creator_firstname = (
        msg_info.users[0].first_name
        if creator_valid and msg_info.users[0].first_name is not None
        else "Deleted Account"
    )
    creator_username = (
        msg_info.users[0].username
        if creator_valid and msg_info.users[0].username is not None
        else None
    )
    created = msg_info.messages[0].date if first_msg_valid else None
    former_title = (
        msg_info.messages[0].action.title
        if first_msg_valid
        and isinstance(msg_info.messages[0].action, MessageActionChannelMigrateFrom)
        and msg_info.messages[0].action.title != chat_title
        else None
    )
    try:
        dc_id, location = get_input_location(chat.full_chat.chat_photo)
    except Exception as e:
        dc_id = "Unknown"
        str(e)

    description = chat.full_chat.about
    members = (
        chat.full_chat.participants_count
        if hasattr(chat.full_chat, "participants_count")
        else chat_obj_info.participants_count
    )
    admins = (
        chat.full_chat.admins_count if hasattr(chat.full_chat, "admins_count") else None
    )
    banned_users = (
        chat.full_chat.kicked_count if hasattr(chat.full_chat, "kicked_count") else None
    )
    restrcited_users = (
        chat.full_chat.banned_count if hasattr(chat.full_chat, "banned_count") else None
    )
    members_online = (
        chat.full_chat.online_count if hasattr(chat.full_chat, "online_count") else 0
    )
    group_stickers = (
        chat.full_chat.stickerset.title
        if hasattr(chat.full_chat, "stickerset") and chat.full_chat.stickerset
        else None
    )
    messages_viewable = msg_info.count if msg_info else None
    messages_sent = (
        chat.full_chat.read_inbox_max_id
        if hasattr(chat.full_chat, "read_inbox_max_id")
        else None
    )
    messages_sent_alt = (
        chat.full_chat.read_outbox_max_id
        if hasattr(chat.full_chat, "read_outbox_max_id")
        else None
    )
    exp_count = chat.full_chat.pts if hasattr(chat.full_chat, "pts") else None
    username = chat_obj_info.username if hasattr(chat_obj_info, "username") else None
    bots_list = chat.full_chat.bot_info  # this is a list
    bots = 0
    supergroup = (
        "<b>Yes</b>"
        if hasattr(chat_obj_info, "megagroup") and chat_obj_info.megagroup
        else "No"
    )
    slowmode = (
        "<b>Yes</b>"
        if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled
        else "No"
    )
    slowmode_time = (
        chat.full_chat.slowmode_seconds
        if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled
        else None
    )
    restricted = (
        "<b>Yes</b>"
        if hasattr(chat_obj_info, "restricted") and chat_obj_info.restricted
        else "No"
    )
    verified = (
        "<b>Yes</b>"
        if hasattr(chat_obj_info, "verified") and chat_obj_info.verified
        else "No"
    )
    username = "@{}".format(username) if username else None
    creator_username = "@{}".format(creator_username) if creator_username else None

    if admins is None:
        try:
            participants_admins = await ultroid_bot(
                GetParticipantsRequest(
                    channel=chat.full_chat.id,
                    filter=ChannelParticipantsAdmins(),
                    offset=0,
                    limit=0,
                    hash=0,
                )
            )
            admins = participants_admins.count if participants_admins else None
        except Exception as e:
            print("Exception:", e)
    if bots_list:
        for bot in bots_list:
            bots += 1

    caption = "<b>CHAT INFO:</b>\n"
    caption += f"ID: <code>{chat_obj_info.id}</code>\n"
    if chat_title is not None:
        caption += f"{chat_type} name: {chat_title}\n"
    if former_title is not None:
        caption += f"Former name: {former_title}\n"
    if username is not None:
        caption += f"{chat_type} type: Public\n"
        caption += f"Link: {username}\n"
    else:
        caption += f"{chat_type} type: Private\n"
    if creator_username is not None:
        caption += f"Creator: {creator_username}\n"
    elif creator_valid:
        caption += (
            f'Creator: <a href="tg://user?id={creator_id}">{creator_firstname}</a>\n'
        )
    if created is not None:
        caption += f"Created: <code>{created.date().strftime('%b %d, %Y')} - {created.time()}</code>\n"
    else:
        caption += f"Created: <code>{chat_obj_info.date.date().strftime('%b %d, %Y')} - {chat_obj_info.date.time()}</code> {warn_emoji}\n"
    caption += f"Data Centre ID: {dc_id}\n"
    if exp_count is not None:
        chat_level = int((1 + sqrt(1 + 7 * exp_count / 14)) / 2)
        caption += f"{chat_type} level: <code>{chat_level}</code>\n"
    if messages_viewable is not None:
        caption += f"Viewable messages: <code>{messages_viewable}</code>\n"
    if messages_sent:
        caption += f"Messages sent: <code>{messages_sent}</code>\n"
    elif messages_sent_alt:
        caption += f"Messages sent: <code>{messages_sent_alt}</code> {warn_emoji}\n"
    if members is not None:
        caption += f"Members: <code>{members}</code>\n"
    if admins is not None:
        caption += f"Administrators: <code>{admins}</code>\n"
    if bots_list:
        caption += f"Bots: <code>{bots}</code>\n"
    if members_online:
        caption += f"Currently online: <code>{members_online}</code>\n"
    if restrcited_users is not None:
        caption += f"Restricted users: <code>{restrcited_users}</code>\n"
    if banned_users is not None:
        caption += f"Banned users: <code>{banned_users}</code>\n"
    if group_stickers is not None:
        caption += f'{chat_type} stickers: <a href="t.me/addstickers/{chat.full_chat.stickerset.short_name}">{group_stickers}</a>\n'
    caption += "\n"
    if not broadcast:
        caption += f"Slow mode: {slowmode}"
        if (
            hasattr(chat_obj_info, "slowmode_enabled")
            and chat_obj_info.slowmode_enabled
        ):
            caption += f", <code>{slowmode_time}s</code>\n\n"
        else:
            caption += "\n\n"
    if not broadcast:
        caption += f"Supergroup: {supergroup}\n\n"
    if hasattr(chat_obj_info, "restricted"):
        caption += f"Restricted: {restricted}\n"
        if chat_obj_info.restricted:
            caption += f"> Platform: {chat_obj_info.restriction_reason[0].platform}\n"
            caption += f"> Reason: {chat_obj_info.restriction_reason[0].reason}\n"
            caption += f"> Text: {chat_obj_info.restriction_reason[0].text}\n\n"
        else:
            caption += "\n"
    if hasattr(chat_obj_info, "scam") and chat_obj_info.scam:
        caption += "Scam: <b>Yes</b>\n\n"
    if hasattr(chat_obj_info, "verified"):
        caption += f"Verified by Telegram: {verified}\n\n"
    if description:
        caption += f"Description: \n<code>{description}</code>\n"
    return caption


async def safeinstall(event):
    ok = await eor(event, "`menginstall...`")
    if event.reply_to_msg_id:
        try:
            downloaded_file_name = await ok.client.download_media(
                await event.get_reply_message(), "addons/"
            )
            n = event.text
            q = n[9:]
            if q != "f":
                xx = open(downloaded_file_name, "r")
                yy = xx.read()
                xx.close()
                try:
                    for dan in DANGER:
                        if re.search(dan, yy):
                            os.remove(downloaded_file_name)
                            return await ok.edit(
                                f"**Installation Aborted.**\n**Reason:** Occurance of `{dan}` in `{downloaded_file_name}`.\n\nIf you trust the provider and/or know what you're doing, use `{HNDLR}install f` to force install.",
                            )
                except BaseException:
                    pass
            if "(" not in downloaded_file_name:
                path1 = Path(downloaded_file_name)
                shortname = path1.stem
                load_addons(shortname.replace(".py", ""))
                try:
                    plug = shortname.replace(".py", "")
                    if plug in HELP:
                        output = "**Plugin** - `{}`\n".format(plug)
                        for i in HELP[plug]:
                            output += i
                        output += "\n© @levinachannel"
                        await eod(
                            ok,
                            f"✓ `Sakura - Installed`: `{plug}` ✓\n\n{output}",
                            time=10,
                        )
                    elif plug in CMD_HELP:
                        kk = f"Plugin Name-{plug}\n\n📚 Commands Available-\n\n"
                        kk += str(CMD_HELP[plug])
                        await eod(
                            ok, f"✓ `Sakura - Installed`: `{plug}` ✓\n\n{kk}", time=10
                        )
                    else:
                        try:
                            x = f"Plugin Name-{plug}\n\n📚 Commands Available-\n\n"
                            for d in LIST[plug]:
                                x += HNDLR + d
                                x += "\n"
                            await eod(
                                ok, f"✓ `Sakura - Installed`: `{plug}` ✓\n\n`{x}`"
                            )
                        except BaseException:
                            await eod(
                                ok, f"✓ `Sakura - Installed`: `{plug}` ✓", time=3
                            )
                except Exception as e:
                    await ok.edit(str(e))
            else:
                os.remove(downloaded_file_name)
                await eod(ok, "**ERROR**\nPlugin might have been pre-installed.")
        except Exception as e:
            await eod(ok, "**ERROR\n**" + str(e))
            os.remove(downloaded_file_name)
    else:
        await eod(ok, f"Please use `{HNDLR}install` as reply to a .py file.")


async def allcmds(event):
    x = str(LIST)
    xx = (
        x.replace(",", "\n")
        .replace("[", """\n """)
        .replace("]", "\n\n")
        .replace("':", """ Plugin\n 📚 Commands Available-""")
        .replace("'", "")
        .replace("{", "")
        .replace("}", "")
    )
    t = telegraph.create_page(title="Sakura All Cmds", content=[f"{xx}"])
    w = t["url"]
    await eod(event, f"All Sakura Cmds : [Click Here]({w})", link_preview=False)


def autopicsearch(query):
    query = query.replace(" ", "-")
    link = f"https://unsplash.com/s/photos/{query}"
    extra = requests.get(link)
    res = bs(extra.content, "html.parser", from_encoding="utf-8")
    results = res.find_all("a", "_2Mc8_")
    return results


async def randomchannel(tochat, channel, range1, range2, caption=None):
    do = random.randrange(range1, range2)
    async for x in ultroid_bot.iter_messages(channel, add_offset=do, limit=1):
        try:
            if not caption:
                caption = x.text
            await ultroid_bot.send_message(tochat, caption, file=x.media)
        except BaseException:
            pass


async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err


async def calcc(cmd, event):
    wtf = f"print({cmd})"
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexecc(wtf, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    return evaluation


async def aexecc(code, event):
    exec(f"async def __aexecc(event): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexecc"](event)


def mediainfo(media):
    xx = str((str(media)).split("(", maxsplit=1)[0])
    m = ""
    if xx == "MessageMediaPhoto":
        m = "pic"
    elif xx == "MessageMediaDocument":
        mim = media.document.mime_type
        if mim == "application/x-tgsticker":
            m = "sticker animated"
        elif "image" in mim:
            if mim == "image/webp":
                m = "sticker"
            elif mim == "image/gif":
                m = "gif as doc"
            else:
                m = "pic as doc"
        elif "video" in mim:
            if "DocumentAttributeAnimated" in str(media):
                m = "gif"
            elif "DocumentAttributeVideo" in str(media):
                i = str(media.document.attributes[0])
                if "supports_streaming=True" in i:
                    m = "video"
                m = "video as doc"
            else:
                m = "video"
        elif "audio" in mim:
            m = "audio"
        else:
            m = "document"
    elif xx == "MessageMediaWebPage":
        m = "web"
    return m


def get_random_user_data():
    from faker import Faker

    cc = Faker().credit_card_full().split("\n")
    card = (
        cc[0]
        + "\n"
        + "**CARD_ID:** "
        + cc[2]
        + "\n"
        + f"**{cc[3].split(':')[0]}:**"
        + cc[3].split(":")[1]
    )
    d = requests.get(base_url).json()
    data_ = d["results"][0]
    _g = data_["gender"]
    gender = "🤵🏻‍♂" if _g == "male" else "🤵🏻‍♀"
    name = data_["name"]
    loc = data_["location"]
    dob = data_["dob"]
    msg = """
{} **Name:** {}.{} {}

**Street:** {} {}
**City:** {}
**State:** {}
**Country:** {}
**Postal Code:** {}

**Email:** {}
**Phone:** {}
**Card:** {}

**Birthday:** {}
""".format(
        gender,
        name["title"],
        name["first"],
        name["last"],
        loc["street"]["number"],
        loc["street"]["name"],
        loc["city"],
        loc["state"],
        loc["country"],
        loc["postcode"],
        data_["email"],
        data_["phone"],
        card,
        dob["date"][:10],
    )
    pic = data_["picture"]["large"]
    return msg, pic


# GoGoAnime Scrapper, Base Credits - TG@Madepranav


def airing_eps():
    resp = requests.get("https://gogoanime.ai/").content
    soup = bs(resp, "html.parser")
    anime = soup.find("nav", {"class": "menu_series cron"}).find("ul")
    air = "**Currently airing anime.**\n\n"
    c = 1
    for link in anime.find_all("a"):
        airing_link = link.get("href")
        name = link.get("title")
        link = airing_link.split("/")
        if c == 21:
            break
        air += f"**{c}.** `{name}`\n"
        c += 1
    return air


async def heroku_logs(event):
    xx = await eor(event, "`Processing...`")
    if not (Var.HEROKU_API and Var.HEROKU_APP_NAME):
        return await xx.edit("Please set `HEROKU_APP_NAME` and `HEROKU_API` in vars.")
    try:
        app = (heroku3.from_key(Var.HEROKU_API)).app(Var.HEROKU_APP_NAME)
    except BaseException:
        return await xx.edit(
            "`HEROKU_API` and `HEROKU_APP_NAME` is wrong! Kindly re-check in config vars."
        )
    await xx.edit("`Downloading Logs...`")
    ok = app.get_log()
    with open("sakura-heroku.log", "w") as log:
        log.write(ok)
    await event.client.send_file(
        event.chat_id,
        file="sakura-heroku.log",
        thumb="resources/extras/sakura.jpg",
        caption=f"**Sakura Heroku Logs.**",
    )
    os.remove("sakura-heroku.log")
    await xx.delete()


async def def_logs(ult):
    await ult.client.send_file(
        ult.chat_id,
        file="sakura.log",
        thumb="resources/extras/sakura.jpg",
        caption=f"**Sakura Logs.**",
    )


def get_paste(data):
    try:
        resp = requests.post("https://hastebin.com/documents", data=data).content
        key = loads(resp)["key"]
        return "haste", key
    except BaseException:
        key = (
            requests.post("https://nekobin.com/api/documents", json={"content": data})
            .json()
            .get("result")
            .get("key")
        )
        return "neko", key


def get_all_files(path):
    filelist = []
    for root, dirs, files in os.walk(path):
        for file in files:
            filelist.append(os.path.join(root, file))
    return sorted(filelist)


def get_anime_src_res(search_str):
    query = """
    query ($id: Int,$search: String) {
      Media (id: $id, type: ANIME,search: $search) {
        id
        title {
          romaji
          english
        }
        description (asHtml: false)
        startDate{
            year
          }
          episodes
          chapters
          volumes
          season
          type
          format
          status
          duration
          averageScore
          genres
          bannerImage
      }
    }
    """
    response = (
        requests.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"search": search_str}},
        )
    ).text
    tjson = json.loads(response)
    res = list(tjson.keys())
    if "errors" in res:
        return f"**Error** : `{tjson['errors'][0]['message']}`"
    else:
        tjson = tjson["data"]["Media"]
        if "bannerImage" in tjson.keys():
            banner = tjson["bannerImage"]
        else:
            banner = None
        title = tjson["title"]["romaji"]
        year = tjson["startDate"]["year"]
        episodes = tjson["episodes"]
        link = f"https://anilist.co/anime/{tjson['id']}"
        ltitle = f"[{title}]({link})"
        info = f"**Type**: {tjson['format']}"
        info += f"\n**Genres**: "
        for g in tjson["genres"]:
            info += g + " "
        info += f"\n**Status**: {tjson['status']}"
        info += f"\n**Episodes**: {tjson['episodes']}"
        info += f"\n**Year**: {tjson['startDate']['year']}"
        info += f"\n**Score**: {tjson['averageScore']}"
        info += f"\n**Duration**: {tjson['duration']} min\n"
        temp = f"{tjson['description']}"
        info += "__" + (re.sub("<br>", "\n", temp)).strip() + "__"
        return banner, ltitle, year, episodes, info


def get_chatbot_reply(event, message):
    req_link = chatbot_base.format(
        message=message, owner=(event.sender.first_name or "SakuraUser")
    )
    try:
        data = requests.get(req_link)
        if data.status_code == 200:
            return (data.json())["message"]
        else:
            LOGS.info("**ERROR:**\n`API down, report this to `@VeezSupportGroup.")
    except Exception:
        LOGS.info("**ERROR:**`{str(e)}`")
