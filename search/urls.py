from django.urls import path

from .views import user, music

app_name = "search"
urlpatterns = [
    path("music", music.search, name="music_search"),
    path("user", user.search, name="user_search"),
]
