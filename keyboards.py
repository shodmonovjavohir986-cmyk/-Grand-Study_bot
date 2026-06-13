from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)
from config import PHONE_NUMBER, YANDEX_MAP_LINK, TG_CHANNEL_LINK, INSTAGRAM_LINK, TG_CHANNEL, INSTAGRAM_NAME


# ════════════════════════════════════════
#  MAJBURIY OBUNA
# ════════════════════════════════════════
def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Telegram kanal",  url=TG_CHANNEL_LINK)],
        [InlineKeyboardButton("📸 Instagram",       url=INSTAGRAM_LINK)],
        [InlineKeyboardButton("✅ Obuna bo'ldim",   callback_data="check_sub")],
    ])


# ════════════════════════════════════════
#  BOSH MENYU  — start bosanda shu chiqadi
#  Ro'yxatdan o'tgan:     6 tugma
#  O'tmagan:              ro'yxatdan o'tish tugmasi boshlanadi
# ════════════════════════════════════════
def main_menu_keyboard(is_registered: bool) -> InlineKeyboardMarkup:
    if is_registered:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📚 Kurslar",         callback_data="courses"),
                InlineKeyboardButton("📝 Ro'yxatdan o'tish", callback_data="enroll"),
            ],
            [
                InlineKeyboardButton("📞 Bog'lanish",      callback_data="contact"),
                InlineKeyboardButton("ℹ️ Ma'lumot",        callback_data="about"),
            ],
            [
                InlineKeyboardButton("👤 Profilim",        callback_data="profile"),
                InlineKeyboardButton("🎁 Referal",         callback_data="referral"),
            ],
        ])
    else:
        # Ro'yxatdan o'tmagan — faqat ro'yxatdan o'tish tugmasi (conversation boshlanadi)
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Ro'yxatdan o'tish", callback_data="register")],
            [
                InlineKeyboardButton("📚 Kurslar",         callback_data="courses"),
                InlineKeyboardButton("ℹ️ Ma'lumot",        callback_data="about"),
            ],
            [InlineKeyboardButton("📞 Bog'lanish",         callback_data="contact")],
        ])


def back_keyboard(back_to: str = "main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"back_{back_to}")]
    ])


# ════════════════════════════════════════
#  KURSLAR
# ════════════════════════════════════════
def courses_keyboard(courses: list) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(f"📖 {c[1]}", callback_data=f"course_{c[0]}")] for c in courses]
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def course_detail_keyboard(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Kursga yozilish", callback_data=f"do_enroll_{course_id}")],
        [InlineKeyboardButton("⬅️ Kurslar",         callback_data="courses")],
    ])


def enroll_courses_keyboard(courses: list) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"📚 {c[1]} — {c[3]}", callback_data=f"do_enroll_{c[0]}")]
        for c in courses
    ]
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def enroll_not_registered_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Ro'yxatdan o'tish", callback_data="register")],
        [InlineKeyboardButton("⬅️ Orqaga",             callback_data="back_main")],
    ])


# ════════════════════════════════════════
#  BOG'LANISH — 2 ta tugma: xarita + telefon
# ════════════════════════════════════════
def contact_keyboard() -> InlineKeyboardMarkup:
    phone_clean = PHONE_NUMBER.replace("+", "").replace(" ", "")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺 Yandex Xarita",    url=YANDEX_MAP_LINK)],
        [InlineKeyboardButton(f"📞 {PHONE_NUMBER}",  url=f"https://t.me/+{phone_clean}")],
        [InlineKeyboardButton("⬅️ Orqaga",           callback_data="back_main")],
    ])


# ════════════════════════════════════════
#  PROFIL — ko'rish + tahrirlash
# ════════════════════════════════════════
def profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Tahrirlash",  callback_data="edit_profile")],
        [InlineKeyboardButton("⬅️ Orqaga",      callback_data="back_main")],
    ])


def edit_profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Ismni o'zgartirish",      callback_data="edit_name")],
        [InlineKeyboardButton("📱 Telefonni o'zgartirish",   callback_data="edit_phone")],
        [InlineKeyboardButton("🎂 Yoshni o'zgartirish",     callback_data="edit_age")],
        [InlineKeyboardButton("⬅️ Profilim",                callback_data="profile")],
    ])


# ════════════════════════════════════════
#  REFERAL
# ════════════════════════════════════════
def referral_keyboard(ref_link: str) -> InlineKeyboardMarkup:
    share_url = f"https://t.me/share/url?url={ref_link}&text=Grand+Study+ga+kiring!"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Do'stlarga yuborish", url=share_url)],
        [InlineKeyboardButton("⬅️ Orqaga",              callback_data="back_main")],
    ])


def register_not_registered_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Ro'yxatdan o'tish", callback_data="register")],
        [InlineKeyboardButton("⬅️ Orqaga",             callback_data="back_main")],
    ])


# ════════════════════════════════════════
#  TELEFON (reply keyboard)
# ════════════════════════════════════════
def phone_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ════════════════════════════════════════
#  ADMIN PANEL
# ════════════════════════════════════════
def admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Ro'yxatdan o'tganlar",  callback_data="adm_users"),
            InlineKeyboardButton("📊 Statistika",             callback_data="adm_stats"),
        ],
        [
            InlineKeyboardButton("📥 Excel yuklash",          callback_data="adm_excel"),
            InlineKeyboardButton("📚 Kurslarni boshqarish",   callback_data="adm_courses"),
        ],
        [InlineKeyboardButton("📣 Xabar yuborish",            callback_data="adm_broadcast")],
        [InlineKeyboardButton("⬅️ Bosh menyu",                callback_data="back_main")],
    ])


def course_manage_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Kurs qo'shish",    callback_data="adm_add_course")],
        [InlineKeyboardButton("📋 Kurslar ro'yxati", callback_data="adm_list_courses")],
        [InlineKeyboardButton("⬅️ Admin panel",      callback_data="admin")],
    ])


def course_list_keyboard(courses: list) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(f"✏️ {c[1]}",  callback_data=f"adm_edit_{c[0]}"),
            InlineKeyboardButton("🗑 O'chirish", callback_data=f"adm_del_{c[0]}"),
        ]
        for c in courses
    ]
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="adm_courses")])
    return InlineKeyboardMarkup(rows)


def delete_confirm_keyboard(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Ha, o'chirish", callback_data=f"confirm_del_{course_id}"),
            InlineKeyboardButton("❌ Bekor",          callback_data="adm_list_courses"),
        ]
    ])


def excel_choice_keyboard(courses: list) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(f"📊 {c[1]}", callback_data=f"excel_course_{c[0]}")] for c in courses]
    rows.append([InlineKeyboardButton("👥 Barcha foydalanuvchilar", callback_data="excel_all_users")])
    rows.append([InlineKeyboardButton("⬅️ Admin panel",             callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def broadcast_confirm_keyboard(count: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ Ha, {count} ta foydalanuvchiga yuborish", callback_data="do_broadcast")],
        [InlineKeyboardButton("❌ Bekor qilish",                              callback_data="admin")],
    ])
