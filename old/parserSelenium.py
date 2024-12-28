from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Запуск в безголовом режиме
options.add_argument('--no-sandbox')  # Отключение песочницы
options.add_argument('--disable-dev-shm-usage')  # Использование /tmp вместо /dev/shm
options.add_argument('--remote-debugging-port=9222')  # Убедитесь, что порт открыт


# Функция для получения последнего твита
def get_latest_tweet_with_selenium():
    # Запрос URL у пользователя
    twitter_url = input("Enter URL: ")

    # Настройка веб-драйвера
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(twitter_url)

    # Поиск последнего твита
    try:
        tweet = driver.find_element(By.TAG_NAME, 'article')
        tweet_text = tweet.text
        print("Последний твит:")
        print(tweet_text)
    except Exception as e:
        print(f"Ошибка при поиске твита: {e}")
    finally:
        driver.quit()

# Вызов функции
get_latest_tweet_with_selenium()
