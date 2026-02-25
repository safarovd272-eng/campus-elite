from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database.crud import (
    get_user_by_telegram_id, create_submission, get_submission_by_id
)
from keyboards.keyboards import activity_keyboard, main_menu_keyboard, cancel_keyboard
from utils.messages import (
    submit_start, submit_proof_request, submit_description_request,
    submit_success, submit_duplicate, admin_new_submission
)
from config import ACTIVITIES, ADMIN_IDS, ADMIN_CHANNEL_ID
from keyboards.keyboards import submission_admin_keyboard

router = Router()


class SubmitStates(StatesGroup):
    choosing_activity = State()
    waiting_proof = State()
    waiting_description = State()


@router.message(Command("submit"))
@router.message(F.text == "📤 Dalil Yuborish")
async def cmd_submit(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("⚠️ Avval ro'yxatdan o'ting: /register")
        return

    await state.set_state(SubmitStates.choosing_activity)
    await state.update_data(user_db_id=user.id)
    await message.answer(
        submit_start(),
        reply_markup=activity_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(SubmitStates.choosing_activity, F.data.startswith("activity:"))
async def process_activity_choice(callback: CallbackQuery, state: FSMContext):
    activity_code = callback.data.split(":", 1)[1]
    activity = ACTIVITIES.get(activity_code)
    if not activity:
        await callback.answer("Noto'g'ri tanlov!", show_alert=True)
        return

    await state.update_data(activity_code=activity_code)
    await state.set_state(SubmitStates.waiting_proof)

    await callback.message.edit_text(
        submit_proof_request(activity["name"], activity["points"]),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(SubmitStates.waiting_proof)
async def process_proof(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.",
                             reply_markup=main_menu_keyboard(message.from_user.id))
        return

    proof_type = None
    proof_data = None

    if message.photo:
        proof_type = "📷 Rasm"
        proof_data = message.photo[-1].file_id
    elif message.document:
        proof_type = "📄 Hujjat"
        proof_data = message.document.file_id
    elif message.text and (message.text.startswith("http://") or message.text.startswith("https://")):
        proof_type = "🔗 Havola"
        proof_data = message.text.strip()
    else:
        await message.answer(
            "⚠️ Iltimos, rasm, PDF hujjat yoki havola (link) yuboring."
        )
        return

    await state.update_data(proof_type=proof_type, proof_data=proof_data)
    await state.set_state(SubmitStates.waiting_description)
    await message.answer(
        submit_description_request(),
        parse_mode="Markdown"
    )


@router.message(SubmitStates.waiting_description)
async def process_description(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.",
                             reply_markup=main_menu_keyboard(message.from_user.id))
        return

    description = None if (message.text and message.text.strip() == "/skip") else (
        message.text.strip() if message.text else None
    )

    data = await state.get_data()
    await state.clear()

    # Submission yaratish
    sub = await create_submission(
        user_id=data["user_db_id"],
        activity_code=data["activity_code"],
        proof_type=data["proof_type"],
        proof_data=data["proof_data"],
        proof_description=description,
    )

    if sub is None:
        await message.answer(
            submit_duplicate(),
            reply_markup=main_menu_keyboard(message.from_user.id),
            parse_mode="Markdown"
        )
        return

    activity = ACTIVITIES[data["activity_code"]]
    await message.answer(
        submit_success(activity["name"]),
        reply_markup=main_menu_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )

    # Admin(lar)ga xabar yuborish
    user = await get_user_by_telegram_id(message.from_user.id)
    admin_text = admin_new_submission(
        user=user,
        activity_name=activity["name"],
        sub_id=sub.id,
        proof_type=data["proof_type"],
        description=description,
    )
    admin_kb = submission_admin_keyboard(sub.id)

    # Dalilni adminga forward qilish
    target_ids = [ADMIN_CHANNEL_ID] if ADMIN_CHANNEL_ID else ADMIN_IDS

    for admin_id in target_ids:
        if not admin_id:
            continue
        try:
            # Avval dalilni yubor
            if data["proof_type"] == "📷 Rasm":
                await bot.send_photo(admin_id, photo=data["proof_data"],
                                     caption=admin_text, reply_markup=admin_kb,
                                     parse_mode="Markdown")
            elif data["proof_type"] == "📄 Hujjat":
                await bot.send_document(admin_id, document=data["proof_data"],
                                        caption=admin_text, reply_markup=admin_kb,
                                        parse_mode="Markdown")
            else:
                await bot.send_message(admin_id, admin_text,
                                       reply_markup=admin_kb, parse_mode="Markdown")
        except Exception as e:
            print(f"Admin {admin_id} ga xabar yuborishda xato: {e}")
