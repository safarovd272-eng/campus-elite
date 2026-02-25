from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database.crud import get_user_by_telegram_id, create_user, get_student_id_exists
from keyboards.keyboards import (
    faculty_keyboard, course_keyboard, phone_keyboard,
    main_menu_keyboard, cancel_keyboard
)
from utils.messages import (
    registration_start, registration_faculty, registration_course,
    registration_student_id, registration_phone, registration_success,
    registration_student_id_exists
)

router = Router()


class RegistrationStates(StatesGroup):
    waiting_name = State()
    waiting_faculty = State()
    waiting_course = State()
    waiting_student_id = State()
    waiting_phone = State()


@router.message(Command("register"))
@router.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_registration(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            "✅ Siz allaqachon ro'yxatdan o'tgansiz!",
            reply_markup=main_menu_keyboard(message.from_user.id)
        )
        return

    await state.set_state(RegistrationStates.waiting_name)
    await message.answer(
        registration_start(),
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown"
    )


@router.message(RegistrationStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Ro'yxatdan o'tish bekor qilindi.",
                             reply_markup=main_menu_keyboard(message.from_user.id))
        return

    name = message.text.strip()
    if len(name) < 5 or len(name) > 200:
        await message.answer("⚠️ Iltimos, to'liq ism-sharifingizni kiriting (5-200 ta belgi).")
        return

    await state.update_data(full_name=name)
    await state.set_state(RegistrationStates.waiting_faculty)
    await message.answer(
        registration_faculty(),
        reply_markup=faculty_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(RegistrationStates.waiting_faculty, F.data.startswith("faculty:"))
async def process_faculty(callback: CallbackQuery, state: FSMContext):
    faculty = callback.data.split(":", 1)[1]
    await state.update_data(faculty=faculty)
    await state.set_state(RegistrationStates.waiting_course)
    await callback.message.edit_text(
        f"✅ Fakultet: {faculty}\n\n" + registration_course(),
        reply_markup=course_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_course, F.data.startswith("course:"))
async def process_course(callback: CallbackQuery, state: FSMContext):
    course = callback.data.split(":", 1)[1]
    await state.update_data(course_year=course)
    await state.set_state(RegistrationStates.waiting_student_id)
    await callback.message.edit_text(
        f"✅ Kurs: {course}\n\n" + registration_student_id(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(RegistrationStates.waiting_student_id)
async def process_student_id(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Ro'yxatdan o'tish bekor qilindi.",
                             reply_markup=main_menu_keyboard(message.from_user.id))
        return

    student_id = message.text.strip()
    if len(student_id) < 3:
        await message.answer("⚠️ Talaba ID juda qisqa. Iltimos, qayta kiriting.")
        return

    # Duplicate check
    if await get_student_id_exists(student_id):
        await message.answer(
            registration_student_id_exists(),
            parse_mode="Markdown"
        )
        return

    await state.update_data(student_id=student_id)
    await state.set_state(RegistrationStates.waiting_phone)
    await message.answer(
        registration_phone(),
        reply_markup=phone_keyboard(),
        parse_mode="Markdown"
    )


@router.message(RegistrationStates.waiting_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await finish_registration(message, state, phone)


@router.message(RegistrationStates.waiting_phone)
async def process_phone_text(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Ro'yxatdan o'tish bekor qilindi.",
                             reply_markup=main_menu_keyboard(message.from_user.id))
        return

    phone = message.text.strip()
    if not phone.startswith("+") or len(phone) < 10:
        await message.answer("⚠️ Telefon raqamini to'g'ri formatda kiriting: +998901234567")
        return

    await finish_registration(message, state, phone)


async def finish_registration(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()

    user = await create_user(
        telegram_id=message.from_user.id,
        full_name=data["full_name"],
        faculty=data["faculty"],
        course_year=data["course_year"],
        student_id=data["student_id"],
        phone_number=phone,
    )

    await state.clear()
    await message.answer(
        registration_success(user),
        reply_markup=main_menu_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )
