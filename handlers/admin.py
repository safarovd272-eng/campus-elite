from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database.crud import (
    get_pending_submissions, get_submission_by_id,
    approve_submission, reject_submission,
    get_stats, get_all_users, add_points,
    get_user_by_telegram_id, get_user_rank, get_user_by_id
)
from keyboards.keyboards import admin_panel_keyboard, submission_admin_keyboard, main_menu_keyboard
from utils.messages import points_added_notification, rejection_notification
from config import ADMIN_IDS, ACTIVITIES

router = Router()


def is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS


def admin_only(func):
    async def wrapper(message_or_cb, *args, **kwargs):
        uid = (message_or_cb.from_user.id
               if hasattr(message_or_cb, 'from_user') else None)
        if not uid or not is_admin(uid):
            if hasattr(message_or_cb, 'answer'):
                await message_or_cb.answer("⛔ Sizda admin huquqlari yo'q.")
            return
        return await func(message_or_cb, *args, **kwargs)
    return wrapper


class AdminStates(StatesGroup):
    waiting_reject_reason = State()
    waiting_addpoints_user = State()
    waiting_addpoints_amount = State()
    waiting_addpoints_reason = State()
    waiting_broadcast_text = State()
    waiting_user_message = State()    # Talaba → Admin
    waiting_admin_reply = State()     # Admin → Talaba


# ===== ADMIN PANEL =====

@router.message(F.text == "⚙️ Admin Panel")
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Sizda admin huquqlari yo'q.")
        return
    await message.answer("⚙️ *Admin Panel*", reply_markup=admin_panel_keyboard(),
                         parse_mode="Markdown")


# ===== PENDING SUBMISSIONS =====

