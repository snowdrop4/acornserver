from django.urls import path

from .views.search import music

app_name = "search"
urlpatterns = [
    path("music", music.search, name="music_search"),
]
