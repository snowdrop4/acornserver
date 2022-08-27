from django.urls import path

from .views.search import music
from .views.autocomplete.music import artist, release_group

app_name = "search"
urlpatterns = [
    path("music", music.search, name="music_search"),
    path(
        "autocomplete/music/artist",
        artist.autocomplete,
        name="music_artist_autocomplete",
    ),
    path(
        "autocomplete/music/release_group",
        release_group.autocomplete,
        name="music_release_group_autocomplete",
    ),
]
