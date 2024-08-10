import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

# Путь к директории, где хранятся файлы пользователей
USER_FILES_DIR = "/root/NOTGAME13"
USERS_PER_PAGE = 13  # Максимальное количество пользователей, показываемое в одном сообщении

def read_user_data(domain):
    file_path = f"{USER_FILES_DIR}/{domain}_info.txt"
    user_data = {
        "points": 0,
        "invited": 0,
        "registered_self": 0,
    }
    
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                key, value = line.strip().split(" = ")
                if key in user_data:
                    user_data[key] = int(float(value))
    return user_data

async def usrserd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    ADMINS = ['553334131', '226482111']  # Укажите здесь идентификаторы администраторов
    
    # Проверяем, является ли пользователь администратором
    if user_id not in ADMINS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    # Получаем список всех файлов, соответствующих шаблону "+domain+_info.txt"
    user_files = [f for f in os.listdir(USER_FILES_DIR) if f.endswith('_info.txt')]
    
    if not user_files:
        await update.message.reply_text("Нет зарегистрированных пользователей.")
        return

    # Формируем список пользователей для показа
    user_list = []
    for idx, filename in enumerate(user_files):
        domain = filename.replace('_info.txt', '')
        user_data = read_user_data(domain)
        user_list.append(f"<a href='https://t.me/{domain}'>{idx + 1}. {domain}</a> - {user_data['points']} / {user_data['invited']} / {user_data['registered_self']}")

    # Разбиваем список пользователей на страницы
    pages = [user_list[i:i + USERS_PER_PAGE] for i in range(0, len(user_list), USERS_PER_PAGE)]

    # Текущая страница (первая по умолчанию)
    current_page = 0
    await show_user_page(update, context, pages, current_page)

def create_pagination_keyboard(current_page, total_pages):
    # Создаем кнопки для навигации по страницам
    keyboard = []
    if current_page > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"prev_page_{current_page - 1}"))
    if current_page < total_pages - 1:
        keyboard.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"next_page_{current_page + 1}"))
    return InlineKeyboardMarkup([keyboard])

async def show_user_page(update, context, pages, current_page):
    # Показываем пользователей на текущей странице
    users = "\n".join(pages[current_page])
    total_pages = len(pages)
    reply_markup = create_pagination_keyboard(current_page, total_pages)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(users, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.message.reply_text(users, reply_markup=reply_markup, parse_mode='HTML')

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # Извлекаем номер текущей страницы из callback_data
    if data.startswith("prev_page_"):
        current_page = int(data.split("_")[-1])
    elif data.startswith("next_page_"):
        current_page = int(data.split("_")[-1])
    else:
        return

    # Получаем список пользователей
    user_files = [f for f in os.listdir(USER_FILES_DIR) if f.endswith('_info.txt')]
    user_list = []
    for idx, filename in enumerate(user_files):
        domain = filename.replace('_info.txt', '')
        user_data = read_user_data(domain)
        user_list.append(f"<a href='https://t.me/{domain}'>{idx + 1}. {domain}</a> - {user_data['points']} / {user_data['invited']} / {user_data['registered_self']}")

    # Разбиваем список пользователей на страницы
    pages = [user_list[i:i + USERS_PER_PAGE] for i in range(0, len(user_list), USERS_PER_PAGE)]
    
    # Показываем новую страницу
    await show_user_page(update, context, pages, current_page)

def get_usrserd_handler():
    return CommandHandler("usrserd", usrserd)

def get_pagination_handler():
    return CallbackQueryHandler(handle_pagination, pattern="^(prev_page_|next_page_)")
