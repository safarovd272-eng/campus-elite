from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.keyboards import main_menu_keyboard
from utils.messages import activities_message, help_message
from database.crud import get_user_by_telegram_id

router = Router()


@router.message(Command("activities"))
@router.message(F.text == "🎯 Qoidalar va Balllar")
async def cmd_activities(message: Message):
    await message.answer(
        activities_message(),
        reply_markup=main_menu_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )


@router.message(Command("help"))
@router.message(F.text == "❓ Yordam")
async def cmd_help(message: Message):
    await message.answer(
        help_message(),
        reply_markup=main_menu_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )


@router.message(Command("register"))
async def cmd_register_redirect(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer("✅ Siz allaqachon ro'yxatdan o'tgansiz!",
                             reply_markup=main_menu_keyboard(message.from_user.id))
    else:
        from handlers.registration import start_registration
        from aiogram.fsm.context import FSMContext
        # Redirect to registration flow
        await message.answer(
            "📝 Ro'yxatdan o'tish uchun quyidagi ma'lumotlarni kiriting.\n"
            "Ism-sharifingizdan boshlang:"
        )
