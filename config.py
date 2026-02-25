import os
from dotenv import load_dotenv

load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Admin Telegram ID lari (vergul bilan ajrating)
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "123456789")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip()]

# Ma'lumotlar bazasi
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///campus_elite.db")

# Admin kanali ID (submissions uchun xabarlar ketadi)
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", "0"))

# Fakultetlar ro'yxati
FACULTIES = [
    "💻 Axborot texnologiyalari",
    "📐 Muhandislik",
    "💼 Iqtisodiyot va boshqaruv",
    "⚖️ Huquq",
    "🔬 Tabiiy fanlar",
    "📚 Gumanitar fanlar",
    "🏥 Tibbiyot",
    "🎨 San'at va dizayn",
]

# Kurslar
COURSES = ["1-kurs", "2-kurs", "3-kurs", "4-kurs", "5-kurs (magistr)"]

# Faoliyat turlari va balllar
ACTIVITIES = {
    "event_participation": {
        "name": "🎪 Tadbirda ishtirok etish",
        "points": 5,
        "description": "Universitet yoki tashqi tadbirlarda ishtirok",
        "max_per_semester": None,
    },
    "event_organizer": {
        "name": "🎤 Tadbir tashkilotchisi",
        "points": 15,
        "description": "Tadbirni tashkil etish va boshqarish",
        "max_per_semester": 5,
    },
    "project_initiative": {
        "name": "💡 Loyiha tashabbus",
        "points": 25,
        "description": "Yangi loyiha boshlash va rahbarlik qilish",
        "max_per_semester": 3,
    },
    "article_publication": {
        "name": "📰 Maqola nashr etish",
        "points": 20,
        "description": "Ilmiy yoki ommabop maqola nashr etish",
        "max_per_semester": 5,
    },
    "national_conference": {
        "name": "🎓 Milliy konferensiya",
        "points": 30,
        "description": "Milliy darajadagi konferensiyada ishtirok",
        "max_per_semester": 3,
    },
    "international_publication": {
        "name": "🌍 Xalqaro nashr",
        "points": 50,
        "description": "Xalqaro jurnalda nashr yoki konferensiya",
        "max_per_semester": 2,
    },
    "volunteering": {
        "name": "🤝 Volontyorlik (1 kun)",
        "points": 10,
        "description": "Ijtimoiy foydali ishlarda ko'ngillilik",
        "max_per_semester": 10,
    },
    "startup_launched": {
        "name": "🚀 Startap boshlash",
        "points": 60,
        "description": "Rasmiy ro'yxatdan o'tgan startap/biznes",
        "max_per_semester": 1,
    },
}

# Nishon chegaralari
BADGE_THRESHOLDS = {
    "bronze": {"min": 50, "name": "🥉 Bronze Active", "emoji": "🥉"},
    "silver": {"min": 150, "name": "🥈 Silver Leader", "emoji": "🥈"},
    "gold": {"min": 300, "name": "🥇 Gold Elite", "emoji": "🥇"},
}
