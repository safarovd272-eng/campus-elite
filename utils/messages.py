from config import ACTIVITIES, BADGE_THRESHOLDS


def welcome_message() -> str:
    return (
        "🎓 *Assalomu alaykum!*\n\n"
        "🏆 *🎓 Stipendiat Ball Tracker* — 🎓 Stipendiat Ball Tracker botiga xush kelibsiz!\n\n"
        "Bu bot orqali siz:\n"
        "✅ Faoliyatingiz uchun ball to'plasiz\n"
        "📊 Reytingdagi o'rningizni ko'rasiz\n"
        "🏅 Nishonlarga ega bo'lasiz\n"
        "🏆 *\"STIPENDIAT\"* unvoniga erishasiz!\n\n"
        "Boshlash uchun ro'yxatdan o'ting 👇"
    )


def already_registered(user_name: str) -> str:
    return (
        f"👋 Xush kelibsiz, *{user_name}*!\n\n"
        "Siz allaqachon ro'yxatdan o'tgansiz.\n"
        "Quyidagi menyu orqali davom eting 👇"
    )


def registration_start() -> str:
    return (
        "📝 *Ro'yxatdan O'tish*\n\n"
        "Iltimos, to'liq ism-sharifingizni kiriting:\n"
        "_(Masalan: Abdullayev Jasur Baxtiyor o'g'li)_"
    )


def registration_faculty() -> str:
    return "🏫 Fakultetingizni tanlang:"


def registration_course() -> str:
    return "📚 Kursingizni tanlang:"


def registration_student_id() -> str:
    return (
        "🪪 Talaba ID raqamingizni kiriting:\n"
        "_(Masalan: AT-2022-0145)_"
    )


def registration_student_id_exists() -> str:
    return (
        "⚠️ Bu talaba ID allaqachon ro'yxatdan o'tgan!\n"
        "Iltimos, to'g'ri ID kiriting yoki admin bilan bog'laning."
    )


def registration_phone() -> str:
    return (
        "📱 Telefon raqamingizni ulashing yoki qo'lda kiriting:\n"
        "_(Masalan: +998901234567)_"
    )


def registration_success(user) -> str:
    return (
        f"🎉 *Tabriklaymiz, {user.full_name}!*\n\n"
        "✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
        f"👤 Ism: {user.full_name}\n"
        f"🏫 Fakultet: {user.faculty}\n"
        f"📚 Kurs: {user.course_year}\n"
        f"🪪 Student ID: {user.student_id}\n\n"
        "Endi faoliyatlaringiz uchun ball to'plasangiz bo'ladi! 🚀\n"
        "Quyidagi menyudan foydalaning 👇"
    )


def dashboard_message(user, rank: int, history: list) -> str:
    badge_text = "—"
    if user.badge_level != "none" and user.badge_level in BADGE_THRESHOLDS:
        badge_text = BADGE_THRESHOLDS[user.badge_level]["name"]

    # Keyingi nishon
    next_badge = ""
    for badge_code, info in sorted(BADGE_THRESHOLDS.items(), key=lambda x: x[1]["min"]):
        if user.total_points < info["min"]:
            needed = info["min"] - user.total_points
            next_badge = f"\n🎯 Keyingi nishon: {info['name']} uchun *{needed} ball* kerak"
            break

    if user.total_points >= 300:
        next_badge = "\n🏆 Siz eng yuqori nishonga egasiz!"

    # Tarix
    history_text = ""
    if history:
        history_text = "\n\n📋 *Oxirgi faoliyatlar:*\n"
        for log in history[:5]:
            sign = "+" if log.points > 0 else ""
            history_text += f"• {log.reason} — {sign}{log.points} ball\n"
    else:
        history_text = "\n\n_Hali hech qanday faoliyat yo'q_"

    return (
        f"📊 *MENING DASHBOARDIM*\n"
        f"{'━' * 25}\n"
        f"👤 {user.full_name}\n"
        f"🏫 {user.faculty}\n"
        f"📚 {user.course_year} | 🪪 {user.student_id}\n\n"
        f"⭐ *Jami ball: {user.total_points} ball*\n"
        f"📈 Reytingdagi o'rni: *#{rank}*\n"
        f"🏅 Nishon: {badge_text}"
        f"{next_badge}"
        f"{history_text}"
    )


def leaderboard_message(users: list, title: str = "🌐 Umumiy Reyting") -> str:
    if not users:
        return "📊 Hali reyting ma'lumotlari yo'q."

    medals = ["🥇", "🥈", "🥉"]
    text = f"🏆 *CAMPUS ELITE REYTINGI*\n"
    text += f"_{title}_\n"
    text += f"{'━' * 25}\n\n"

    for i, user in enumerate(users):
        medal = medals[i] if i < 3 else f"{i+1}."
        badge = ""
        if user.badge_level != "none" and user.badge_level in BADGE_THRESHOLDS:
            badge = BADGE_THRESHOLDS[user.badge_level]["emoji"] + " "
        text += f"{medal} {badge}{user.full_name}\n"
        text += f"   🏫 {user.faculty} | {user.course_year}\n"
        text += f"   ⭐ *{user.total_points} ball*\n\n"

    return text


