import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class TwitterBot:
    def __init__(self, accounts_file, keywords_file, bot=None, chat_id=None):
        self.accounts_file = accounts_file
        self.keywords_file = keywords_file
        self.keywords = self.load_keywords()
        self.seen_tweets = set()  # Множество для хранения уникальных твитов
        self.running = False  # Флаг для управления работой бота
        self.thread = None  # Поток для работы бота
        self.bot = bot
        self.chat_id = chat_id

    def send_telegram(self, text):
        self.bot.send_message(self.chat_id, text)

    def load_keywords(self):
        with open(self.keywords_file, 'r') as file:
            return [keyword.strip() for keyword in file.readlines()]

    def save_account(self, account):
        with open(self.accounts_file, 'a') as file:
            file.write(account + '\n')

    def save_keyword(self, keyword):
        with open(self.keywords_file, 'a') as file:
            file.write(keyword + '\n')

    def load_accounts(self):
        with open(self.accounts_file, 'r') as file:
            return [account.strip() for account in file.readlines()]

    def load_keywords(self):
        with open(self.keywords_file, 'r') as file:
            return [keyword.strip() for keyword in file.readlines()]
        
    def delete_account(self, account):
        accounts = self.load_accounts()
        new_list = []

        for ac in accounts:
            if account != ac:
                new_list.append(ac)

        with open(self.accounts_file, 'w') as file:
            for ac in new_list:
                file.write(ac + '\n')

    def delete_keyword(self, keyword):
        keywords = self.load_keywords()
        new_list = []

        for ac in keywords:
            if keyword != ac:
                new_list.append(ac)

        with open(self.keywords_file, 'w') as file:
            for ac in new_list:
                file.write(ac + '\n')

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

        accounts = self.load_accounts()

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

                                self.send_telegram(tweet_link)

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
