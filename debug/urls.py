from django.urls import path

from .views import index, populate_music_database, populate_forum_database, populate_news_database, test_messages


app_name = 'debug'
urlpatterns = [
	path('', index, name=''),
	path('populate_music_database', populate_music_database, name='populate_music_database'),
	path('populate_forum_database', populate_forum_database, name='populate_forum_database'),
	path('populate_news_database',  populate_news_database,  name='populate_news_database'),
	path('test_messages', test_messages, name='test_messages'),
]
