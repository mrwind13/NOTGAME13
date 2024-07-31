from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import os
from PIL import Image

# Состояния разговора
NICKNAME, DOMAIN, PHOTO, LINKS = range(4)

# Путь для сохранения данных
BASE_DIR = '/root/perpage'

# Максимальные размеры фотографий (в пикселях)
MAX_WIDTH = 314
MAX_HEIGHT = 105

def check_write_permissions(directory):
    test_file = os.path.join(directory, 'test_file.txt')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except IOError:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Я помогу тебе создать твою персональную страницу.\n"
        "Сначала выбери себе никнейм (до 13 символов латинскими буквами):"
    )
    return NICKNAME

async def nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nickname = update.message.text
    if len(nickname) > 13 or not nickname.isalnum():
        await update.message.reply_text(
            "Никнейм должен быть латинскими буквами и не длиннее 13 символов. Попробуй снова:"
        )
        return NICKNAME

    context.user_data['nickname'] = nickname
    await update.message.reply_text(
        "Отлично! Теперь выбери доменное имя (латинские буквы и цифры, минимум 3 символа):"
    )
    return DOMAIN

async def domain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    domain = update.message.text
    if len(domain) < 3 or not domain.isalnum():
        await update.message.reply_text(
            "Доменное имя должно содержать латинские буквы и цифры и быть не короче 3 символов. Попробуй снова:"
        )
        return DOMAIN

    # Проверка существования папки с таким именем
    user_dir = os.path.join(BASE_DIR, domain)
    if os.path.exists(user_dir):
        await update.message.reply_text(
            "Такое доменное имя уже занято. Пожалуйста, выбери другое:"
        )
        return DOMAIN

    context.user_data['domain'] = domain
    await update.message.reply_text(
        "Отлично! Теперь мне нужно три фотографии: голова, тело, ноги.\n"
        "Загрузи первую фотографию (голова):\n"
        "⚠️ Важно! Пожалуйста, отправляй фотографию как фото, не как файл! ⚠️"
    )
    context.user_data['photo_index'] = 1  # Начинаем с 1
    return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.photo:
        await update.message.reply_text(
            "⚠️ Важно! Пожалуйста, отправляй фотографию как фото, не как файл! ⚠️\n"
            "Попробуй еще раз:"
        )
        return PHOTO

    photo_file = await update.message.photo[-1].get_file()
    user_data = context.user_data
    photo_index = user_data.get('photo_index', 1)  # Используем индекс, начинающийся с 1

    # Путь для сохранения фотографий
    user_dir = os.path.join(BASE_DIR, user_data['domain'])
    os.makedirs(user_dir, exist_ok=True)
    photo_path = os.path.join(user_dir, f"{photo_index}.jpg")

    # Скачивание файла
    await photo_file.download_to_drive(photo_path)

    # Проверка размера изображения
    try:
        with Image.open(photo_path) as img:
            width, height = img.size
            if width != MAX_WIDTH or height != MAX_HEIGHT:
                os.remove(photo_path)
                await update.message.reply_text(
                    f"Фотография должна быть размером {MAX_WIDTH}x{MAX_HEIGHT} пикселей. Попробуй снова:"
                )
                return PHOTO
    except Exception as e:
        os.remove(photo_path)
        await update.message.reply_text(f"Не удалось обработать фотографию. Попробуй снова. Ошибка: {e}")
        return PHOTO

    # Увеличение индекса
    user_data['photo_index'] = photo_index + 1

    if photo_index == 1:
        await update.message.reply_text("Загрузи вторую фотографию (тело):")
        return PHOTO
    elif photo_index == 2:
        await update.message.reply_text("Загрузи третью фотографию (ноги):")
        return PHOTO
    else:
        await update.message.reply_text(
            "Отлично! Теперь отправь мне три ссылки, которые ты хочешь разместить на своей персональной странице."
        )
        return LINKS

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    links = update.message.text.split()
    if len(links) != 3:
        await update.message.reply_text("Пожалуйста, отправь ровно три ссылки, разделенные пробелами:")
        return LINKS

    context.user_data['links'] = links

    # Сохранение данных о пользователе
    user_data = context.user_data
    user_dir = os.path.join(BASE_DIR, user_data['domain'])
    user_file_path = os.path.join(user_dir, 'user_info.txt')

    with open(user_file_path, 'w') as user_file:
        user_file.write(f"Nickname: {user_data['nickname']}\n")
        user_file.write(f"Domain: {user_data['domain']}\n")
        user_file.write(f"Links: {', '.join(user_data['links'])}\n")
        user_file.write(f"Telegram ID: {update.message.from_user.id}\n")

    await update.message.reply_text(
        "Все данные успешно собраны! Твоя персональная страница скоро будет готова."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отмена операции. Если хочешь начать заново, напиши /start")
    return ConversationHandler.END

def main() -> None:
    # Токен вашего бота
    TOKEN = "7281514687:AAGFfDxSOel1Plo-pcRqYQOzIX6gzJnrd7w"

    # Убедитесь, что базовый каталог существует
    os.makedirs(BASE_DIR, exist_ok=True)

    # Проверка прав на запись в базовый каталог
    if not check_write_permissions(BASE_DIR):
        print(f"Нет прав на запись в каталог {BASE_DIR}. Пожалуйста, проверьте права доступа.")
        return

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nickname)],
            DOMAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, domain)],
            PHOTO: [MessageHandler(filters.PHOTO & ~filters.COMMAND, photo)],
            LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, links)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
