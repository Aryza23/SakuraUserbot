# Sakura - UserBot

from datetime import datetime


@asst_cmd("ping$")
@owner
async def _(event):
    start = datetime.now()
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await asst.send_message(
        event.chat_id,
        f"**⚡️ kecepatan ultra**\n➥ `{ms} milliseconds`",
    )
