import requests
from bs4 import BeautifulSoup

# Функция для получения последнего твита по ссылке
def get_latest_tweet_from_url(url):
    try:
        # Отправка GET-запроса к странице x.com
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки запроса

        # Парсинг HTML-страницы
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск последнего твита
        tweet = soup.find('article')  # Обычно твиты находятся в теге <article>
        if tweet:
            # Извлечение текста твита
            tweet_text = tweet.get_text()
            
            # Извлечение tweet_id (если доступно)
            tweet_id = tweet['data-tweet-id'] if 'data-tweet-id' in tweet.attrs else None
            
            # Формирование ссылки на твит
            username = url.split('/')[-1]  # Получение имени пользователя из URL
            tweet_link = f"https://x.com/{username}/status/{tweet_id}" if tweet_id else None
            
            print("Последний твит:")
            print(tweet_text)
            if tweet_link:
                print("Ссылка на твит:")
                print(tweet_link)
            else:
                print("Не удалось получить ID твита.")
        else:
            print("Не удалось найти твит.")
    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")

# Пример использования
# twitter_url = 'https://x.com/имя_пользователя'  # Замените на нужную ссылку
twitter_url = input('Enter url: ')

get_latest_tweet_from_url(twitter_url)
