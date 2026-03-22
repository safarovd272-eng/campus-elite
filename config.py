import os
from dotenv import load_dotenv
load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "8731746159:AAFB9EDKmxgQaKUaRP9yiDj7jJKjzuYPusQ")

# Admin Telegram ID lari (vergul bilan ajrating)
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "7378071060")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip()]

# Ma'lumotlar bazasi
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///campus_elite.db")

# Admin kanali ID (submissions uchun xabarlar ketadi)
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", "0"))

# Fakultetlar ro'yxati
FACULTIES = [
    "💻 Iqtisodiyot va axborot texnologiyalari fakulteti",
    "📚 Pedagogika va Ijtimoiy gumanitar fanlar fakulteti",
    "🏥 Tibbiyot fakulteti",
]

# Kurslar
COURSES = ["1-kurs", "2-kurs", "3-kurs", "4-kurs", "5-kurs"]

# Faoliyat turlari va balllar
ACTIVITIES = {
    "event_participation": {
        "name": "🎪 Tadbirda ishtirok etish",
        "points": 2,
        "description": "Universitet yoki tashqi tadbirlarda ishtirok",
        "max_per_semester": None,
    },
    "article_oak": {
        "name": "📰 Maqola nashr etish (OAK jurnal)",
        "points": 3,
        "description": "Ilmiy yoki ommabop maqola nashr etish",
        "max_per_semester": 5,
    },
    "article_local": {
        "name": "📰 Maqola nashr etish (mahalliy jurnal)",
        "points": 2,
        "description": "Ilmiy yoki ommabop maqola nashr etish",
        "max_per_semester": 5,
    },
    "national_conference": {
        "name": "🎓 Milliy konferensiya",
        "points": 1,
        "description": "Milliy darajadagi konferensiyada ishtirok",
        "max_per_semester": 3,
    },
    "international_publication": {
        "name": "🌍 Xalqaro nashr",
        "points": 2,
        "description": "Xalqaro jurnalda nashr yoki konferensiya",
        "max_per_semester": 2,
    },
    "volunteering": {
        "name": "🤝 Volontyorlik (1 kun)",
        "points": 10,
        "description": "Ijtimoiy foydali ishlarda ko'ngillilik",
        "max_per_semester": 10,
    },
    "dgu_certificate": {
        "name": "📜 DGU guvohnoma",
        "points": 3,
        "description": "DGU tomonidan berilgan guvohnoma",
        "max_per_semester": None,
    },
    "newspaper_article": {
        "name": "🗞️ Gazetaga maqola",
        "points": 1,
        "description": "Gazetada maqola chop etish",
        "max_per_semester": None,
    },
}

# Nishon chegaralari
BADGE_THRESHOLDS = {
    "bronze": {"min": 50, "name": "🥉 Bronze Active", "emoji": "🥉"},
    "silver": {"min": 150, "name": "🥈 Silver Leader", "emoji": "🥈"},
    "gold": {"min": 300, "name": "🥇 Gold Elite", "emoji": "🥇"},
}
