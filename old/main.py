from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from os import listdir

TOKEN = ''
USERS = []
wait_user = False

if not 'users.txt' in listdir():
    open('users.txt', 'w', encoding='utf8').close()

else:
    with open('users.txt', 'r', encoding='utf8') as file:
        for user in file.read().split('\n'):
            if user != '':
                USERS.append(user)

def add_user(user_link):
    if not user_link in USERS:
        USERS.append(user_link)

        with open('users.txt', 'w', encoding='utf8') as file:
            file.write('\n'.join(USERS))

        return True
    return False

def check_chat(chat_id):
    if not '-' in str(chat_id):
        return True
    return False

def create_keyboard(method='default', btn_list:list=None):
    keyboard = InlineKeyboardMarkup()

    match method:
        case 'default':
            keyboard.add(InlineKeyboardButton('Список', callback_data='user_list'), InlineKeyboardButton('Добавить', callback_data='user_add'))

        case 'cancel':
            keyboard.add(InlineKeyboardButton('Отмена', callback_data='cancel'))

        case 'remove':
            keyboard.add(InlineKeyboardButton('Отмена', callback_data='cancel'), InlineKeyboardButton('Удалить из списка', callback_data='remove'))

        case 'list':
            keyboard.add(InlineKeyboardButton('Отмена', callback_data='cancel'))

            for btn in btn_list:
                keyboard.add(InlineKeyboardButton(btn, callback_data='rU#' + btn))

    return keyboard


bot = TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    if not check_chat(message.chat.id): return

    bot.send_message(message.chat.id, 'Привет! Выбери какое действие ты хочешь сделать:', reply_markup=create_keyboard('default'))

@bot.message_handler(content_types=['text'])
def text_message(message):
    global wait_user
    if not check_chat(message.chat.id): return

    if wait_user:
        if add_user(message.text):
            bot.send_message(message.chat.id, 'Аккаунт был добавлен в список', reply_markup=create_keyboard('default'))
        else:
            bot.send_message(message.chat.id, 'Аккаунт уже был в списке', reply_markup=create_keyboard('default'))

        wait_user = False

    else:
        bot.send_message(message.chat.id, 'Что вы хотите сделать? Выберите действие:', reply_markup=create_keyboard('default'))

@bot.callback_query_handler(lambda call: True)
def bot_callback(call):
    global wait_user
    # print(call.data)

    match call.data:
        case 'user_add':
            wait_user = True
            bot.send_message(call.message.chat.id, 'Отправь ссылку на аккаунт:', reply_markup=create_keyboard('cancel'))

        case 'user_list':
            bot.send_message(call.message.chat.id, 'Список аккаунтов:\n' + '\n'.join(USERS), reply_markup=create_keyboard('remove'))

        case 'cancel':
            wait_user = False
            bot.send_message(call.message.chat.id, 'Отмена! Выберите действие:', reply_markup=create_keyboard('default'))

        case 'remove':
            bot.send_message(call.message.chat.id, 'Отмена! Выберите действие:', reply_markup=create_keyboard('list', USERS))

    if 'rU#' in call.data:
        count = 0
        for user in USERS:
            if call.data.split('rU#', 1)[1] == user:
                USERS.pop(count)
                break

            count += 1

        bot.send_message(call.message.chat.id, 'Аккаунт был удален! Выберите действие:', reply_markup=create_keyboard('default'))



    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    bot.infinity_polling()