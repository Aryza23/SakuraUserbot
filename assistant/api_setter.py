# Sakura - UserBot

from . import *


@callback("apiset")
@owner
async def apiset(event):
    await event.edit(
        get_string("ast_1"),
        buttons=[
            [Button.inline("ʀᴇᴍᴏᴠᴇ.ʙɢ ᴀᴘɪ", data="rmbg")],
            [Button.inline("ᴅᴇᴇᴘ ᴀᴘɪ", data="dapi")],
            [Button.inline("ᴏᴄʀ ᴀᴘɪ", data="oapi")],
            [Button.inline("« ʙᴀᴄᴋ", data="setter")],
        ],
    )


@callback("rmbg")
@owner
async def rmbgapi(event):
    await event.delete()
    pru = event.sender_id
    var = "RMBG_API"
    name = "Remove.bg API Key"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(get_string("ast_2"))
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("apiset"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} diatur ke {themssg}",
                buttons=get_back_button("apiset"),
            )


@callback("dapi")
@owner
async def rmbgapi(event):
    await event.delete()
    pru = event.sender_id
    var = "DEEP_API"
    name = "DEEP AI API Key"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("dapatkan deep api mu dari deepai.org dan kirim kesini.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("apiset"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} diatur ke {themssg}",
                buttons=get_back_button("apiset"),
            )


@callback("oapi")
@owner
async def rmbgapi(event):
    await event.delete()
    pru = event.sender_id
    var = "OCR_API"
    name = "OCR API Key"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("dapatkan ocr api dari ocr.space lalu kirim kesini.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "dibatalkan !!",
                buttons=get_back_button("apiset"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} diatur ke {themssg}",
                buttons=get_back_button("apiset"),
            )
