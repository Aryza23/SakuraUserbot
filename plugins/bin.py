# originally writen by levina on github
# copyright (C) 2021 by @levina-lab

"""
📚 Commands Available : bin
• `{i}bin`
   ini adalah plugin bin generator, generate kode bin secara acak.
"""

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from userbot.utils import admin_cmd as danish_00

@bot.on(danish_00(pattern="bin ?(.*)"))
async def _(event):
    if event.fwd_from:
        return 
    
    danish = event.pattern_match.group(1)
    chat = "@Carol5_bot"
    await event.edit("mencari bin untuk anda 😁...")
    async with event.client.conversation(chat) as conv:
          try:     
              response = conv.wait_event(events.NewMessage(incoming=True,from_users=1247032902))
              await event.client.send_message(chat, "/bin {}".format(danish))
              response = await response 
          except YouBlockedUserError: 
              await event.reply("sensei!, tolong unblock @Carol5_bot ")
              return
          if response.text.startswith(" "):
             await event.edit("maaf sensei, ternyata bot nya telah tewas dan tidak berfungsi lagi 😔")
          else: 
             await event.delete()
             await event.client.send_message(event.chat_id, response.message)


@bot.on(danish_00(pattern="vbv ?(.*)"))
async def _(event):
    if event.fwd_from:
        return 
    
    danish = event.pattern_match.group(1)
    chat = "@Carol5_bot"
    await event.edit("menghubungkan...")
    async with event.client.conversation(chat) as conv:
          try:     
              response = conv.wait_event(events.NewMessage(incoming=True,from_users=1247032902))
              await event.client.send_message(chat, "/vbv {}".format(danish))
              response = await response 
          except YouBlockedUserError: 
              await event.reply("sensei!, tolong unblock @Carol5_bot")
              return
          if response.text.startswith(" "):
             await event.edit("maaf sensei, ternyata bot nya telah tewas dan tidak berfungsi lagi 😔")
          else: 
             await event.delete()
             await event.client.send_message(event.chat_id, response.message)

@bot.on(danish_00(pattern="key ?(.*)"))
async def _(event):
    if event.fwd_from:
        return 
    
    danish = event.pattern_match.group(1)
    chat = "@Carol5_bot"
    await event.edit("menghubungkan...")
    async with event.client.conversation(chat) as conv:
          try:     
              response = conv.wait_event(events.NewMessage(incoming=True,from_users=1247032902))
              await event.client.send_message(chat, "/key {}".format(danish))
              response = await response 
          except YouBlockedUserError: 
              await event.reply("sensei!, tolong unblock @Carol5_bot ")
              return
          if response.text.startswith(" "):
             await event.edit("maaf sensei, ternyata bot nya telah tewas dan tidak berfungsi lagi 😔")
          else: 
             await event.delete()
             await event.client.send_message(event.chat_id, response.message)

  
@bot.on(danish_00(pattern="iban ?(.*)"))
async def _(event):
    if event.fwd_from:
        return 
    
    danish = event.pattern_match.group(1)
    chat = "@Carol5_bot"
    await event.edit("menghubungkan...")
    async with event.client.conversation(chat) as conv:
          try:     
              response = conv.wait_event(events.NewMessage(incoming=True,from_users=1247032902))
              await event.client.send_message(chat, "/iban {}".format(danish))
              response = await response 
          except YouBlockedUserError: 
              await event.reply("sensei!, tolong unblock @Carol5_bot ")
              return
          if response.text.startswith(" "):
             await event.edit("maaf sensei, ternyata bot nya telah tewas dan tidak berfungsi lagi 😔")
          else: 
             await event.delete()
             await event.client.send_message(event.chat_id, response.message)
