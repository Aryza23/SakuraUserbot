# originally writen by @levina-lab on github
# copyright (C) 2021 by veez project

"""
📚 Commands Available -
• `{i}pong`
   ketik <handler>pong untuk melihat kecepatan sakura userbot mu.
"""

import asyncio

@ultroid_cmd(pattern="pong")
async def dsb(ult):
	await ult.edit("`pong!....`")
	await asyncio.sleep(0.5)
	await ult.edit("`pong..!..`")
	await asyncio.sleep(0.5)
	await ult.edit("`pong....!`")
	await asyncio.sleep(0.5)
	await ult.edit("`🌸🌸 PONG 🌸🌸\n\n➥ SAKURA AI\n➥ 69.69ms\n➥ SAKURA UBOT BY:`@dlwrml")
	
# By @levina-lab 😁

