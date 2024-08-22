from fake_useragent import FakeUserAgent
from bot import DogeHouseBot
from modules import account

import asyncio
import logging
import const
import json
import os


async def main():
    logging.info("Бот запущен!")

    if const.WORK_DIR[:-1] not in os.listdir():
        os.mkdir(const.WORK_DIR)

    sessions_dir = os.listdir(const.WORK_DIR)
    logging.info(f"Найдено {len(sessions_dir)} сессий!")

    if "accounts.json" not in os.listdir():
        with open("accounts.json", "w") as accounts:
            accounts.write("{}")

    accounts = json.load(open("accounts.json"))

    ref_name = None
    ref_code = None
    balance = 0

    for session in sessions_dir:
        if not session.endswith(".session"):
            continue

        session = session.split(".")[0]

        try:
            _id = await account.check(session)
            logging.info(f"Account {session} | id{_id} Deploy!")
        except Exception:
            logging.error(f"Account {session} Destroy!")

            action = input(f"Хотите удалить сессию: {session}? y/n ")

            if action == "y":
                os.remove(f"{const.WORK_DIR}{session}.session")

            continue

        if session not in accounts:
            accounts[session] = {
                "User-Agent": FakeUserAgent(os="android").random(),
                "ref_code": "",
                "referrals": 0,
                "balance": 0,
            }

            if ref_code and not accounts[session]["ref_code"]:
                code = ref_code
            else:
                code = None

            bot = DogeHouseBot(session, accounts[session].copy(), code)
            await bot.login()
            accounts[session] = bot.account

            if code:
                ref_bot = DogeHouseBot(ref_name, accounts[ref_name].copy(), None)
                await ref_bot.login(stat=True)

                if accounts[ref_name]["referrals"] != ref_bot.account["referrals"]:
                    logging.info(f"{session} стал рефералом {ref_name}!")

                accounts[ref_name] = ref_bot.account
                await ref_bot.session.close()

            await bot.logout()

            if (
                not ref_code
                and bot.account["referrals"] < const.REFERRAL_COUNT
                or ref_code
                and accounts[ref_name]["referrals"] >= const.REFERRAL_COUNT
            ):
                ref_code = bot.reference
                ref_name = bot.name

            json.dump(accounts, open("accounts.json", "w"))

            balance += bot.balance

    logging.info(f"Общий капитал фермы: {balance} DOGS!")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)-8s [%(asctime)s]  %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )
    logging.getLogger("pyrogram").setLevel(logging.ERROR)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
