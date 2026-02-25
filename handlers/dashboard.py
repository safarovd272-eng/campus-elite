from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from database.crud import get_user_by_telegram_id, get_user_rank, get_points_history
from keyboards.keyboards import main_menu_keyboard
from utils.messages import dashboard_message

router = Router()


async def require_registered(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(
            "⚠️ Siz hali ro'yxatdan o'tmagansiz!\n"
            "Ro'yxatdan o'tish uchun /register buyrug'ini bering."
        )
        return None
    return user


@router.message(Command("dashboard"))
@router.message(F.text == "📊 Mening Dashboardim")
async def cmd_dashboard(message: Message):
    user = await require_registered(message)
    if not user:
        return

    rank = await get_user_rank(message.from_user.id)
    history = await get_points_history(user.id, limit=5)

    await message.answer(
        dashboard_message(user, rank, history),
        reply_markup=main_menu_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )
