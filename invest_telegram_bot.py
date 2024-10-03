import asyncio, nest_asyncio
import logging, aioschedule, traceback
from aiogram import Bot, Dispatcher, types
from app.handlers import router

from threading import Thread

from invest_api.start_invest import start_invest

from config import TOKEN_TELEGRAM

import time

nest_asyncio.apply()

bot = Bot(token=TOKEN_TELEGRAM)
dp = Dispatcher()



async def ping():
    try:
        print("cледование стратегиям началось ")
        await start_invest()
    except Exception:
        print(traceback.format_exc())


async def scheduler():
    try:
        await ping()
    except Exception:
        print(traceback.format_exc())
        time.sleep(10)
        await ping()


async def on_startup():
    try:
        await asyncio.create_task(scheduler())
    except Exception:
        print(traceback.format_exc())
        time.sleep(10)
        await asyncio.create_task(scheduler())


def start_startup():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(on_startup())


async def main():
    dp.include_router(router)
    Thread(target=start_startup, daemon=True).start()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
