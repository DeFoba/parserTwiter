import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class TwitterBot:
    def __init__(self, accounts_file, keywords_file):
        self.accounts_file = accounts_file
        self.keywords_file = keywords_file
        self.keywords = self.load_keywords()
        self.seen_tweets = set()  # Множество для хранения уникальных твитов
        self.running = False  # Флаг для управления работой бота
        self.thread = None  # Поток для работы бота

    def load_keywords(self):
        with open(self.keywords_file, 'r') as file:
            return [keyword.strip() for keyword in file.readlines()]

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.check_for_new_tweets)
            self.thread.start()
            print("Twitter бот запущен.")

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()  # Ждем, пока поток завершится
            print("Twitter бот остановлен.")

    def check_for_new_tweets(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Установка драйвера
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        with open(self.accounts_file, 'r') as file:
            accounts = [account.strip() for account in file.readlines()]

        try:
            while self.running:  # Бесконечный цикл
                for account in accounts:
                    if not self.running:
                        break  # Проверяем флаг перед каждой итерацией

                    twitter_url = account
                    print(f"\nПроверка аккаунта: {twitter_url}")

                    driver.get(twitter_url)

                    try:
                        # Ожидание появления твитов на странице
                        tweets = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//article[contains(@role, "article")]'))
                        )

                        # Поиск первого твита, содержащего одно из ключевых слов
                        for tweet in tweets:
                            tweet_text = tweet.text
                            tweet_link = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]').get_attribute('href')

                            # Проверка на наличие хотя бы одного ключевого слова и уникальность
                            if any(keyword.lower() in tweet_text.lower() for keyword in self.keywords) and tweet_link not in self.seen_tweets:
                                print(f"Найден твит с ключевым словом: {tweet_text}")
                                print(f"Ссылка на твит: {tweet_link}")

                                # Сохраняем ссылку на твит в файл
                                with open('tweets.txt', 'a') as output_file:
                                    output_file.write(f"{tweet_link}\n")
                                
                                self.seen_tweets.add(tweet_link)  # Добавляем ссылку в множество
                                break  # Останавливаемся на первом найденном твите

                        else:
                            print("Твитов с указанными ключевыми словами не найдено.")

                    except Exception as e:
                        print(f"Ошибка при поиске твитов: {e}")

                time.sleep(30)  # Ожидание 30 секунд перед следующим обновлением

        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            driver.quit()

# Пример использования
if __name__ == "__main__":
    accounts_file = input("Введите имя файла с аккаунтами (например, accounts.txt): ")
    keywords_file = input("Введите имя файла с ключевыми словами (например, keywords.txt): ")

    bot = TwitterBot(accounts_file, keywords_file)

    # Запуск бота
    bot.start()

    # Остановка бота (для тестирования, можно заменить на обработчик команд Telegram)
    try:
        while True:
            command = input("Введите 'stop' для остановки бота: ")
            if command.lower() == 'stop':
                bot.stop()
                break
    except KeyboardInterrupt:
        bot.stop()
