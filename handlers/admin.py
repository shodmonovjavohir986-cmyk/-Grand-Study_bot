from telegram import Update, InputFile
from telegram.ext import ContextTypes, ConversationHandler

import database as db
from excel import generate_excel_enrollments, generate_excel_users
from keyboards import (
    admin_main_keyboard, course_manage_keyboard, course_list_keyboard,
    delete_confirm_keyboard, excel_choice_keyboard, broadcast_confirm_keyboard,
)
from config import ADMIN_IDS

# Conversation states (course add)
ADD_NAME, ADD_DESC, ADD_PRICE, ADD_DURATION = range(10, 14)
# Conversation states (course edit)
EDIT_NAME, EDIT_DESC, EDIT_PRICE, EDIT_DURATION = range(20, 24)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ── Admin panel ────────────────────────────────────────
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback yoki /admin buyrug'i orqali ochiladi"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if not is_admin(query.from_user.id):
            await query.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        await query.edit_message_text("⚙️ *Admin Panel*", parse_mode="Markdown", reply_markup=admin_main_keyboard())
    else:
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Ruxsat yo'q!")
            return
        await update.message.reply_text("⚙️ *Admin Panel*", parse_mode="Markdown", reply_markup=admin_main_keyboard())


# ── Statistika ─────────────────────────────────────────
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    total_users, total_courses, total_enrollments, today_users = db.get_stats()
    await query.edit_message_text(
        f"📊 *Statistika*\n\n"
        f"👥 Jami foydalanuvchilar: *{total_users}*\n"
        f"🆕 Bugun ro'yxatdan o'tganlar: *{today_users}*\n"
        f"📚 Kurslar soni: *{total_courses}*\n"
        f"✅ Jami yozilishlar: *{total_enrollments}*",
        parse_mode="Markdown",
        reply_markup=admin_main_keyboard(),
    )


# ── Foydalanuvchilar ───────────────────────────────────
async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    users = db.get_all_users()
    if not users:
        await query.edit_message_text("👥 Ro'yxatdan o'tganlar yo'q.", reply_markup=admin_main_keyboard())
        return
    text = f"👥 *Foydalanuvchilar ({len(users)} ta):*\n\n"
    for i, u in enumerate(users[:30], 1):
        text += f"{i}. {u[2]} — {u[3]}\n"
    if len(users) > 30:
        text += f"\n... va yana {len(users) - 30} ta"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_main_keyboard())


# ── Excel ──────────────────────────────────────────────
async def excel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    courses = db.get_all_courses()
    if not courses:
        await query.answer("Kurslar mavjud emas!", show_alert=True)
        return
    await query.edit_message_text(
        "📥 *Qaysi ma'lumotni yuklab olish?*",
        parse_mode="Markdown",
        reply_markup=excel_choice_keyboard(courses),
    )


async def excel_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    cid = int(query.data.split("_")[2])
    course = db.get_course(cid)
    enrollments = db.get_enrollments_for_course(cid)
    excel_buf = generate_excel_enrollments(course, enrollments)
    await context.bot.send_document(
        query.from_user.id,
        document=InputFile(excel_buf, filename=f"{course['name']}_royxat.xlsx"),
        caption=f"📊 *{course['name']}* — yozilganlar ro'yxati\nJami: {len(enrollments)} ta",
        parse_mode="Markdown",
    )


async def excel_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    users = db.get_all_users()
    excel_buf = generate_excel_users(users)
    await context.bot.send_document(
        query.from_user.id,
        document=InputFile(excel_buf, filename="grand_study_foydalanuvchilar.xlsx"),
        caption=f"👥 Jami foydalanuvchilar: {len(users)} ta",
    )


# ── Kurslarni boshqarish ───────────────────────────────
async def courses_manage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await query.edit_message_text(
        "📚 *Kurslarni boshqarish*",
        parse_mode="Markdown",
        reply_markup=course_manage_keyboard(),
    )


async def list_courses_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    courses = db.get_all_courses()
    if not courses:
        await query.edit_message_text("📚 Kurslar yo'q.", reply_markup=course_manage_keyboard())
        return
    await query.edit_message_text(
        "📚 *Kurslar ro'yxati:*\nTahrirlash yoki o'chirish uchun bosing.",
        parse_mode="Markdown",
        reply_markup=course_list_keyboard(courses),
    )


# Kurs o'chirish
async def delete_course_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    cid = int(query.data.split("_")[2])
    course = db.get_course(cid)
    await query.edit_message_text(
        f"⚠️ *{course['name']}* kursini o'chirishni tasdiqlaysizmi?",
        parse_mode="Markdown",
        reply_markup=delete_confirm_keyboard(cid),
    )


