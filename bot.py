import logging
import asyncio
import handlers
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from config import load_config
from database.methods import Database
from keyboards.keyboards import set_commands


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    config = load_config()
    storage = RedisStorage.from_url(config.redis_url)
    bot = Bot(token=config.token)
    dp = Dispatcher(storage=storage)

    dp.include_router(handlers.commands_router)
    dp.include_router(handlers.add_travel_router)
    dp.include_router(handlers.edit_profile_router)
    dp.include_router(handlers.back_buttons_router)
    dp.include_router(handlers.check_travels_router)
    dp.include_router(handlers.create_profile_router)
    dp.include_router(handlers.travel_check_and_map_router)

    await bot.set_my_commands(set_commands())
    await Database.create_tables()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
