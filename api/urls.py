from django.urls import path

from .search import autocomplete
from .inbox.views import InboxThreadView, InboxMessagesView
from .torrent.music import artist, release, contribution, release_group

app_name = "api"

search_autocomplete_music = [
    path(
        "autocomplete/music/artist",
        autocomplete.music.artist.autocomplete,
        name="music_artist_autocomplete",
    ),
    path(
        "autocomplete/music/release_group",
        autocomplete.music.release_group.autocomplete,
        name="music_release_group_autocomplete",
    ),
]

search_autocomplete_account = [
    path(
        "autocomplete/user",
        autocomplete.account.user.autocomplete,
        name="user_autocomplete",
    ),
]

torrent_music_artist = [
    path(
        "music/artist/view/<int:pk>",
        artist.view_json,
        name="music_artist_view",
    ),
    path(
        "music/artist/view/contributions/<int:pk>",
        artist.view_contributions_json,
        name="music_artist_view_contributions",
    ),
]

torrent_music_release_group = [
    path(
        "music/release_group/view/<int:pk>",
        release_group.view_json,
        name="music_release_group_view",
    ),
]

torrent_music_contribution = [
    path(
        "music/contribution/view/<int:pk>",
        contribution.view_json,
        name="music_contribution_view",
    ),
    path(
        "music/contribution/view/releases/<int:pk>",
        contribution.view_releases_json,
        name="music_contribution_view_releases",
    ),
]

torrent_music_release = [
    path(
        "music/release/view/<int:pk>",
        release.view_json,
        name="music_release_view",
    ),
]

inbox = [
    path("inbox/threads", InboxThreadView.as_view(), name="inbox_threads_view"),
    path(
        "inbox/thread/<int:thread_pk>/messages",
        InboxMessagesView.as_view(),
        name="inbox_messages_view",
    ),
]

urlpatterns = [
    *search_autocomplete_music,
    *search_autocomplete_account,
    *torrent_music_artist,
    *torrent_music_release_group,
    *torrent_music_contribution,
    *torrent_music_release,
    *inbox,
]