async def delete_course_do(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    cid = int(query.data.split("_")[2])
    db.delete_course(cid)
    await query.edit_message_text("✅ Kurs o'chirildi.", reply_markup=course_manage_keyboard())


# ── Kurs qo'shish (ConversationHandler) ───────────────
async def add_course_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return ConversationHandler.END
    await query.edit_message_text("➕ *Kurs qo'shish*\n\nKurs nomini kiriting:", parse_mode="Markdown")
    return ADD_NAME


async def add_course_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["c_name"] = update.message.text.strip()
    await update.message.reply_text("📝 Kurs tavsifini kiriting:")
    return ADD_DESC


async def add_course_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["c_desc"] = update.message.text.strip()
    await update.message.reply_text("💰 Kurs narxini kiriting (masalan: 500,000 so'm):")
    return ADD_PRICE


async def add_course_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["c_price"] = update.message.text.strip()
    await update.message.reply_text("⏱ Kurs davomiyligini kiriting (masalan: 3 oy):")
    return ADD_DURATION


async def add_course_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.add_course(
        context.user_data["c_name"],
        context.user_data["c_desc"],
        context.user_data["c_price"],
        update.message.text.strip(),
    )
    await update.message.reply_text(
        f"✅ *{context.user_data['c_name']}* kursi qo'shildi!",
        parse_mode="Markdown",
        reply_markup=course_manage_keyboard(),
    )
    return ConversationHandler.END


# ── Kurs tahrirlash (ConversationHandler) ─────────────
async def edit_course_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return ConversationHandler.END
    cid = int(query.data.split("_")[2])
    course = db.get_course(cid)
    context.user_data["edit_id"] = cid
    context.user_data["edit"] = dict(course)
    await query.edit_message_text(
        f"✏️ *{course['name']}* kursini tahrirlash\n\n"
        f"Yangi nomni kiriting (o'zgartirmaslik uchun /skip yozing):",
        parse_mode="Markdown",
    )
    return EDIT_NAME


async def edit_course_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() != "/skip":
        context.user_data["edit"]["name"] = update.message.text.strip()
    await update.message.reply_text("📝 Yangi tavsifni kiriting (o'zgartirmaslik: /skip):")
    return EDIT_DESC


async def edit_course_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() != "/skip":
        context.user_data["edit"]["description"] = update.message.text.strip()
    await update.message.reply_text("💰 Yangi narxni kiriting (o'zgartirmaslik: /skip):")
    return EDIT_PRICE


async def edit_course_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() != "/skip":
        context.user_data["edit"]["price"] = update.message.text.strip()
    await update.message.reply_text("⏱ Yangi davomiylikni kiriting (o'zgartirmaslik: /skip):")
    return EDIT_DURATION


async def edit_course_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ec = context.user_data["edit"]
    if update.message.text.strip() != "/skip":
        ec["duration"] = update.message.text.strip()
    db.update_course(context.user_data["edit_id"], ec["name"], ec["description"], ec["price"], ec["duration"])
    await update.message.reply_text(
        f"✅ *{ec['name']}* kursi yangilandi!",
        parse_mode="Markdown",
        reply_markup=course_manage_keyboard(),
    )
    return ConversationHandler.END


# ── Xabar yuborish (broadcast) ─────────────────────────
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    context.user_data["awaiting_broadcast"] = True
    await query.edit_message_text(
        "📣 *Xabar yuborish*\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni yuboring.\n"
        "📎 Fayl, 🎥 Video yoki 🖼 Rasm ham yuborishingiz mumkin!\n\n"
        "❌ Bekor qilish: /cancel",
        parse_mode="Markdown",
    )


async def broadcast_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_broadcast"):
        return
    if not is_admin(update.effective_user.id):
        return

    context.user_data.pop("awaiting_broadcast", None)
    msg = update.message
    context.user_data["bcast"] = {
        "text":     msg.text or msg.caption or "",
        "photo":    msg.photo[-1].file_id if msg.photo else None,
        "video":    msg.video.file_id if msg.video else None,
        "document": msg.document.file_id if msg.document else None,
    }
    users = db.get_all_users()
    await update.message.reply_text(
        f"📣 *Xabar ko'rinishi:*\n\n{context.user_data['bcast']['text']}\n\n"
        f"Jami *{len(users)}* ta foydalanuvchiga yuboriladi. Tasdiqlaysizmi?",
        parse_mode="Markdown",
        reply_markup=broadcast_confirm_keyboard(len(users)),
    )


async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    bm = context.user_data.get("bcast", {})
    users = db.get_all_users()
    sent = failed = 0

    for u in users:
        tid = u[1]
        try:
            if bm.get("photo"):
                await context.bot.send_photo(tid, photo=bm["photo"], caption=bm["text"])
            elif bm.get("video"):
                await context.bot.send_video(tid, video=bm["video"], caption=bm["text"])
            elif bm.get("document"):
                await context.bot.send_document(tid, document=bm["document"], caption=bm["text"])
            else:
                await context.bot.send_message(tid, bm["text"])
            sent += 1
        except Exception:
            failed += 1

    await query.edit_message_text(
        f"✅ *Xabar yuborildi!*\n\n✔️ Muvaffaqiyatli: {sent}\n❌ Xato: {failed}",
        parse_mode="Markdown",
        reply_markup=admin_main_keyboard(),
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Bekor qilindi.",
        reply_markup=admin_main_keyboard(),
    )
    return ConversationHandler.END
