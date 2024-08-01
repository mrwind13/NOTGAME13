from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import logging
from handlers import start, button, name, domain, links, phone, photo1, photo2, photo3, photo_confirm, NAME, DOMAIN, LINKS, PHONE, PHOTO1, PHOTO2, PHOTO3, PHOTO_CONFIRM

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TOKEN = '7281514687:AAGFfDxSOel1Plo-pcRqYQOzIX6gzJnrd7w'

def main():
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            DOMAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, domain)],
            LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, links)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            PHOTO1: [MessageHandler(filters.PHOTO & ~filters.COMMAND, photo1)],
            PHOTO2: [MessageHandler(filters.PHOTO & ~filters.COMMAND, photo2)],
            PHOTO3: [MessageHandler(filters.PHOTO & ~filters.COMMAND, photo3)],
            PHOTO_CONFIRM: [CallbackQueryHandler(photo_confirm)],
        },
        fallbacks=[CommandHandler('cancel', lambda update, context: update.message.reply_text('Отменено'))]
    )
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()
