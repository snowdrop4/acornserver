from django.http import HttpResponse
from django.shortcuts import render

from torrent.models.music import MusicTorrent
from root.type_annotations import AuthedHttpRequest
from torrent.models.music_utilities import group_torrents


def latest_uploads(request: AuthedHttpRequest) -> HttpResponse:
    torrents = (
        MusicTorrent.objects.select_related("release__release_group")
        .prefetch_related("downloads")
        .order_by("-upload_datetime")[:10]
    )

    return render(
        request,
        "torrent/music/latest.html",
        {"grouped_torrents": group_torrents(torrents)},
    )
