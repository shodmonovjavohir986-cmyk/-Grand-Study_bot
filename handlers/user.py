import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import database as db
from keyboards import (
    main_menu_keyboard, back_keyboard, contact_keyboard,
    courses_keyboard, course_detail_keyboard,
    enroll_not_registered_keyboard, enroll_courses_keyboard,
    referral_keyboard, register_not_registered_keyboard,
    phone_request_keyboard, remove_keyboard,
    profile_keyboard, edit_profile_keyboard,
    subscribe_keyboard,
)
from config import (
    ADMIN_IDS, GROUP_ID, PHONE_NUMBER, CENTER_ADDRESS, CENTER_ABOUT,
    REFERRAL_BONUS, GIF_PATH,
    TG_CHANNEL, TG_CHANNEL_LINK, INSTAGRAM_LINK, INSTAGRAM_NAME,
)

# ── Conversation states ────────────────────────────────
REGISTER_NAME, REGISTER_AGE, REGISTER_PHONE = range(3)
EDIT_NAME, EDIT_PHONE, EDIT_AGE = range(10, 13)


# ══════════════════════════════════════════════════════
#  GIF YORDAMCHI
# ══════════════════════════════════════════════════════
async def send_gif(bot, chat_id: int, caption: str, reply_markup):
    """GIF yuboradi. file_id DB da saqlanadi — tezroq ishlaydi."""
    gif_id = db.get_setting("gif_file_id")
    if gif_id:
        msg = await bot.send_animation(
            chat_id=chat_id, animation=gif_id,
            caption=caption, parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    else:
        gif_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), GIF_PATH)
        with open(gif_path, "rb") as f:
            msg = await bot.send_animation(
                chat_id=chat_id, animation=f,
                caption=caption, parse_mode="Markdown",
                reply_markup=reply_markup,
            )
        db.set_setting("gif_file_id", msg.animation.file_id)
    return msg


async def del_and_gif(query, caption: str, reply_markup):
    """Eski xabarni o'chirib GIF yuboradi."""
    try:
        await query.message.delete()
    except Exception:
        pass
    return await send_gif(query.get_bot(), query.message.chat_id, caption, reply_markup)


