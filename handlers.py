import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from PIL import Image, ImageOps
from git import Repo
import io  # Добавляем этот импорт

# Включение логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Определение состояний для ConversationHandler
DOMAIN, NICKNAME, SOCIAL_LINK1, SOCIAL_LINK2, SOCIAL_LINK3, CUSTOM_LINK1, NAME_CUSTOM_LINK1, CUSTOM_LINK2, NAME_CUSTOM_LINK2, PHOTO1, PHOTO2, PHOTO3, PHOTO_CONFIRM = range(13)

ADMINS = ['553334131', '226482111']  # Идентификаторы администраторов

GITHUB_REPO_SSH = "git@github.com:mrwind13/NOTGAME13.git"  # Ваш SSH-репозиторий GitHub
LOCAL_REPO_DIR = "/root/NOTGAME13"  # Локальный путь к вашему репозиторию

USER_FILES_DIR = "/root/NOTGAME13"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Обновление perpages_list.txt при первом запуске
    perpages_list_path = "perpages_list.txt"
    if not os.path.exists(perpages_list_path):
        with open(perpages_list_path, "w") as f:
            for user_file in os.listdir(USER_FILES_DIR):
                if user_file.endswith("_info.txt"):
                    f.write(f"{user_file}\n")
    
    # Сброс пользовательских данных
    context.user_data.clear()
    context.user_data['domain'] = ""
    context.user_data['nickname'] = ""
    context.user_data['social_link1'] = ""
    context.user_data['social_link2'] = ""
    context.user_data['social_link3'] = ""
    context.user_data['custom_link1'] = ""
    context.user_data['name_custom_link1'] = ""
    context.user_data['custom_link2'] = ""
    context.user_data['name_custom_link2'] = ""

    await update.message.reply_text(
        'Привет! 😊 Создай персональную страницу для себя или своего бизнеса:',
        reply_markup=get_keyboard(user_id)
    )
    logger.info(f"Start called by user {user_id}")
    return DOMAIN

def commit_and_push_changes(file_path, commit_message="Update files"):
    repo = Repo(LOCAL_REPO_DIR)
    origin = repo.remotes.origin

    origin.set_url(GITHUB_REPO_SSH)
    repo.git.pull('origin', 'main')
    repo.git.add(file_path)
    repo.index.commit(commit_message)
    origin.push()

    origin.set_url(GITHUB_REPO_SSH)

def save_user_data(user_data):
    domain = user_data.get('domain', 'default')
    file_path = f"{LOCAL_REPO_DIR}/{domain}_info.txt"

    with open(file_path, "w") as file:
        file.write(f"domain = {domain}\n")
        file.write(f"nickname = {user_data.get('nickname', 'Не указано')}\n")
        file.write(f"social_link1 = {user_data.get('social_link1', 'Не указано')}\n")
        file.write(f"social_link2 = {user_data.get('social_link2', 'Не указано')}\n")
        file.write(f"social_link3 = {user_data.get('social_link3', 'Не указано')}\n")
        file.write(f"custom_link1 = {user_data.get('custom_link1', 'Не указано')}\n")
        file.write(f"name_custom_link1 = {user_data.get('name_custom_link1', 'Не указано')}\n")
        file.write(f"custom_link2 = {user_data.get('custom_link2', 'Не указано')}\n")
        file.write(f"name_custom_link2 = {user_data.get('name_custom_link2', 'Не указано')}\n")
        file.write(f"telegram_id = {user_data.get('telegram_id', 'Не указано')}\n")

    commit_and_push_changes(file_path, f"Added info for {domain}")
    return file_path

