import logging
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler,
)

from config import BOT_TOKEN
from database import init_db
import handlers.user as user_h
import handlers.admin as admin_h

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)


def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # ── Ro'yxatdan o'tish ─────────────────────────────
    reg_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(user_h.register_start, pattern="^register$")],
        states={
            user_h.REGISTER_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.register_name)],
            user_h.REGISTER_AGE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.register_age)],
            user_h.REGISTER_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), user_h.register_phone)],
        },
        fallbacks=[CommandHandler("cancel", user_h.cancel)],
    )

    # ── Profil tahrirlash ──────────────────────────────
    edit_name_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(user_h.edit_name_start, pattern="^edit_name$")],
        states={
            user_h.EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.edit_name_receive)],
        },
        fallbacks=[CommandHandler("cancel", user_h.cancel)],
    )

    edit_phone_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(user_h.edit_phone_start, pattern="^edit_phone$")],
        states={
            user_h.EDIT_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), user_h.edit_phone_receive)],
        },
        fallbacks=[CommandHandler("cancel", user_h.cancel)],
    )

    edit_age_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(user_h.edit_age_start, pattern="^edit_age$")],
        states={
            user_h.EDIT_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.edit_age_receive)],
        },
        fallbacks=[CommandHandler("cancel", user_h.cancel)],
    )

    # ── Kurs qo'shish ──────────────────────────────────
    add_course_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.add_course_start, pattern="^adm_add_course$")],
        states={
            admin_h.ADD_NAME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.add_course_name)],
            admin_h.ADD_DESC:     [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.add_course_desc)],
            admin_h.ADD_PRICE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.add_course_price)],
            admin_h.ADD_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.add_course_duration)],
        },
        fallbacks=[CommandHandler("cancel", admin_h.cancel)],
    )

    # ── Kurs tahrirlash ────────────────────────────────
    edit_course_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.edit_course_start, pattern=r"^adm_edit_\d+$")],
        states={
            admin_h.EDIT_NAME:     [MessageHandler(filters.TEXT, admin_h.edit_course_name)],
            admin_h.EDIT_DESC:     [MessageHandler(filters.TEXT, admin_h.edit_course_desc)],
            admin_h.EDIT_PRICE:    [MessageHandler(filters.TEXT, admin_h.edit_course_price)],
            admin_h.EDIT_DURATION: [MessageHandler(filters.TEXT, admin_h.edit_course_duration)],
        },
        fallbacks=[CommandHandler("cancel", admin_h.cancel)],
    )

    # ── Handlerlar ─────────────────────────────────────
    app.add_handler(CommandHandler("start", user_h.start))
    app.add_handler(CommandHandler("admin", admin_h.admin_panel))

    app.add_handler(reg_conv)
    app.add_handler(edit_name_conv)
    app.add_handler(edit_phone_conv)
    app.add_handler(edit_age_conv)
    app.add_handler(add_course_conv)
    app.add_handler(edit_course_conv)

    # Foydalanuvchi callback lari
    app.add_handler(CallbackQueryHandler(user_h.check_sub_callback,  pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(user_h.back_to_main,        pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(user_h.show_courses,        pattern="^courses$"))
    app.add_handler(CallbackQueryHandler(user_h.show_course_detail,  pattern=r"^course_\d+$"))
    app.add_handler(CallbackQueryHandler(user_h.show_enroll_list,    pattern="^enroll$"))
    app.add_handler(CallbackQueryHandler(user_h.do_enroll,           pattern=r"^do_enroll_\d+$"))
    app.add_handler(CallbackQueryHandler(user_h.show_contact,        pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(user_h.show_about,          pattern="^about$"))
    app.add_handler(CallbackQueryHandler(user_h.show_profile,        pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(user_h.show_referral,       pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(user_h.edit_profile_menu,   pattern="^edit_profile$"))

    # Admin callback lari
    app.add_handler(CallbackQueryHandler(admin_h.admin_panel,           pattern="^admin$"))
    app.add_handler(CallbackQueryHandler(admin_h.show_stats,            pattern="^adm_stats$"))
    app.add_handler(CallbackQueryHandler(admin_h.show_users,            pattern="^adm_users$"))
    app.add_handler(CallbackQueryHandler(admin_h.excel_menu,            pattern="^adm_excel$"))
    app.add_handler(CallbackQueryHandler(admin_h.excel_course,          pattern=r"^excel_course_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_h.excel_all_users,       pattern="^excel_all_users$"))
    app.add_handler(CallbackQueryHandler(admin_h.courses_manage,        pattern="^adm_courses$"))
    app.add_handler(CallbackQueryHandler(admin_h.list_courses_admin,    pattern="^adm_list_courses$"))
    app.add_handler(CallbackQueryHandler(admin_h.delete_course_confirm, pattern=r"^adm_del_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_h.delete_course_do,      pattern=r"^confirm_del_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_h.broadcast_start,       pattern="^adm_broadcast$"))
    app.add_handler(CallbackQueryHandler(admin_h.broadcast_send,        pattern="^do_broadcast$"))

    # Broadcast xabar qabul qilish
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL) & ~filters.COMMAND,
        admin_h.broadcast_receive,
    ))

    print("🚀 Grand Study Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
