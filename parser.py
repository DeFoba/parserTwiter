import requests
from bs4 import BeautifulSoup
from fp.fp import FreeProxy

px = FreeProxy(rand=True).get()

# Функция для получения последнего твита по ссылке
def get_latest_tweet_from_url(url, proxies=None):
    try:
        # Отправка GET-запроса к странице Twitter с использованием прокси
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()  # Проверка на ошибки запроса

        # Парсинг HTML-страницы
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск последнего твита
        tweet = soup.find('div', {'data-testid': 'tweet'})
        if tweet:
            # Извлечение текста твита
            tweet_text = tweet.find('div', {'lang': 'ru'}).get_text()
            
            # Извлечение tweet_id
            tweet_id = tweet['data-tweet-id']
            
            # Формирование ссылки на твит
            username = url.split('/')[-1]  # Получение имени пользователя из URL
            tweet_link = f"https://twitter.com/{username}/status/{tweet_id}"
            
            print("Последний твит:")
            print(tweet_text)
            print("Ссылка на твит:")
            print(tweet_link)
        else:
            print("Не удалось найти твит.")
    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")

# Пример использования
twitter_url = 'https://twitter.com/ilonmask2'  # Замените на нужную ссылку

# Прокси-сервер (пример)
proxies = {
    'http': px,  # Замените на ваш прокси
    'https': px,  # Замените на ваш прокси
}

get_latest_tweet_from_url(twitter_url, proxies)