def activities_message() -> str:
    text = "🎯 *BALL OLISH MUMKIN BO'LGAN FAOLIYATLAR*\n"
    text += f"{'━' * 25}\n\n"
    for code, info in ACTIVITIES.items():
        text += f"{info['name']}\n"
        text += f"   💰 *+{info['points']} ball*\n"
        text += f"   📝 _{info['description']}_\n"
        if info.get("max_per_semester"):
            text += f"   ⚠️ Semestriga max: {info['max_per_semester']} ta\n"
        text += "\n"
    return text


def submit_start() -> str:
    return (
        "📤 *Dalil Yuborish*\n\n"
        "Qaysi faoliyat uchun dalil yubormoqchisiz?\n"
        "Tanlang 👇"
    )


def submit_proof_request(activity_name: str, points: int) -> str:
    return (
        f"✅ Tanlandi: *{activity_name}* (+{points} ball)\n\n"
        "📎 Endi dalilni yuboring:\n"
        "• 🖼 Rasm (sertifikat, guvohnoma)\n"
        "• 📄 PDF hujjat\n"
        "• 🔗 Havola (link)\n\n"
        "_Admin ko'rib chiqqandan so'ng ball qo'shiladi_"
    )


def submit_description_request() -> str:
    return (
        "📝 Qisqacha izoh yozing:\n"
        "_(Masalan: \"O'zbekiston IT konferensiyasi, 2025-yil 15-yanvar\")_\n\n"
        "_Yoki o'tkazib yuborish uchun /skip yozing_"
    )


def submit_success(activity_name: str) -> str:
    return (
        f"✅ *Ariza qabul qilindi!*\n\n"
        f"📋 Faoliyat: {activity_name}\n\n"
        "⏳ Admin ko'rib chiqib, natija haqida xabar beradi.\n"
        "Odatda 1-2 ish kuni ichida ko'rib chiqiladi.\n\n"
        "🙏 Faolligingiz uchun rahmat!"
    )


def submit_duplicate() -> str:
    return (
        "⚠️ *Bu dalil allaqachon yuborilgan!*\n\n"
        "Bir xil dalilni qayta yuborish mumkin emas.\n"
        "Agar xatolik deb hisoblasangiz, admin bilan bog'laning."
    )


def points_added_notification(user_name: str, points: int, reason: str,
                               total: int, rank: int, new_badge: str = None) -> str:
    text = (
        f"🎉 *Tabriklaymiz, {user_name}!*\n\n"
        f"✅ *+{points} ball* qo'shildi!\n"
        f"📋 Sabab: {reason}\n\n"
        f"⭐ Jami ballingiz: *{total} ball*\n"
        f"📈 Reytingdagi o'rningiz: *#{rank}*"
    )
    if new_badge:
        badge_name = BADGE_THRESHOLDS.get(new_badge, {}).get("name", "")
        text += f"\n\n🏅 *Yangi nishon qo'lga kiritildi: {badge_name}!*"
    return text


def rejection_notification(activity_name: str, reason: str) -> str:
    return (
        f"❌ *Dalil rad etildi*\n\n"
        f"📋 Faoliyat: {activity_name}\n"
        f"📝 Sabab: {reason}\n\n"
        "Iltimos, to'g'ri dalil bilan qayta urinib ko'ring 👇"
    )


def admin_new_submission(user, activity_name: str, sub_id: int,
                          proof_type: str, description: str = None) -> str:
    desc_text = f"\n📝 Izoh: {description}" if description else ""
    return (
        f"🔔 *YANGI ARIZA #{sub_id}*\n"
        f"{'━' * 25}\n"
        f"👤 {user.full_name}\n"
        f"🏫 {user.faculty} | {user.course_year}\n"
        f"🪪 {user.student_id}\n\n"
        f"🎯 Faoliyat: *{activity_name}*\n"
        f"📎 Dalil turi: {proof_type}"
        f"{desc_text}\n\n"
        f"Quyidagi tugmalar orqali qaror qiling 👇"
    )


def weekly_broadcast(top_users: list) -> str:
    text = "🏆 *HAFTALIK REYTING YANGILANDI!*\n"
    text += f"{'━' * 25}\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top_users[:3]):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} {user.full_name} — *{user.total_points} ball*\n"
    if len(top_users) > 3:
        text += f"\n_va yana {len(top_users)-3} ta talaba..._\n"
    text += "\n📊 To'liq reytingni ko'rish uchun:\n/leaderboard"
    return text


def help_message() -> str:
    return (
        "❓ *YORDAM VA QOIDALAR*\n"
        f"{'━' * 25}\n\n"
        "🤖 *Bot buyruqlari:*\n"
        "/start — Bosh sahifa\n"
        "/dashboard — Shaxsiy statistika\n"
        "/leaderboard — Reyting jadvali\n"
        "/submit — Dalil yuborish\n"
        "/activities — Faoliyatlar ro'yxati\n"
        "/help — Yordam\n\n"
        "🏅 *Nishon tizimi:*\n"
        "🥉 Bronze Active — 50+ ball\n"
        "🥈 Silver Leader — 150+ ball\n"
        "🥇 Gold Elite — 300+ ball\n"
        "🏆 Campus Elite — TOP-10\n\n"
        "📞 *Muammolar uchun:*\n"
        "Admin bilan bog'laning yoki /start buyrug'ini bering"
    )
