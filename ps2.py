from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def get_latest_tweet_with_selenium():
    twitter_url = input("Введите URL профиля Twitter: ")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Безголовый режим (не отображает браузер)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Установка драйвера
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(twitter_url)

    try:
        # Ожидание появления последнего твита
        tweet = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//article[contains(@role, "article")]'))
        )
        tweet_text = tweet.text
        print("Последний твит:")
        print(tweet_text)
    except Exception as e:
        print(f"Ошибка при поиске твита: {e}")
    finally:
        driver.quit()

# Вызов функции
get_latest_tweet_with_selenium()
