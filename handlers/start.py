from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.crud import get_user_by_telegram_id
from keyboards.keyboards import main_menu_keyboard
from utils.messages import welcome_message, already_registered

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    if user:
        await message.answer(
            already_registered(user.full_name),
            reply_markup=main_menu_keyboard(message.from_user.id),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            welcome_message(),
            parse_mode="Markdown"
        )
        await message.answer(
            "📝 Ro'yxatdan o'tish uchun /register buyrug'ini bering",
            reply_markup=main_menu_keyboard(message.from_user.id)
        )