# ══════════════════════════════════════════════════════
#  OBUNA TEKSHIRISH
# ══════════════════════════════════════════════════════
async def is_subscribed(bot, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(TG_CHANNEL, user_id)
        return m.status not in ("left", "kicked")
    except Exception:
        return True   # kanal topilmasa bloklama


# ══════════════════════════════════════════════════════
#  /start
# ══════════════════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Referal
    if context.args:
        conn = db.get_conn()
        c = conn.cursor()
        c.execute("SELECT telegram_id FROM users WHERE referral_code=?", (context.args[0],))
        row = c.fetchone()
        conn.close()
        if row and row[0] != user.id:
            context.user_data["referred_by"] = row[0]

    # Obuna tekshirish
    if not await is_subscribed(context.bot, user.id):
        await send_gif(
            context.bot, update.effective_chat.id,
            "👋 *Assalomu alaykum!*\n\n"
            "🎓 *Grand Study* rasmiy botiga xush kelibsiz!\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📌 Botdan foydalanish uchun avval\n"
            "quyidagi kanallarimizga obuna bo'ling:\n\n"
            f"📢 Telegram: {TG_CHANNEL}\n"
            f"📸 Instagram: {INSTAGRAM_NAME}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Obuna bo'lgach ✅ tugmani bosing!",
            subscribe_keyboard(),
        )
        return

    db_user = db.get_user(user.id)
    is_reg = db_user is not None

    # Ro'yxatdan o'tmagan bo'lsa — ro'yxatdan o'tish boshlanadi
    if not is_reg:
        await send_gif(
            context.bot, update.effective_chat.id,
            f"👋 Salom, *{user.first_name}*!\n\n"
            "🎓 *Grand Study* o'quv markaziga xush kelibsiz!\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🌟 Biz zamonaviy ta'lim markazi bo'lib,\n"
            "har bir o'quvchiga sifatli bilim va\n"
            "professional rivojlanish imkonini beramiz.\n\n"
            "📚 *Bizda nima bor:*\n"
            "• Malakali va tajribali ustozlar\n"
            "• Amaliy va zamonaviy kurslar\n"
            "• Rasmiy sertifikat\n"
            "• Ish topishda ko'mak\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👇 Boshlash uchun ro'yxatdan o'ting:",
            main_menu_keyboard(False),
        )
    else:
        await send_gif(
            context.bot, update.effective_chat.id,
            f"👋 Qaytib keldingiz, *{db_user['full_name'].split()[0]}*!\n\n"
            "🎓 *Grand Study* botiga xush kelibsiz!\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🌟 Yangi kurslar, bilimlar va imkoniyatlar\n"
            "siz bilan birga! Quyidagi bo'limdan\n"
            "kerakligini tanlang 👇",
            main_menu_keyboard(True),
        )


# ══════════════════════════════════════════════════════
#  OBUNA CALLBACK
# ══════════════════════════════════════════════════════
async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if not await is_subscribed(context.bot, user.id):
        await query.answer(
            f"⚠️ Siz hali {TG_CHANNEL} kanalga obuna bo'lmadingiz!\n"
            "Iltimos, avval obuna bo'ling.",
            show_alert=True,
        )
        return

    db_user = db.get_user(user.id)
    is_reg = db_user is not None

    if not is_reg:
        await del_and_gif(
            query,
            f"✅ *Rahmat, obuna tasdiqlandi!*\n\n"
            f"👋 Salom, *{user.first_name}*!\n\n"
            "🎓 *Grand Study* o'quv markaziga xush kelibsiz!\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📚 Bizda nima bor:\n"
            "• Malakali ustozlar\n"
            "• Amaliy kurslar\n"
            "• Rasmiy sertifikat\n"
            "• Ish topishda ko'mak\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👇 Boshlash uchun ro'yxatdan o'ting:",
            main_menu_keyboard(False),
        )
    else:
        await del_and_gif(
            query,
            f"✅ *Obuna tasdiqlandi!*\n\n"
            f"👋 Qaytib keldingiz, *{db_user['full_name'].split()[0]}*!\n\n"
            "🎓 *Grand Study* bilan birga o'sib boring!\n\n"
            "👇 Kerakli bo'limni tanlang:",
            main_menu_keyboard(True),
        )


# ══════════════════════════════════════════════════════
#  ORQAGA — BOSH MENYU
# ══════════════════════════════════════════════════════
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db_user = db.get_user(query.from_user.id)
    await del_and_gif(
        query,
        "🏠 *Bosh menyu*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎓 *Grand Study* — bilim va muvaffaqiyat markazi!\n\n"
        "👇 Kerakli bo'limni tanlang:",
        main_menu_keyboard(db_user is not None),
    )


# ══════════════════════════════════════════════════════
#  KURSLAR
# ══════════════════════════════════════════════════════
async def show_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    courses = db.get_all_courses()
    if not courses:
        await del_and_gif(
            query,
            "📚 *Kurslar*\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⏳ Hozircha yangi kurslar tayyorlanmoqda.\n"
            "Tez orada qo'shiladi — kuzatib boring!",
            back_keyboard(),
        )
        return

    text = (
        "📚 *Mavjud kurslar*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Har bir kurs amaliy bilim va real tajribaga\n"
        "asoslangan. Batafsil ma'lumot uchun bosing 👇\n\n"
    )
    for c in courses:
        text += f"🔹 *{c[1]}*\n   💰 {c[3]}  |  ⏱ {c[4]}\n\n"

    await del_and_gif(query, text, courses_keyboard(courses))


async def show_course_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = int(query.data.split("_")[1])
    course = db.get_course(cid)
    if not course:
        await query.answer("Kurs topilmadi!", show_alert=True)
        return

    await del_and_gif(
        query,
        f"📚 *{course['name']}*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *Tavsif:*\n{course['description']}\n\n"
        f"💰 *Narxi:* {course['price']}\n"
        f"⏱ *Davomiyligi:* {course['duration']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ Yozilish uchun quyidagi tugmani bosing!\n"
        f"📞 Savol bo'lsa: {PHONE_NUMBER}",
        course_detail_keyboard(cid),
    )


# ══════════════════════════════════════════════════════
#  KURSGA YOZILISH
# ══════════════════════════════════════════════════════
async def show_enroll_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not db.get_user(query.from_user.id):
        await del_and_gif(
            query,
            "⚠️ *Diqqat!*\n\n"
            "Kursga yozilish uchun avval\n"
            "ro'yxatdan o'tishingiz kerak.\n\n"
            "Bu bepul va atigi 1 daqiqa! 😊",
            enroll_not_registered_keyboard(),
        )
        return
    courses = db.get_all_courses()
    if not courses:
        await del_and_gif(query, "⏳ Hozircha kurslar mavjud emas.", back_keyboard())
        return
    await del_and_gif(
        query,
        "📝 *Kursga yozilish*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Quyidagi kurslardan birini tanlang.\n"
        "Yozilgach, mutaxassislarimiz siz bilan\n"
        "tez orada bog'lanishadi 📞\n\n"
        "👇 Kursni tanlang:",
        enroll_courses_keyboard(courses),
    )


async def do_enroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    db_user = db.get_user(user.id)
    cid = int(query.data.split("_")[2])

    if not db_user:
        await del_and_gif(
            query, "⚠️ Avval ro'yxatdan o'ting!",
            enroll_not_registered_keyboard(),
        )
        return

    course = db.get_course(cid)
    success = db.enroll_user(user.id, cid)

    if success:
        await del_and_gif(
            query,
            f"🎉 *Tabriklaymiz!*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Siz *\"{course['name']}\"* kursiga\n"
            f"muvaffaqiyatli yozildingiz!\n\n"
            f"📋 *Keyingi qadam:*\n"
            f"Mutaxassislarimiz siz bilan bog'lanib,\n"
            f"dars jadvali va to'lov haqida\n"
            f"ma'lumot beradi.\n\n"
            f"📞 Shoshilinch: {PHONE_NUMBER}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌟 Grand Study bilan muvaffaqiyat sari!",
            back_keyboard(),
        )
        # Guruhga xabar
        try:
            await context.bot.send_message(
                GROUP_ID,
                f"🆕 *Yangi ro'yxat!*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Ism: *{db_user['full_name']}*\n"
                f"🎂 Yosh: {db_user['age']}\n"
                f"📞 Telefon: {db_user['phone']}\n"
                f"📚 Kurs: *{course['name']}*\n"
                f"💰 Narx: {course['price']}\n"
                f"🔗 Telegram: @{user.username or 'yoq'}\n"
                f"🕐 Vaqt: {db.get_current_time()}",
                parse_mode="Markdown",
            )
        except Exception as e:
            pass
        # Adminlarga ham
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"🆕 *Yangi ro'yxat!*\n"
                    f"👤 {db_user['full_name']}\n"
                    f"🎂 {db_user['age']} yosh\n"
                    f"📞 {db_user['phone']}\n"
                    f"📚 {course['name']}",
                    parse_mode="Markdown",
                )
            except Exception:
                pass
    else:
        await del_and_gif(
            query,
            f"ℹ️ *Ma'lumot*\n\n"
            f"Siz *\"{course['name']}\"* kursiga\n"
            f"avval yozilgansiz!\n\n"
            f"📞 Savol bo'lsa: {PHONE_NUMBER}",
            back_keyboard(),
        )