def get_keyboard(user_id):
    if str(user_id) in ADMINS:
        keyboard = [
            [InlineKeyboardButton("Персональная страница", callback_data='personal')],
            [InlineKeyboardButton("Бизнес страница (скоро)", callback_data='business')],
            [InlineKeyboardButton("Администратор", callback_data='admin')]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("Персональная страница", callback_data='personal')],
            [InlineKeyboardButton("Бизнес страница (скоро)", callback_data='business')]
        ]
    return InlineKeyboardMarkup(keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"Button pressed: {query.data} by user {query.from_user.id}")
    
    if query.data == 'personal':
        await query.message.reply_text("Какой домен ты хочешь использовать? 🌐")
        return DOMAIN
    elif query.data == 'business':
        await query.message.reply_text("Услуга для бизнеса скоро появится, подпишитесь на обновления. 🚀")
        return ConversationHandler.END
    elif query.data == 'admin':
        return await admin_button(update, context)

async def admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"Admin button pressed by {query.from_user.id}")
    
    if str(query.from_user.id) in ADMINS:
        await query.message.reply_text("Введите домен:")
        return DOMAIN
    else:
        await query.message.reply_text("У вас нет прав для доступа к этой функции.")
        return ConversationHandler.END

async def domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domain = update.message.text
    logger.info(f"Domain received: {domain} from user {update.effective_user.id}")
    
    context.user_data['domain'] = domain
    await update.message.reply_text(f"Вы ввели домен: {domain}. Теперь введите nickname:")
    return NICKNAME

async def nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = update.message.text
    logger.info(f"Nickname received: {nickname} from user {update.effective_user.id}")
    
    context.user_data['nickname'] = nickname
    await update.message.reply_text("Введите social_link1:")
    return SOCIAL_LINK1

async def social_link1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['social_link1'] = update.message.text
    await update.message.reply_text("Введите social_link2:")
    return SOCIAL_LINK2

async def social_link2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['social_link2'] = update.message.text
    await update.message.reply_text("Введите social_link3:")
    return SOCIAL_LINK3

async def social_link3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['social_link3'] = update.message.text
    await update.message.reply_text("Введите custom_link1:")
    return CUSTOM_LINK1

async def custom_link1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['custom_link1'] = update.message.text
    await update.message.reply_text("Введите name_custom_link1:")
    return NAME_CUSTOM_LINK1

async def name_custom_link1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name_custom_link1'] = update.message.text
    await update.message.reply_text("Введите custom_link2:")
    return CUSTOM_LINK2

async def custom_link2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['custom_link2'] = update.message.text
    await update.message.reply_text("Введите name_custom_link2:")
    return NAME_CUSTOM_LINK2

async def name_custom_link2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name_custom_link2'] = update.message.text
    await update.message.reply_text("Загрузите первую фотографию. 📷")
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
        await update.message.reply_text(f"Загрузите фотографию {photo_number + 1}. 📸")
        return PHOTO1 + photo_number
    else:
        await update.message.reply_text("Все ли фотографии загружены верно?", reply_markup=get_confirm_keyboard())
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
        file_path = save_user_data(context.user_data)
        for i in range(1, 4):
            photo_path = os.path.join(LOCAL_REPO_DIR, f"{context.user_data['domain']}_{i}.jpg")
            with open(photo_path, 'wb') as file:
                file.write(context.user_data[f'photo{i}'])
            commit_and_push_changes(photo_path, f"Added photo {i} for {context.user_data['domain']}")
        await query.edit_message_text("Все данные сохранены и отправлены в репозиторий.")
    elif query.data == 'confirm_no':
        await query.edit_message_text("Пожалуйста, начните заново и загрузите фотографии ещё раз.")
        return DOMAIN  # Возвращаемся к состоянию для перезапуска

def get_confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton("Да, все в порядке", callback_data='confirm_yes')],
        [InlineKeyboardButton("Нет, загрузить заново", callback_data='confirm_no')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referral_link = f"https://t.me/perpage_bot?start={user_id}"
    keyboard = [
        [InlineKeyboardButton("Скопировать ссылку", url=referral_link)],
        [InlineKeyboardButton("Пригласить друга", switch_inline_query="Приглашаю тебя использовать этот бот!")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=user_id,
        text="Вы можете пригласить других пользователей и получить за это бонусы! Вот ваша реферальная ссылка:",
        reply_markup=reply_markup
    )

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пригласите маму друга и получите бонусы!")
    await send_referral_info(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Сценарий отменен.')
    return ConversationHandler.END
