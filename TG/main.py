import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru_settings import log
import config as cfg

storage = MemoryStorage()
loop = asyncio.get_event_loop()
bot = Bot(cfg.BOT_TOKEN, parse_mode='HTML', disable_web_page_preview=True)
dp = Dispatcher(bot, storage=storage, loop=loop)

if __name__ == '__main__':
    from handlers import dp, on_startup
    log.info('start bot')
    executor.start_polling(dp, on_startup=on_startup)
