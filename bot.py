import asyncio
import logging

from handlers.support.support import support_router
from handlers.support.util import util_support_router
from handlers.user.user import user_router
from handlers.user.util import util_user_router
from handlers.user.deposit import deposit_router, schedule_transfer_option
from handlers.task import task_router
from db.store import init_db_pool, create_table
from main import dp, bot
from utils.command_menu import set_commands


async def main():
    # scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    # admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    await init_db_pool()
    await create_table()

    dp.include_routers(
        util_support_router,
        support_router,
        util_user_router,
        deposit_router,
        user_router,
        task_router)

    await schedule_transfer_option()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await set_commands()


if __name__ == '__main__':
    asyncio.run(main())
