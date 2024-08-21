from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
from modules import api

from urllib.parse import unquote
from pyrogram import Client
import aiohttp
import logging
import asyncio
import random
import const


class DogeHouseBot:
    def __init__(self, name, account, ref_code=None):
        self.balance = 0
        self.ref_code = ref_code
        self.account = account
        self.name = name

        self.client = Client(
            api_hash=const.API_HASH,
            workdir=const.WORK_DIR,
            api_id=const.API_ID,
            name=name,
        )

        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False),
            headers={"User-Agent": account["User-Agent"]},
            trust_env=True,
        )

    async def login(self, stat=False):
        await asyncio.sleep(random.uniform(*const.ACCOUNT_TIMEOUT))

        try:
            query = await self.get_web_data()
        except Exception:
            logging.error(f"Can't login from {self.name}!")
            return

        url = const.APP_URL

        if self.ref_code:
            url += f"?invite_hash={self.ref_code}"

        responce = await self.session.post(url, data=query)
        responce = await responce.json()

        self.telegram_id = responce.get("telegram_id")
        self.reference = responce.get("reference")
        self.balance = int(responce.get("balance"))

        referrals = await api.get_referrals(self)

        if not stat:
            await self.start_working()

        self.account["referrals"] = referrals
        self.account["ref_code"] = self.reference
        self.account["balance"] = self.balance

    async def start_working(self):
        tasks = await api.get_tasks(self)

        for task in tasks:
            if (
                task["complete"]
                or task["slug"] in const.BLACK_LIST_TASKS
                and "subscribe" not in task["slug"]
            ):
                continue

            if await api.verify_task(self, task["slug"]):
                logging.info(
                    f"{self.name} выполнил задание {task['slug']} : Награда {task['reward']}"
                )
                self.balance += int(task["reward"])
            else:
                logging.error(f"{self.name} не смог выполнить задание {task['slug']}!")

            await asyncio.sleep(random.uniform(*const.TASK_TIMEOUT))

        logging.info(f"На аккаунте : {self.name} : завершена работа!")

    async def logout(self):
        logging.info(f"Logout from {self.name} | Balance: {self.balance}")
        await self.session.close()

    async def get_web_data(self):
        await self.client.connect()

        peer_name = await self.client.resolve_peer(const.BOT_USERNAME)

        web = await self.client.invoke(
            RequestAppWebView(
                peer=peer_name,
                app=InputBotAppShortName(bot_id=peer_name, short_name="join"),
                start_param=self.ref_code,
                platform="android",
                write_allowed=True,
            )
        )

        await self.client.disconnect()

        query = unquote(
            string=unquote(
                string=web.url.split("tgWebAppData=")[1].split("&tgWebAppVersion")[0]
            )
        )

        return query
