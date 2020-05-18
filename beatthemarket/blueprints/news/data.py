import requests
from config import settings


def get_news(ticker, num_of_articles=10):
    res = requests.get(
        f"{settings.API_BASE_URL}/stable/stock/{ticker}/news/last/{num_of_articles}",
        params={'token': settings.MY_API_KEY})
    data = res.json()

    articles = []
    for article in data:
        articles.append(article)
    return articles


def get_tickers_news(tickers):
    tickers_articles = []
    for ticker in tickers:
        tickers_articles.append(get_news(ticker, num_of_articles=10))
    return tickers_articles
