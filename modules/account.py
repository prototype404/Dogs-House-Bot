from pyrogram import Client
import asyncio
import random
import const


async def check(name):
    async with Client(
        api_hash=const.API_HASH, workdir=const.WORK_DIR, api_id=const.API_ID, name=name
    ) as client:
        me = await client.get_me()

        if const.BONE not in me.first_name:
            await client.update_profile(first_name=f"{me.first_name}{const.BONE}")
            await asyncio.sleep(random.uniform(1, 2))

        return me.id
