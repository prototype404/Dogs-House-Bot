import asyncio
import random
import const


actions = {
    "subscribe": {"dogs": "dogs_community", "notcoin": "notcoin", "blum": "blumcrypto"}
}


async def get_referrals(bot):
    responce = await bot.session.get(
        const.FRENS_API_URL.format(bot.telegram_id, bot.reference)
    )
    responce = await responce.json()
    count = 0

    for fren in responce["frens"]:
        if fren["reward"] != 0:
            count += 1

    return count


async def get_tasks(bot):
    responce = await bot.session.get(
        const.TASKS_API_URL.format(bot.telegram_id, bot.reference)
    )
    return await responce.json()


async def verify_task(bot, slug):
    url = const.TASKS_API_URL.format(bot.telegram_id, bot.reference)
    url = f"/verify?task={slug}&".join(url.split("?"))

    if "subscribe" in slug:
        tag = slug.split("-")[1]

        if "subscribe" in actions and tag in actions["subscribe"]:
            await bot.client.connect()
            await bot.client.join_chat(actions["subscribe"][tag])
            await bot.client.disconnect()
            await asyncio.sleep(random.uniform(1, 2))

    responce = await bot.session.post(url)
    responce = await responce.json()

    return responce.get("success")
