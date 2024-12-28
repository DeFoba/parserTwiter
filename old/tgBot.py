from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def start(update: Update, context: CallbackContext):
    bot.start()
    update.message.reply_text("Twitter бот запущен.")

def stop(update: Update, context: CallbackContext):
    bot.stop()
    update.message.reply_text("Twitter бот остановлен.")

if __name__ == "__main__":
    accounts_file = "accounts.txt"  # Укажите ваши файлы
    keywords_file = "keywords.txt"
    
    bot = TwitterBot(accounts_file, keywords_file)

    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()
