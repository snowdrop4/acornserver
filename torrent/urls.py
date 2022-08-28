from django.urls import path

from .views.music import (
    artist,
    latest,
    upload,
    release,
    torrent,
    contribution,
    release_group,
)

app_name = "torrent"
urlpatterns = [
    path("music/artist/add",             artist.add,              name="music_artist_add"),
    path("music/artist/view/<int:pk>",   artist.view,             name="music_artist_view"),
    path("music/artist/edit/<int:pk>",   artist.edit,             name="music_artist_edit"),
    path("music/artist/delete/<int:pk>", artist.Delete.as_view(), name="music_artist_delete"),

    path("music/release_group/add",             release_group.add,              name="music_release_group_add"),
    path("music/release_group/view/<int:pk>",   release_group.view,             name="music_release_group_view"),
    path("music/release_group/edit/<int:pk>",   release_group.edit,             name="music_release_group_edit"),
    path("music/release_group/delete/<int:pk>", release_group.Delete.as_view(), name="music_release_group_delete"),

    path("music/contribution/add",             contribution.add,               name="music_contribution_add"),
    path("music/contribution/edit/<int:pk>",   contribution.edit,              name="music_contribution_edit"),
    path("music/contribution/delete/<int:pk>", contribution.Delete.as_view(),  name="music_contribution_delete"),

    path("music/release/add",             release.add,              name="music_release_add"),
    path("music/release/view/<int:pk>",   release.view,             name="music_release_view"),
    path("music/release/edit/<int:pk>",   release.edit,             name="music_release_edit"),
    path("music/release/delete/<int:pk>", release.Delete.as_view(), name="music_release_delete"),

    path("music/torrent/add",               torrent.add,              name="music_torrent_add"),
    path("music/torrent/view/<int:pk>",     torrent.view,             name="music_torrent_view"),
    path("music/torrent/edit/<int:pk>",     torrent.edit,             name="music_torrent_edit"),
    path("music/torrent/delete/<int:pk>",   torrent.Delete.as_view(), name="music_torrent_delete"),
    path("music/torrent/download/<int:pk>", torrent.download,         name="music_torrent_download"),

    path("music/upload", upload.upload, name="music_upload"),

    path("music/latest", latest.latest_uploads, name="music_latest"),
]