@router.callback_query(F.data == "admin:pending")
async def cb_admin_pending(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return

    submissions = await get_pending_submissions()
    if not submissions:
        await callback.message.edit_text(
            "✅ Hozircha ko'rib chiqilmagan arizalar yo'q!",
            reply_markup=admin_panel_keyboard()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📋 *Kutayotgan arizalar: {len(submissions)} ta*\n"
        "Har bir ariza alohida ko'rsatiladi 👇",
        parse_mode="Markdown",
        reply_markup=admin_panel_keyboard()
    )
    await callback.answer()

    # Har bir submission ko'rsatiladi
    for sub in submissions[:5]:  # Max 5 ta
        activity = ACTIVITIES.get(sub.activity_code, {})
        activity_name = activity.get("name", sub.activity_code)
        points = activity.get("points", 0)
        desc = f"\n📝 Izoh: {sub.proof_description}" if sub.proof_description else ""

        text = (
            f"🔔 *Ariza #{sub.id}*\n"
            f"👤 {sub.user.full_name}\n"
            f"🏫 {sub.user.faculty}\n"
            f"🎯 {activity_name} (+{points} ball)\n"
            f"📎 Dalil: {sub.proof_type}"
            f"{desc}\n"
            f"📅 {sub.submitted_at.strftime('%d.%m.%Y %H:%M')}"
        )
        kb = submission_admin_keyboard(sub.id)

        try:
            if sub.proof_type == "📷 Rasm":
                await callback.message.answer_photo(sub.proof_data, caption=text,
                                                    reply_markup=kb, parse_mode="Markdown")
            elif sub.proof_type == "📄 Hujjat":
                await callback.message.answer_document(sub.proof_data, caption=text,
                                                       reply_markup=kb, parse_mode="Markdown")
            else:
                await callback.message.answer(
                    text + f"\n🔗 {sub.proof_data}", reply_markup=kb, parse_mode="Markdown"
                )
        except Exception as e:
            await callback.message.answer(
                text + f"\n⚠️ Dalil yuklanmadi: {e}", reply_markup=kb, parse_mode="Markdown"
            )


# ===== APPROVE =====

@router.callback_query(F.data.startswith("approve:"))
async def cb_approve(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return

    sub_id = int(callback.data.split(":")[1])
    sub = await approve_submission(sub_id, callback.from_user.id)

    if not sub:
        await callback.answer("⚠️ Ariza topilmadi yoki allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"✅ Ariza #{sub_id} tasdiqlandi! +{sub.points_awarded} ball qo'shildi."
    )
    await callback.answer("✅ Tasdiqlandi!")

    # Talabaga bildirishnoma
    user = await get_user_by_id(sub.user_id)
    if user:
        rank = await get_user_rank(user.telegram_id)
        activity_name = ACTIVITIES.get(sub.activity_code, {}).get("name", sub.activity_code)

        from database.crud import check_and_update_badge
        new_badge = await check_and_update_badge(user.id, user.total_points)

        try:
            await bot.send_message(
                user.telegram_id,
                points_added_notification(
                    user_name=user.full_name,
                    points=sub.points_awarded,
                    reason=activity_name,
                    total=user.total_points,
                    rank=rank,
                    new_badge=new_badge,
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Talabaga bildirishnoma yuborishda xato: {e}")


# ===== REJECT =====

@router.callback_query(F.data.startswith("reject:"))
async def cb_reject_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return

    sub_id = int(callback.data.split(":")[1])
    await state.set_state(AdminStates.waiting_reject_reason)
    await state.update_data(sub_id=sub_id)
    await callback.message.answer(
        f"❌ Ariza #{sub_id} rad etish sababini yozing:\n"
        "_(Masalan: Sertifikat rasmiy hujjat emas)_",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(AdminStates.waiting_reject_reason)
async def process_reject_reason(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    sub_id = data["sub_id"]
    reason = message.text.strip()
    await state.clear()

    sub = await reject_submission(sub_id, message.from_user.id, reason)
    if not sub:
        await message.answer("⚠️ Ariza topilmadi yoki allaqachon ko'rib chiqilgan!")
        return

    await message.answer(f"✅ Ariza #{sub_id} rad etildi.")

    # Talabaga bildirishnoma
    user = await get_user_by_id(sub.user_id)
    if user:
        activity_name = ACTIVITIES.get(sub.activity_code, {}).get("name", sub.activity_code)
        try:
            await bot.send_message(
                user.telegram_id,
                rejection_notification(activity_name, reason),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Rad etish bildirishnomasida xato: {e}")


# ===== STATS =====

@router.callback_query(F.data == "admin:stats")
async def cb_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return

    stats = await get_stats()
    text = (
        "📊 *TIZIM STATISTIKASI*\n"
        f"{'━' * 25}\n\n"
        f"👥 Jami talabalar: *{stats['total_users']}* ta\n"
        f"📋 Jami arizalar: *{stats['total_submissions']}* ta\n"
        f"⏳ Kutayotgan: *{stats['pending_submissions']}* ta\n"
        f"✅ Tasdiqlangan: *{stats['approved_submissions']}* ta\n"
        f"⭐ Berilgan jami ball: *{stats['total_points_given']}*\n"
    )
    await callback.message.edit_text(text, reply_markup=admin_panel_keyboard(),
                                     parse_mode="Markdown")
    await callback.answer()


# ===== MANUAL POINTS =====

@router.callback_query(F.data == "admin:addpoints")
async def cb_addpoints_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_addpoints_user)
    await callback.message.answer(
        "➕ *Ball qo'shish*\n\nTalabaning Telegram ID yoki Student ID ni kiriting:"
    )
    await callback.answer()


@router.message(AdminStates.waiting_addpoints_user)
async def process_addpoints_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()
    user = None
    try:
        tg_id = int(text)
        user = await get_user_by_telegram_id(tg_id)
    except ValueError:
        from database.db import async_session
        from sqlalchemy import select
        from database.db import User
        async with async_session() as session:
            result = await session.execute(select(User).where(User.student_id == text))
            user = result.scalar_one_or_none()

    if not user:
        await message.answer("⚠️ Talaba topilmadi! ID ni tekshiring.")
        return

    await state.update_data(target_user_id=user.id, target_name=user.full_name)
    await state.set_state(AdminStates.waiting_addpoints_amount)
    await message.answer(
        f"✅ Talaba: *{user.full_name}*\n"
        f"Joriy ball: {user.total_points}\n\n"
        "Qancha ball qo'shish kerak? (raqam kiriting):",
        parse_mode="Markdown"
    )


@router.message(AdminStates.waiting_addpoints_amount)
async def process_addpoints_amount(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        points = int(message.text.strip())
        if points <= 0 or points > 500:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ 1-500 orasida raqam kiriting.")
        return

    await state.update_data(points=points)
    await state.set_state(AdminStates.waiting_addpoints_reason)
    await message.answer("📝 Ball qo'shish sababini yozing:")


@router.message(AdminStates.waiting_addpoints_reason)
async def process_addpoints_reason(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    reason = message.text.strip()
    await state.clear()

    user = await add_points(
        user_id=data["target_user_id"],
        points=data["points"],
        reason=reason,
        source="manual",
        added_by=message.from_user.id,
    )
    await message.answer(
        f"✅ *{data['target_name']}* ga *+{data['points']} ball* qo'shildi!\n"
        f"Yangi jami: {user.total_points} ball",
        parse_mode="Markdown"
    )

    # Talabaga bildirishnoma
    rank = await get_user_rank(user.telegram_id)
    try:
        await bot.send_message(
            user.telegram_id,
            points_added_notification(
                user_name=user.full_name,
                points=data["points"],
                reason=reason,
                total=user.total_points,
                rank=rank,
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Bildirishnomada xato: {e}")


# ===== STUDENTS LIST =====

@router.callback_query(F.data == "admin:students")
async def cb_students(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return

    users = await get_all_users(limit=20)
    text = f"👥 *TALABALAR RO'YXATI* (TOP-20)\n{'━' * 25}\n\n"
    for i, u in enumerate(users, 1):
        text += f"{i}. {u.full_name} — *{u.total_points} ball*\n"
        text += f"   🪪 {u.student_id} | {u.faculty}\n"
    await callback.message.edit_text(text, reply_markup=admin_panel_keyboard(),
                                     parse_mode="Markdown")
    await callback.answer()


# ===== BROADCAST =====

@router.callback_query(F.data == "admin:broadcast")
async def cb_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_broadcast_text)
    await callback.message.answer(
        "📣 *Xabar yuborish*\n\nBarcha talabalarga yuboriladigan xabarni yozing:",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(AdminStates.waiting_broadcast_text)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()
    await state.clear()

    users = await get_all_users(limit=10000)
    sent = 0
    failed = 0
    broadcast_text = f"📣 *E'LON*\n\n{text}\n\n_— Campus Elite Administrator_"

    status_msg = await message.answer(f"⏳ Yuborilmoqda... 0/{len(users)}")

    for user in users:
        try:
            await bot.send_message(user.telegram_id, broadcast_text, parse_mode="Markdown")
            sent += 1
        except Exception:
            failed += 1

        if (sent + failed) % 10 == 0:
            try:
                await status_msg.edit_text(f"⏳ Yuborilmoqda... {sent+failed}/{len(users)}")
            except Exception:
                pass

    await status_msg.edit_text(
        f"✅ Xabar yuborildi!\n"
        f"📨 Muvaffaqiyatli: {sent}\n"
        f"❌ Yuborilmadi: {failed}"
    )


# ===== TALABA → ADMINGA XABAR =====

@router.message(F.text == "📩 Adminga Xabar")
async def cmd_contact_admin(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("⚠️ Avval ro'yxatdan o'ting: /register")
        return

    await state.set_state(AdminStates.waiting_user_message)
    await state.update_data(sender_user_id=user.id, sender_tg_id=message.from_user.id)
    await message.answer(
        "📩 *Adminga Xabar*\n\n"
        "Xabaringizni yozing, admin imkon topishi bilan javob beradi.\n\n"
        "_Bekor qilish uchun /cancel_",
        parse_mode="Markdown"
    )


@router.message(AdminStates.waiting_user_message)
async def process_user_message_to_admin(message: Message, state: FSMContext, bot: Bot):
    if message.text and message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(message.from_user.id))
        return

    data = await state.get_data()
    await state.clear()

    user = await get_user_by_telegram_id(message.from_user.id)
    user_text = message.text or "[media]"

    admin_notification = (
        f"📩 *TALABADAN XABAR*\n"
        f"{'━' * 25}\n"
        f"👤 {user.full_name}\n"
        f"🏫 {user.faculty} | {user.course_year}\n"
        f"🪪 {user.student_id}\n"
        f"🆔 TG ID: `{message.from_user.id}`\n\n"
        f"💬 *Xabar:*\n{user_text}"
    )

    from keyboards.keyboards import reply_to_user_keyboard

    # Barcha adminlarga yuborish
    sent_to_admin = False
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                admin_notification,
                reply_markup=reply_to_user_keyboard(message.from_user.id),
                parse_mode="Markdown"
            )
            sent_to_admin = True
        except Exception as e:
            print(f"Admin {admin_id} ga xabar yuborishda xato: {e}")

    if sent_to_admin:
        await message.answer(
            "✅ *Xabaringiz adminga yetkazildi!*\n\n"
            "Admin imkon topishi bilan javob beradi. 🙏",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(message.from_user.id)
        )
    else:
        await message.answer(
            "⚠️ Xabar yuborishda xatolik yuz berdi. Keyinroq urinib ko'ring.",
            reply_markup=main_menu_keyboard(message.from_user.id)
        )


# ===== ADMIN → TALABAGA JAVOB =====

@router.callback_query(F.data.startswith("reply_user:"))
async def cb_reply_to_user_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return

    target_tg_id = int(callback.data.split(":")[1])
    await state.set_state(AdminStates.waiting_admin_reply)
    await state.update_data(reply_target_tg_id=target_tg_id)

    await callback.message.answer(
        f"✏️ *Javob yozing*\n\n"
        f"Talabaga (ID: `{target_tg_id}`) javob xabarini kiriting:\n\n"
        f"_Bekor qilish uchun /cancel_",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(AdminStates.waiting_admin_reply)
async def process_admin_reply(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    if message.text and message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi.")
        return

    data = await state.get_data()
    target_tg_id = data["reply_target_tg_id"]
    reply_text = message.text or "[media]"
    await state.clear()

    admin_name = message.from_user.full_name or "Admin"
    user_message = (
        f"📬 *Admindan Javob*\n"
        f"{'━' * 25}\n\n"
        f"💬 {reply_text}\n\n"
        f"_— {admin_name}_"
    )

    try:
        await bot.send_message(target_tg_id, user_message, parse_mode="Markdown")
        await message.answer(f"✅ Javob muvaffaqiyatli yuborildi! (ID: {target_tg_id})")
    except Exception as e:
        await message.answer(f"❌ Xabar yuborishda xato: {e}\nTalaba botni bloklagan bo'lishi mumkin.")

