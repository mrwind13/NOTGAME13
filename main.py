import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import handlers
import referral_handler
import user_list_handler

# Включение логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = '7281514687:AAGFfDxSOel1Plo-pcRqYQOzIX6gzJnrd7w'

def main():
    # Создание экземпляра приложения
    application = Application.builder().token(TOKEN).build()

    # Обработчик сценариев (ConversationHandler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start)],
        states={
            handlers.DOMAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.domain)],
            handlers.NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.nickname)],
            handlers.SOCIAL_LINK1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.social_link1)],
            handlers.SOCIAL_LINK2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.social_link2)],
            handlers.SOCIAL_LINK3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.social_link3)],
            handlers.CUSTOM_LINK1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.custom_link1)],
            handlers.NAME_CUSTOM_LINK1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.name_custom_link1)],
            handlers.CUSTOM_LINK2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.custom_link2)],
            handlers.NAME_CUSTOM_LINK2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.name_custom_link2)],
            handlers.PHOTO1: [MessageHandler(filters.PHOTO & ~filters.COMMAND, handlers.photo1)],
            handlers.PHOTO2: [MessageHandler(filters.PHOTO & ~filters.COMMAND, handlers.photo2)],
            handlers.PHOTO3: [MessageHandler(filters.PHOTO & ~filters.COMMAND, handlers.photo3)],
            handlers.PHOTO_CONFIRM: [CallbackQueryHandler(handlers.photo_confirm)],
        },
        fallbacks=[CommandHandler('cancel', handlers.cancel)],
        per_message=False  # Этот параметр важен, чтобы команды корректно обрабатывались
    )

    # Добавляем обработчики в приложение
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handlers.button))  # Обработка нажатий кнопок
    application.add_handler(CommandHandler('referal', handlers.referral))  # Добавляем команду /referal
    application.add_handler(user_list_handler.get_usrserd_handler())  # Обработчик команды /usrserd
    application.add_handler(user_list_handler.get_pagination_handler())  # Обработчик пагинации

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