# ══════════════════════════════════════════════════════
#  BOG'LANISH — xarita + telefon
# ══════════════════════════════════════════════════════
async def show_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await del_and_gif(
        query,
        "📞 *Bog'lanish*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Biz bilan istalgan vaqt bog'laning!\n\n"
        f"📞 *Telefon:* {PHONE_NUMBER}\n"
        f"📍 *Manzil:* {CENTER_ADDRESS}\n\n"
        "🕐 *Ish vaqti:*\n"
        "Dushanba — Shanba: 09:00 — 19:00\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👇 Qulay usulni tanlang:",
        contact_keyboard(),
    )


# ══════════════════════════════════════════════════════
#  MA'LUMOT — markaz haqida + manzil + telefon
# ══════════════════════════════════════════════════════
async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await del_and_gif(
        query,
        "ℹ️ *Grand Study haqida*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{CENTER_ABOUT}\n\n"
        "🏆 *Bizning afzalliklarimiz:*\n"
        "• 👨‍🏫 Malakali va tajribali ustozlar\n"
        "• 📱 Zamonaviy o'quv dasturlari\n"
        "• 🕐 O'quvchiga qulay jadval\n"
        "• 📜 Rasmiy sertifikat\n"
        "• 💼 Ish topishda ko'mak\n"
        "• 🔄 100% amaliy mashg'ulotlar\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Bizning natijalar:*\n"
        "• 500+ muvaffaqiyatli bitiruvchi\n"
        "• 95% ish bilan ta'minlanish\n"
        "• ⭐⭐⭐⭐⭐ o'rtacha baholash\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 *Manzil:* {CENTER_ADDRESS}\n"
        f"📞 *Telefon:* {PHONE_NUMBER}\n"
        f"📢 *Telegram:* {TG_CHANNEL}\n"
        f"📸 *Instagram:* {INSTAGRAM_NAME}",
        back_keyboard(),
    )


