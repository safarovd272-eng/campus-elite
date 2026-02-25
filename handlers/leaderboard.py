from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from database.crud import get_leaderboard, get_user_by_telegram_id, get_user_rank
from keyboards.keyboards import (
    leaderboard_filter_keyboard, faculty_filter_keyboard,
    course_filter_keyboard, main_menu_keyboard
)
from utils.messages import leaderboard_message

router = Router()


@router.message(Command("leaderboard"))
@router.message(F.text == "🏆 Reyting Jadvali")
async def cmd_leaderboard(message: Message):
    users = await get_leaderboard(limit=10)
    user = await get_user_by_telegram_id(message.from_user.id)
    rank = await get_user_rank(message.from_user.id) if user else 0

    text = leaderboard_message(users, "Umumiy TOP-10")
    if user and rank:
        text += f"\n📍 *Sizning o'rningiz: #{rank}* ({user.total_points} ball)"

    await message.answer(
        text,
        reply_markup=leaderboard_filter_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "lb:overall")
async def cb_leaderboard_overall(callback: CallbackQuery):
    users = await get_leaderboard(limit=10)
    text = leaderboard_message(users, "Umumiy TOP-10")
    await callback.message.edit_text(
        text,
        reply_markup=leaderboard_filter_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "lb:faculty")
async def cb_leaderboard_faculty(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏫 Fakultetni tanlang:",
        reply_markup=faculty_filter_keyboard("lbf"),
    )
    await callback.answer()


@router.callback_query(F.data == "lb:course")
async def cb_leaderboard_course(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 Kursni tanlang:",
        reply_markup=course_filter_keyboard("lbc"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lbf:"))
async def cb_leaderboard_by_faculty(callback: CallbackQuery):
    faculty = callback.data.split(":", 1)[1]
    users = await get_leaderboard(limit=10, faculty=faculty)
    text = leaderboard_message(users, f"TOP-10: {faculty}")
    if not users:
        text = f"_{faculty}_ bo'yicha hali talabalar ro'yxatda yo'q."
    await callback.message.edit_text(
        text,
        reply_markup=leaderboard_filter_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lbc:"))
async def cb_leaderboard_by_course(callback: CallbackQuery):
    course = callback.data.split(":", 1)[1]
    users = await get_leaderboard(limit=10, course=course)
    text = leaderboard_message(users, f"TOP-10: {course}")
    if not users:
        text = f"_{course}_ bo'yicha hali talabalar ro'yxatda yo'q."
    await callback.message.edit_text(
        text,
        reply_markup=leaderboard_filter_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
