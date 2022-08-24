from random import random

from root.models import NewsArticle
from root.utils.random import random_str, random_prose


def create_random_news_article() -> tuple[NewsArticle, dict]:
    data = {
        "news-title": random_str(2) + " " + random_str(5) + " " + random_str(5),
        "news-content": random_prose(30),
    }

    args = {a.removeprefix("news-"): b for (a, b) in data.items()}
    news_article = NewsArticle.objects.create(**args)

    return news_article, data
