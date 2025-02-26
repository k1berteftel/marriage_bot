import asyncio
import logging
import os
import inspect

from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.schedulers import start_schedulers
from storage.nats_storage import NatsStorage
from utils.nats_connect import connect_to_nats
from database.action_data_class import DataInteraction
from database.build import PostgresBuild
from database.model import Base
from config_data.config import load_config, Config
from handlers.user_handlers import user_router
from handlers.search_handlers import search_router
from handlers.admin_handlers import admin_router
from dialogs import get_dialogs
from middlewares import (BlockMiddleware, TransferObjectsMiddleware, RemindMiddleware,
                         OpMiddleware, ImpressionsMiddleware, SupportMiddleware)


module_path = inspect.getfile(inspect.currentframe())
module_dir = os.path.realpath(os.path.dirname(module_path))


format = '[{asctime}] #{levelname:8} {filename}:' \
         '{lineno} - {name} - {message}'

logging.basicConfig(
    level=logging.DEBUG,
    format=format,
    style='{'
)


logger = logging.getLogger(__name__)

config: Config = load_config()


async def main():
    database = PostgresBuild(config.db.dns)
    #await database.drop_tables(Base)
    #await database.create_tables(Base)
    session = database.session()

    scheduler: AsyncIOScheduler = AsyncIOScheduler()
    scheduler.start()

    #  nc, js = await connect_to_nats(servers=config.nats.servers)
    #  storage: NatsStorage = await NatsStorage(nc=nc, js=js).create_storage()

    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    #await start_schedulers(DataInteraction(session), scheduler, bot)

    dp = Dispatcher()  # storage=storage

    # подключаем роутеры
    dp.include_routers(user_router, search_router, admin_router, *get_dialogs())

    # подключаем middleware
    dp.message.outer_middleware(SupportMiddleware())
    dp.update.outer_middleware(BlockMiddleware())
    dp.update.middleware(TransferObjectsMiddleware())
    dp.update.middleware(RemindMiddleware())
    dp.update.middleware(OpMiddleware())
    dp.update.middleware(ImpressionsMiddleware())

    # запуск
    await bot.delete_webhook(drop_pending_updates=True)
    setup_dialogs(dp)
    logger.info('Bot start polling')

    try:
        await dp.start_polling(bot, _scheduler=scheduler, _session=session)
    except Exception as e:
        logger.exception(e)
    finally:
        #  await nc.close()
        logger.info('Connection closed')


if __name__ == "__main__":
    asyncio.run(main())