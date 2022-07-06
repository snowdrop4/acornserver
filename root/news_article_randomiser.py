from random import random

from root.utils.random import random_str, random_prose

from root.models import NewsArticle

def create_random_news_article():
	data = {
		'news-title': random_str(2) + ' ' + random_str(5) + ' ' + random_str(5),
		'news-content': random_prose(30)
	}
	
	args = { a.removeprefix('news-'): b for (a, b) in data.items() }
	news_article = NewsArticle.objects.create(**args)
	
	return news_article, data