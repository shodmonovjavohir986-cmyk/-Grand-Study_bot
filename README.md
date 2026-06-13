# 🎓 Grand Study — Telegram Bot

## Fayl tuzilmasi

```
grand_study_bot/
├── main.py              ← Botni ishga tushirish + handlerlarni ulash
├── config.py            ← Barcha sozlamalar (token, admin ID, raqam...)
├── database.py          ← SQLite: foydalanuvchilar, kurslar, yozilishlar
├── keyboards.py         ← Barcha inline klaviaturalar
├── excel.py             ← Excel fayl generatorlari
├── requirements.txt     ← Python kutubxonalar
└── handlers/
    ├── user.py          ← Foydalanuvchi handlerlari (start, kurslar, profil...)
    └── admin.py         ← Admin handlerlari (statistika, broadcast, CRUD...)
```

---

## O'rnatish

```bash
pip install -r requirements.txt
```

## Sozlash — `config.py`

```python
BOT_TOKEN      = "YOUR_BOT_TOKEN_HERE"           # @BotFather dan oling
ADMIN_IDS      = [123456789]                     # Sizning Telegram ID ingiz
YANDEX_MAP_LINK = "https://yandex.uz/maps/..."   # Yandex xarita havolasi
PHONE_NUMBER   = "+998901234567"                 # Markaz telefoni
REFERRAL_BONUS = 10000                           # Referal bonus (so'm)
```

> Telegram ID bilish: @userinfobot ga `/start` yuboring

## Ishga tushirish

```bash
python main.py
```

---

## Funksiyalar

### Foydalanuvchi:
| Tugma | Vazifa |
|-------|--------|
| 📚 Kurslar | Kurslar ro'yxati + tafsilotlar |
| 📝 Kursga yozilish | Ro'yxatga yozilish |
| 📞 Bog'lanish | Yandex xarita + Telefon |
| ℹ️ Ma'lumot | O'quv markaz haqida |
| 👤 Profilim | Shaxsiy ma'lumotlar + kurslar |
| 🎁 Referal | Havola olish + bonus |

### Admin (`/admin`):
| Tugma | Vazifa |
|-------|--------|
| 👥 Ro'yxatdan o'tganlar | Foydalanuvchilar |
| 📊 Statistika | Umumiy ko'rsatkichlar |
| 📥 Excel yuklash | Kurs yoki barcha foydalanuvchilar |
| 📚 Kurslarni boshqarish | Qo'shish / Tahrirlash / O'chirish |
| 📣 Xabar yuborish | Matn + Rasm + Video + Fayl |
