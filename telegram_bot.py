import telebot
from telebot import types
from twitter_bot import TwitterBot
from config import API_TOKEN, ACCOUNTS_FILE, KEYWORDS_FILE, PUBLIC_ID

# Создаем объект Telegram-бота
bot = telebot.TeleBot(API_TOKEN)

# Создаем объект Twitter-бота
twitter_bot = TwitterBot(ACCOUNTS_FILE, KEYWORDS_FILE, bot, PUBLIC_ID)

# Флаг для отслеживания состояния парсера
parser_running = False
# Флаг для разрешения ввода текста
allow_text_input = False

# Функция для отображения главного меню с инлайн-кнопками
def main_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Кнопка статуса парсера
    if parser_running:
        markup.add(types.InlineKeyboardButton("🛑 Остановить парсер", callback_data="stop_parser"))
    else:
        markup.add(types.InlineKeyboardButton("🚀 Запустить парсер", callback_data="start_parser"))

    markup.add(
        types.InlineKeyboardButton("➕ Добавить аккаунт", callback_data="add_account"),
        types.InlineKeyboardButton("➕ Добавить слово", callback_data="add_word"),
    )
    markup.add(
        types.InlineKeyboardButton("📜 Показать аккаунты", callback_data="show_accounts"),
        types.InlineKeyboardButton("📜 Показать слова", callback_data="show_words"),
    )

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_bot(message):
    main_menu(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global parser_running, allow_text_input

    if call.data == "start_parser":
        start_parsing(call)
    elif call.data == "stop_parser":
        stop_parsing(call)
    elif call.data == "add_account":
        add_account(call)
    elif call.data == "add_word":
        add_word(call)
    elif call.data == "show_accounts":
        show_accounts(call)
    elif call.data == "show_words":
        show_words(call)
    elif call.data.startswith("delete_account_"):
        confirm_delete_account(call)
    elif call.data.startswith("delete_word_"):
        confirm_delete_word(call)
    elif call.data == "cancel":
        cancel(call)

def start_parsing(call):
    global parser_running
    twitter_bot.start()
    parser_running = True
    bot.send_message(call.message.chat.id, "Парсер запущен.")
    main_menu(call.message)

def stop_parsing(call):
    global parser_running
    twitter_bot.stop()
    parser_running = False
    bot.send_message(call.message.chat.id, "Парсер остановлен.")
    main_menu(call.message)

def add_account(call):
    global allow_text_input
    allow_text_input = True  # Разрешаем ввод текста
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    msg = bot.send_message(call.message.chat.id, "Введите аккаунт Twitter для добавления:", reply_markup=markup)
    bot.register_next_step_handler(msg, save_account)

def save_account(message):
    global allow_text_input
    if not allow_text_input:
        bot.send_message(message.chat.id, "Ввод текста запрещен. Пожалуйста, используйте кнопку.")
        return

    try:
        # Сохраняем аккаунт, если ввод разрешен
        twitter_bot.save_account(message.text)
        bot.send_message(message.chat.id, f"Аккаунт {message.text} добавлен.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении аккаунта: {str(e)}")
    finally:
        allow_text_input = False  # Запрещаем ввод текста после завершения
        main_menu(message)

def add_word(call):
    global allow_text_input
    allow_text_input = True  # Разрешаем ввод текста
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    msg = bot.send_message(call.message.chat.id, "Введите ключевое слово для добавления:", reply_markup=markup)
    bot.register_next_step_handler(msg, save_word)

def save_word(message):
    global allow_text_input
    if not allow_text_input:
        bot.send_message(message.chat.id, "Ввод текста запрещен. Пожалуйста, используйте кнопку.")
        return

    try:
        # Сохраняем слово, если ввод разрешен
        twitter_bot.save_keyword(message.text)
        bot.send_message(message.chat.id, f"Ключевое слово '{message.text}' добавлено.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении ключевого слова: {str(e)}")
    finally:
        allow_text_input = False  # Запрещаем ввод текста после завершения
        main_menu(message)

def show_accounts(call):
    accounts = twitter_bot.load_accounts()
    markup = types.InlineKeyboardMarkup()
    
    if accounts:
        for account in accounts:
            markup.add(types.InlineKeyboardButton(f"Удалить {account}", callback_data=f"delete_account_{account}"))
        
        # Добавляем кнопку отмены
        markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
        
        bot.send_message(call.message.chat.id, "Выберите аккаунт для удаления:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Список аккаунтов пуст.")
        main_menu(call.message)

def show_words(call):
    keywords = twitter_bot.load_keywords()
    markup = types.InlineKeyboardMarkup()
    
    if keywords:
        for keyword in keywords:
            markup.add(types.InlineKeyboardButton(f"Удалить {keyword}", callback_data=f"delete_word_{keyword}"))
        
        # Добавляем кнопку отмены
        markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
        
        bot.send_message(call.message.chat.id, "Выберите слово для удаления:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Список ключевых слов пуст.")
    
    main_menu(call.message)

def confirm_delete_account(call):
    account = call.data.split("_", 2)[2]  # Получаем аккаунт из callback_data
    try:
        twitter_bot.delete_account(account)
        bot.send_message(call.message.chat.id, f"Аккаунт {account} удален.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка при удалении аккаунта: {str(e)}")
    main_menu(call.message)

def confirm_delete_word(call):
    keyword = call.data.split("_", 2)[2]  # Получаем слово из callback_data
    try:
        twitter_bot.delete_keyword(keyword)
        bot.send_message(call.message.chat.id, f"Ключевое слово '{keyword}' удалено.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка при удалении ключевого слова: {str(e)}")
    main_menu(call.message)

def cancel(call):
    global allow_text_input
    allow_text_input = False  # Запрещаем ввод текста при отмене
    bot.send_message(call.message.chat.id, "Действие отменено.")
    main_menu(call.message)

if __name__ == "__main__":
    bot.polling(none_stop=True)
