import asyncio
import logging
from decouple import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.support import support_router
from handlers.user import user_router
from handlers.task import task_router
from main import dp, bot
from utils.command_menu import set_commands


async def main():
    # scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    # admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    dp.include_routers(support_router, user_router, task_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await set_commands()


if __name__ == '__main__':
    asyncio.run(main())