# ══════════════════════════════════════════════════════
#  PROFIL — ko'rish + tahrirlash
# ══════════════════════════════════════════════════════
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    db_user = db.get_user(user.id)

    if not db_user:
        await del_and_gif(
            query,
            "👤 *Profil*\n\n"
            "Profil ko'rish uchun avval\n"
            "ro'yxatdan o'ting! 😊",
            register_not_registered_keyboard(),
        )
        return

    enrollments = db.get_enrollments_for_user(user.id)
    ref_count = db.get_referral_count(user.id)

    enroll_text = "\n\n📚 *Yozilgan kurslar:* hali yo'q"
    if enrollments:
        enroll_text = "\n\n📚 *Yozilgan kurslar:*\n"
        for e in enrollments:
            enroll_text += f"  ✅ {e[0]} — {e[1]}\n"

    await del_and_gif(
        query,
        f"👤 *Mening profilim*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism: *{db_user['full_name']}*\n"
        f"🎂 Yosh: *{db_user['age']}*\n"
        f"📞 Telefon: {db_user['phone']}\n"
        f"🗓 Ro'yxat: {db_user['registered_at']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎁 Referal bonus: *{db_user['referral_bonus']:,} so'm*\n"
        f"👥 Taklif qilganlar: *{ref_count} kishi*"
        f"{enroll_text}",
        profile_keyboard(),
    )


async def edit_profile_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await del_and_gif(
        query,
        "✏️ *Profilni tahrirlash*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Qaysi ma'lumotni o'zgartirmoqchisiz?\n"
        "👇 Bosing:",
        edit_profile_keyboard(),
    )


async def edit_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except Exception:
        pass
    await context.bot.send_message(
        query.message.chat_id,
        "👤 *Ismni o'zgartirish*\n\n"
        "Yangi ism va familiyangizni kiriting:\n"
        "_(masalan: Alisher Valiyev)_\n\n"
        "/cancel — bekor qilish",
        parse_mode="Markdown",
    )
    return EDIT_NAME


async def edit_name_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 3:
        await update.message.reply_text("⚠️ Kamida 3 ta harf kiriting:")
        return EDIT_NAME
    db_user = db.get_user(update.effective_user.id)
    db.update_user(update.effective_user.id, name, db_user["phone"], db_user["age"])
    await update.message.reply_text(
        f"✅ Ism o'zgartirildi: *{name}*",
        parse_mode="Markdown",
        reply_markup=edit_profile_keyboard(),
    )
    return ConversationHandler.END


