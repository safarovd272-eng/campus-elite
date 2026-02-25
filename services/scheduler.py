from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from database.crud import get_leaderboard, get_all_users
from utils.messages import weekly_broadcast
from config import ADMIN_IDS


def setup_scheduler(scheduler: AsyncIOScheduler, bot: Bot):
    # Har dushanba 09:00 da haftalik reyting
    scheduler.add_job(
        send_weekly_leaderboard,
        trigger="cron",
        day_of_week="mon",
        hour=9,
        minute=0,
        args=[bot],
        id="weekly_leaderboard",
        replace_existing=True,
    )


async def send_weekly_leaderboard(bot: Bot):
    top_users = await get_leaderboard(limit=10)
    if not top_users:
        return

    text = weekly_broadcast(top_users)
    all_users = await get_all_users(limit=10000)

    sent = 0
    for user in all_users:
        try:
            await bot.send_message(user.telegram_id, text, parse_mode="Markdown")
            sent += 1
        except Exception:
            pass

    # Admin ga hisobot
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"📊 Haftalik reyting xabari yuborildi.\n"
                f"✅ Yetkazildi: {sent}/{len(all_users)} ta foydalanuvchi",
            )
        except Exception:
            pass
