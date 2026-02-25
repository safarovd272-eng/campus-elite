# 🏆 Campus Elite – Telegram Bot

**Student Ranking System** — Talabalar faolligini kuzatuvchi Telegram bot

---

## 📋 Imkoniyatlar

| Funksiya | Tavsif |
|----------|--------|
| 📝 Ro'yxatdan o'tish | Ism, fakultet, kurs, talaba ID, telefon |
| 📊 Dashboard | Ballingiz, reytingdagi o'rningiz, tarix, nishonlar |
| 🏆 Leaderboard | TOP-10 (umumiy, fakultet, kurs bo'yicha filtr) |
| 📤 Dalil yuborish | Rasm / PDF / havola → admin tasdiqlaydi |
| 🏅 Nishonlar | Bronze (50+), Silver (150+), Gold (300+), Elite (TOP-10) |
| 🔔 Bildirishnomalar | Ball qo'shilganda + haftalik reyting |
| ⚙️ Admin panel | Tasdiqlash/rad etish, ball qo'shish, statistika, broadcast |

---

## 🚀 O'rnatish

### 1. Fayllarni yuklab oling
```bash
git clone <repository>
cd campus_elite_bot
```

### 2. Virtual muhit yarating
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
# yoki
venv\Scripts\activate           # Windows
```

### 3. Kutubxonalarni o'rnating
```bash
pip install -r requirements.txt
```

### 4. Bot token oling
1. Telegramda **@BotFather** ga yozing
2. `/newbot` buyrug'ini bering
3. Bot uchun nom va username bering
4. Token nusxalang

### 5. .env faylini sozlang
```bash
cp .env.example .env
nano .env  # yoki istalgan matn muharrir
```

`.env` faylini to'ldiring:
```
BOT_TOKEN=sizning_bot_tokeningiz
ADMIN_IDS=sizning_telegram_id_ingiz
```

> 💡 **Telegram ID qanday bilinadi?** [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring

### 6. Botni ishga tushiring
```bash
python bot.py
```

---

## ⚙️ Admin Panel

Admin bo'lish uchun `.env` da `ADMIN_IDS` ga Telegram ID qo'shing.

### Admin imkoniyatlari:
- **📋 Kutayotgan arizalar** — Talabalar yuborgan dalillar
- **✅ Tasdiqlash / ❌ Rad etish** — Inline tugmalar orqali
- **➕ Ball qo'shish** — Qo'lda istalgan talabaga ball qo'shish
- **👥 Barcha talabalar** — Ro'yxat va statistika
- **📣 Xabar yuborish** — Barcha talabalarga broadcast

---

## 🏅 Ball Tizimi

| Faoliyat | Ball |
|----------|------|
| Tadbirda ishtirok | +5 |
| Tadbir tashkilotchisi | +15 |
| Loyiha tashabbus | +25 |
| Maqola nashr | +20 |
| Milliy konferensiya | +30 |
| Xalqaro nashr | +50 |
| Volontyorlik (1 kun) | +10 |
| Startap boshlash | +60 |

---

## 📁 Loyiha Tuzilmasi

```
campus_elite_bot/
├── bot.py                  # Asosiy ishga tushirish
├── config.py               # Barcha sozlamalar
├── requirements.txt
├── .env.example
│
├── database/
│   ├── db.py               # SQLAlchemy modellari
│   └── crud.py             # Ma'lumotlar bazasi amallari
│
├── handlers/
│   ├── start.py            # /start
│   ├── registration.py     # Ro'yxatdan o'tish (FSM)
│   ├── dashboard.py        # Shaxsiy statistika
│   ├── submit.py           # Dalil yuborish (FSM)
│   ├── leaderboard.py      # Reyting jadvali
│   ├── admin.py            # Admin panel
│   └── notifications.py    # Yordam va boshqalar
│
├── keyboards/
│   └── keyboards.py        # Barcha tugmalar
│
├── services/
│   └── scheduler.py        # Haftalik broadcast
│
└── utils/
    └── messages.py         # O'zbek tilidagi xabarlar
```

---

## 🛠 Texnik Stack

- **Python 3.11+**
- **aiogram 3.x** — Telegram Bot framework
- **SQLAlchemy 2.0** — ORM (async)
- **SQLite** — Ma'lumotlar bazasi (boshlash uchun)
- **APScheduler** — Haftalik scheduler
- **python-dotenv** — Sozlamalar

---

## 🌐 Production uchun (VPS)

### PostgreSQL o'tkazish:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/campus_elite
pip install asyncpg
```

### systemd service:
```ini
[Unit]
Description=Campus Elite Bot
After=network.target

[Service]
WorkingDirectory=/path/to/campus_elite_bot
ExecStart=/path/to/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable campus_elite
sudo systemctl start campus_elite
sudo systemctl status campus_elite
```

---

## 💡 Maslahat

- Bot birinchi ishga tushganda SQLite fayl avtomatik yaratiladi
- Admin ID ni noto'g'ri kiritsangiz, hech qanday admin funksiyasi ishlamaydi
- Haftalik leaderboard har dushanba soat 09:00 da avtomatik yuboriladi

---

*Campus Elite Bot — Talabalar Kengashi loyihasi 🎓*