async def edit_phone_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except Exception:
        pass
    await context.bot.send_message(
        query.message.chat_id,
        "📱 *Telefonni o'zgartirish*\n\n"
        "Yangi raqamingizni yuboring 👇\n\n"
        "/cancel — bekor qilish",
        parse_mode="Markdown",
        reply_markup=phone_request_keyboard(),
    )
    return EDIT_PHONE


async def edit_phone_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg.contact:
        await msg.reply_text(
            "⚠️ Tugma orqali yuboring!",
            reply_markup=phone_request_keyboard(),
        )
        return EDIT_PHONE
    phone = msg.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    db_user = db.get_user(update.effective_user.id)
    db.update_user(update.effective_user.id, db_user["full_name"], phone, db_user["age"])
    await msg.reply_text(
        f"✅ Telefon o'zgartirildi: *{phone}*",
        parse_mode="Markdown",
        reply_markup=remove_keyboard(),
    )
    await context.bot.send_message(
        msg.chat_id, "Davom ettiring 👇",
        reply_markup=edit_profile_keyboard(),
    )
    return ConversationHandler.END


async def edit_age_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except Exception:
        pass
    await context.bot.send_message(
        query.message.chat_id,
        "🎂 *Yoshni o'zgartirish*\n\n"
        "Yoshingizni kiriting _(5—60)_:\n\n"
        "/cancel — bekor qilish",
        parse_mode="Markdown",
    )
    return EDIT_AGE


async def edit_age_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("⚠️ Faqat raqam kiriting:")
        return EDIT_AGE
    if age < 5 or age > 60:
        await update.message.reply_text("⚠️ Yosh 5—60 orasida bo'lishi kerak:")
        return EDIT_AGE
    db_user = db.get_user(update.effective_user.id)
    db.update_user(update.effective_user.id, db_user["full_name"], db_user["phone"], age)
    await update.message.reply_text(
        f"✅ Yosh o'zgartirildi: *{age}*",
        parse_mode="Markdown",
        reply_markup=edit_profile_keyboard(),
    )
    return ConversationHandler.END


# ══════════════════════════════════════════════════════
#  REFERAL
# ══════════════════════════════════════════════════════
async def show_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    db_user = db.get_user(user.id)

    if not db_user:
        await del_and_gif(
            query,
            "🎁 *Referal*\n\nAvval ro'yxatdan o'ting!",
            register_not_registered_keyboard(),
        )
        return

    ref_count = db.get_referral_count(user.id)
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={db_user['referral_code']}"

    await del_and_gif(
        query,
        f"🎁 *Referal tizimi*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Do'stlaringizni Grand Study ga taklif qiling!\n"
        f"Har bir do'stingiz uchun *{REFERRAL_BONUS:,} so'm* bonus!\n\n"
        f"🔗 *Sizning havolangiz:*\n`{ref_link}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Taklif qilganlar: *{ref_count} kishi*\n"
        f"💰 Jami bonus: *{db_user['referral_bonus']:,} so'm*",
        referral_keyboard(ref_link),
    )


# ══════════════════════════════════════════════════════
#  RO'YXATDAN O'TISH (ConversationHandler)
# ══════════════════════════════════════════════════════
async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if db.get_user(query.from_user.id):
        await del_and_gif(
            query,
            "✅ Siz allaqachon ro'yxatdan o'tgansiz!\n\n"
            "Profilingizni ko'rish uchun *Profilim* tugmasini bosing.",
            back_keyboard(),
        )
        return ConversationHandler.END
    try:
        await query.message.delete()
    except Exception:
        pass
    await context.bot.send_message(
        query.message.chat_id,
        "📋 *Ro'yxatdan o'tish*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Atigi 3 ta savol — 1 daqiqa! 😊\n\n"
        "👤 *1-qadam:* Ism va familiyangizni kiriting:\n"
        "_(masalan: Alisher Valiyev)_\n\n"
        "/cancel — bekor qilish",
        parse_mode="Markdown",
    )
    return REGISTER_NAME


