import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from database.db import init_db
from handlers import start, registration, dashboard, submit, leaderboard, admin, notifications
from services.scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token="8457415158:AAGSQKefTR1eSGIEv7FYdIjmErLeCJbdsHA")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Init DB
    await init_db()
    logger.info("✅ Ma'lumotlar bazasi tayyor")

    # Register routers
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(dashboard.router)
    dp.include_router(submit.router)
    dp.include_router(leaderboard.router)
    dp.include_router(admin.router)
    dp.include_router(notifications.router)

    # Scheduler (haftalik leaderboard)
    scheduler = AsyncIOScheduler()
    setup_scheduler(scheduler, bot)
    scheduler.start()
    logger.info("✅ Scheduler ishga tushdi")

    logger.info("🚀 Campus Elite bot ishga tushdi!")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
