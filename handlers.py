from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from PIL import Image, ImageOps
import io
import os

# Определение состояний для ConversationHandler
NAME, DOMAIN, LINKS, PHONE, PHOTO1, PHOTO2, PHOTO3, PHOTO_CONFIRM = range(8)
LOCAL_REPO_DIR = '/root/NOTGAME13'  # Путь к вашему репозиторию

def commit_and_push_changes(file_path):
    # Команды для коммита и пуша изменений
    os.system(f'cd {LOCAL_REPO_DIR} && git add . && git commit -m "Updated user data and photos" && git push')

def get_keyboard():
    keyboard = [
        [InlineKeyboardButton("Персональная страница", callback_data='personal')],
        [InlineKeyboardButton("Бизнес страница (скоро)", callback_data='business')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Создай персональную страницу для себя или своего бизнеса:',
        reply_markup=get_keyboard()
    )
    return NAME

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'personal':
        await query.message.reply_text("Как тебя зовут? (не более 13 символов)")
        return NAME
    elif query.data == 'business':
        await query.message.reply_text("Услуга для бизнеса скоро появится, подпишитесь на обновления.")
        return ConversationHandler.END

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if len(name) > 13:
        await update.message.reply_text("Имя должно быть не длиннее 13 символов. Попробуй еще раз:")
        return NAME
    context.user_data['name'] = name
    await update.message.reply_text("Какой домен ты хочешь использовать?")
    return DOMAIN

async def domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domain = update.message.text
    if len(domain) < 3 or not domain.isalnum():
        await update.message.reply_text("Домен должен быть не короче 3 символов и содержать только латинские буквы или цифры. Попробуй еще раз:")
        return DOMAIN
    context.user_data['domain'] = domain
    await update.message.reply_text("Введи три ссылки через запятую:")
    return LINKS

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    links = update.message.text.split(',')
    if len(links) != 3:
        await update.message.reply_text("Пожалуйста, отправь ровно три ссылки, разделенные запятой:")
        return LINKS
    context.user_data['links'] = links
    await update.message.reply_text("Хочешь ли ты указать свой номер телефона для прямого звонка? Если нет, напиши 'нет'.")
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if phone.lower() == 'нет':
        phone = None
    context.user_data['phone'] = phone
    await update.message.reply_text("Загрузи первую фотографию.")
    return PHOTO1

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_number):
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    image = Image.open(io.BytesIO(photo_bytes))

    if image.size != (314, 105):
        image = ImageOps.fit(image, (314, 105), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        context.user_data[f'photo{photo_number}'] = buffer.getvalue()
        await update.message.reply_photo(photo=buffer)
    else:
        context.user_data[f'photo{photo_number}'] = photo_bytes

    if photo_number < 3:
        await update.message.reply_text(f"Загрузи фотографию {photo_number + 1}.")
        return PHOTO1 + photo_number
    else:
        await update.message.reply_text("Всё ли тебя устраивает?", reply_markup=get_confirm_keyboard())
        return PHOTO_CONFIRM

async def photo1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await photo(update, context, 1)

async def photo2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await photo(update, context, 2)

async def photo3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await photo(update, context, 3)

async def photo_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'confirm_yes':
        # Сохранение файлов и коммит в репозиторий
        for i in range(1, 4):
            file_path = os.path.join(LOCAL_REPO_DIR, f"{context.user_data['domain']}_{i}.jpg")
            with open(file_path, 'wb') as file:
                file.write(context.user_data[f'photo{i}'])
        commit_and_push_changes(file_path)
        await query.edit_message_text("Все данные сохранены и отправлены в репозиторий.")
    elif query.data == 'confirm_no':
        await query.edit_message_text("Пожалуйста, начни заново и загрузи фотографии ещё раз.")
        return NAME  # или другое состояние для перезапуска

def get_confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton("Да, все в порядке", callback_data='confirm_yes')],
        [InlineKeyboardButton("Нет, загрузить заново", callback_data='confirm_no')]
    ]
    return InlineKeyboardMarkup(keyboard)

def main():
    TOKEN = '7281514687:AAGFfDxSOel1Plo-pcRqYQOzIX6gzJnrd7w'
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
            PHOTO_CONFIRM: [CallbackQueryHandler(photo_confirm)]
        },
        fallbacks=[CommandHandler('cancel', lambda update, context: update.message.reply_text('Отменено'))]
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()