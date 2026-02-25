from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import FACULTIES, COURSES, ACTIVITIES, ADMIN_IDS


def main_menu_keyboard(telegram_id: int = 0) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📊 Mening Dashboardim"),
        KeyboardButton(text="🏆 Reyting Jadvali"),
    )
    builder.row(
        KeyboardButton(text="📤 Dalil Yuborish"),
        KeyboardButton(text="🎯 Qoidalar va Balllar"),
    )
    builder.row(
        KeyboardButton(text="📩 Adminga Xabar"),
        KeyboardButton(text="❓ Yordam"),
    )
    if telegram_id in ADMIN_IDS:
        builder.row(KeyboardButton(text="⚙️ Admin Panel"))
    return builder.as_markup(resize_keyboard=True)


def faculty_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for faculty in FACULTIES:
        builder.button(text=faculty, callback_data=f"faculty:{faculty}")
    builder.adjust(1)
    return builder.as_markup()


def course_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for course in COURSES:
        builder.button(text=course, callback_data=f"course:{course}")
    builder.adjust(2)
    return builder.as_markup()


def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamimni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def activity_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, info in ACTIVITIES.items():
        label = f"{info['name']} (+{info['points']} ball)"
        builder.button(text=label, callback_data=f"activity:{code}")
    builder.adjust(1)
    return builder.as_markup()


def leaderboard_filter_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Umumiy TOP-10", callback_data="lb:overall")
    builder.button(text="🎓 Fakultet bo'yicha", callback_data="lb:faculty")
    builder.button(text="📚 Kurs bo'yicha", callback_data="lb:course")
    builder.adjust(1)
    return builder.as_markup()


def faculty_filter_keyboard(prefix: str = "lbf") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for faculty in FACULTIES:
        builder.button(text=faculty, callback_data=f"{prefix}:{faculty}")
    builder.button(text="🔙 Orqaga", callback_data="lb:overall")
    builder.adjust(1)
    return builder.as_markup()


def course_filter_keyboard(prefix: str = "lbc") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for course in COURSES:
        builder.button(text=course, callback_data=f"{prefix}:{course}")
    builder.button(text="🔙 Orqaga", callback_data="lb:overall")
    builder.adjust(2)
    return builder.as_markup()


def submission_admin_keyboard(sub_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"approve:{sub_id}")
    builder.button(text="❌ Rad etish", callback_data=f"reject:{sub_id}")
    builder.adjust(2)
    return builder.as_markup()


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Kutayotgan arizalar", callback_data="admin:pending")
    builder.button(text="➕ Ball qo'shish", callback_data="admin:addpoints")
    builder.button(text="👥 Barcha talabalar", callback_data="admin:students")
    builder.button(text="📊 Statistika", callback_data="admin:stats")
    builder.button(text="📣 Xabar yuborish", callback_data="admin:broadcast")
    builder.adjust(1)
    return builder.as_markup()


def reply_to_user_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ Javob berish", callback_data=f"reply_user:{telegram_id}")
    return builder.as_markup()



    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