async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 3:
        await update.message.reply_text(
            "⚠️ Iltimos, to'liq ism va familiyangizni kiriting:"
        )
        return REGISTER_NAME
    context.user_data["reg_name"] = name
    await update.message.reply_text(
        f"✅ Zo'r, *{name.split()[0]}*!\n\n"
        "🎂 *2-qadam:* Yoshingizni kiriting:\n"
        "_(faqat raqam, masalan: 20)_\n\n"
        "📌 Yosh 5 dan 60 gacha bo'lishi kerak.",
        parse_mode="Markdown",
    )
    return REGISTER_AGE


async def register_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("⚠️ Faqat raqam kiriting, masalan: 18")
        return REGISTER_AGE
    if age < 5 or age > 60:
        await update.message.reply_text(
            "⚠️ Yosh *5 dan 60 gacha* bo'lishi kerak. Qayta kiriting:",
            parse_mode="Markdown",
        )
        return REGISTER_AGE
    context.user_data["reg_age"] = age
    await update.message.reply_text(
        "✅ Yaxshi!\n\n"
        "📱 *3-qadam:* Telefon raqamingizni yuboring.\n\n"
        "🔒 Raqamingiz xavfsiz saqlanadi va\n"
        "faqat administrator ko'radi.\n\n"
        "👇 Pastdagi tugmani bosing:",
        parse_mode="Markdown",
        reply_markup=phone_request_keyboard(),
    )
    return REGISTER_PHONE


async def register_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user

    if not msg.contact:
        await msg.reply_text(
            "⚠️ Iltimos, *tugma orqali* yuboring!\n"
            "Qo'lda yozilgan raqam qabul qilinmaydi.",
            parse_mode="Markdown",
            reply_markup=phone_request_keyboard(),
        )
        return REGISTER_PHONE

    phone = msg.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    referred_by = context.user_data.get("referred_by")
    db.create_user(
        user.id,
        context.user_data["reg_name"],
        phone,
        context.user_data["reg_age"],
        user.username,
        referred_by,
    )
    db_user = db.get_user(user.id)
    bonus_text = f"\n🎁 Referal bonus: *{REFERRAL_BONUS:,} so'm* qo'shildi!" if referred_by else ""

    await msg.reply_text("✅ Ro'yxatdan o'tdingiz!", reply_markup=remove_keyboard())
    await send_gif(
        context.bot, msg.chat_id,
        f"🎉 *Tabriklaymiz, {db_user['full_name'].split()[0]}!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Grand Study botida ro'yxatdan o'tdingiz!\n\n"
        f"📋 *Ma'lumotlaringiz:*\n"
        f"👤 Ism: *{db_user['full_name']}*\n"
        f"🎂 Yosh: *{db_user['age']}*\n"
        f"📞 Telefon: {db_user['phone']}"
        f"{bonus_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 Endi kurslarimizni ko'rib chiqing!\n\n"
        f"👇 Kerakli bo'limni tanlang:",
        main_menu_keyboard(True),
    )

    # Guruhga xabar
    try:
        await context.bot.send_message(
            GROUP_ID,
            f"🆕 *Yangi ro'yxatdan o'tdi!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Ism: *{db_user['full_name']}*\n"
            f"🎂 Yosh: {db_user['age']}\n"
            f"📞 Telefon: {db_user['phone']}\n"
            f"🔗 Telegram: @{user.username or 'yoq'}\n"
            f"🕐 Vaqt: {db_user['registered_at']}",
            parse_mode="Markdown",
        )
    except Exception:
        pass

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin_id,
                f"🆕 Yangi foydalanuvchi!\n"
                f"👤 {db_user['full_name']}\n"
                f"🎂 {db_user['age']} yosh\n"
                f"📞 {db_user['phone']}\n"
                f"🔗 @{user.username or 'yoq'}",
            )
        except Exception:
            pass
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    db_user = db.get_user(update.effective_user.id)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=remove_keyboard())
    await send_gif(
        update.get_bot(), update.effective_chat.id,
        "🏠 *Bosh menyu*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎓 *Grand Study* — bilim va muvaffaqiyat!\n\n"
        "👇 Kerakli bo'limni tanlang:",
        main_menu_keyboard(db_user is not None),
    )
    return ConversationHandler.END
