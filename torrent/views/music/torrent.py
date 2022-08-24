from typing import Any

from django.http import HttpRequest, FileResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views.generic.edit import DeleteView

from bcoding import bdecode, bencode

from root import messages, renderers
from torrent.metainfo import (get_torrent_size, get_torrent_file_listing,
                              get_infohash_sha1_hexdigest,)
from torrent.models.music import (MusicArtist, MusicRelease,
                                  MusicTorrent, MusicTorrentDownload,)
from root.type_annotations import AuthedHttpRequest
from root.utils.get_parameters import fill_typed_get_parameters
from torrent.forms.music.torrent import MusicTorrentFormAdd, MusicTorrentFormEdit


def add(request: AuthedHttpRequest) -> HttpResponse:
    try:
        get_params = fill_typed_get_parameters(
            request, {"release": (True, int, "must be an integer")}
        )
    except ValueError as e:
        return renderers.render_http_bad_request(request, str(e))

    fk = get_object_or_404(MusicRelease, pk=get_params["release"])

    if request.method == "POST":
        form = MusicTorrentFormAdd(fk, request.POST, request.FILES)

        if form.is_valid():
            # A torrent object requires more fields than the torrent form provides,
            #   so use `commit=False`, and then manually add these fields,
            #   before finally saving the torrent object.
            torrent = form.save(commit=False)

            metainfo = request.FILES["torrent-metainfo_file"]
            metainfo.seek(0)
            metainfo_decoded = bdecode(metainfo)

            torrent.uploader = request.user
            torrent.infohash_sha1_hexdigest = get_infohash_sha1_hexdigest(
                metainfo_decoded
            )
            torrent.torrent_size = get_torrent_size(metainfo_decoded)
            torrent.torrent_files = get_torrent_file_listing(metainfo_decoded)

            torrent.save()

            messages.creation(request, "Created torrent.")
            return redirect("torrent:music_torrent_view", pk=torrent.pk)
    else:
        form = MusicTorrentFormAdd(fk)

    return render(request, "torrent/music/torrent/add.html", {"form": form})


def view(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    try:
        get_params = fill_typed_get_parameters(
            request, {"artist": (False, int, "must be an integer")}
        )
    except ValueError as e:
        return renderers.render_http_bad_request(request, str(e))

    try:
        torrent = MusicTorrent.objects.select_related("release__release_group").get(
            pk=pk
        )
    except MusicTorrent.DoesNotExist:
        return renderers.render_http_not_found(request, "Torrent not found.")

    template_args = {
        "torrent": torrent,
        "release": torrent.release,
        "release_group": torrent.release.release_group,
    }

    if "artist" in get_params:
        template_args["artist"] = get_object_or_404(
            MusicArtist, pk=get_params["artist"]
        )

    return render(request, "torrent/music/torrent/view.html", template_args)


def edit(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    torrent = get_object_or_404(MusicTorrent, pk=pk)

    if request.method == "POST":
        form = MusicTorrentFormEdit(request.POST, request.FILES, instance=torrent)

        if form.is_valid():
            torrent = form.save()
            messages.modification(request, "Modified torrent.")
            return redirect("torrent:music_torrent_view", pk=torrent.pk)
    else:
        form = MusicTorrentFormEdit(instance=torrent)

    return render(
        request, "torrent/music/torrent/edit.html", {"form": form, "torrent": torrent}
    )


class Delete(DeleteView):
    model = MusicTorrent
    template_name = "torrent/music/torrent/delete.html"  # template to use
    context_object_name = "torrent"  # name of object in template

    def post(self, *args: Any, **kwargs: Any) -> HttpResponse:
        user = self.request.user
        torrent = self.get_object()

        if self.request.POST.get("confirm", "no") == "yes":
            # Only delete the torrent if the current user has the permission to delete torrents,
            #  or if it was the current user uploaded this torrent.
            if user.has_perm("torrent.delete_musictorrent") or user == torrent.uploader:
                torrent.delete()
                messages.deletion(self.request, "Deleted torrent.")
                return redirect("torrent:music_release_view", pk=torrent.release.pk)
            else:
                messages.error(
                    self.request, "Insufficient permissions to delete torrent."
                )

        return redirect("torrent:music_torrent_view", pk=torrent.pk)


EXTERNAL_URL = "http://127.0.0.1"
TRACKER_NAME = "[AcornTorrent]"

# Register the torrent in the user's downloads if the user has not downloaded
# the torrent before.
# 
# If the user has already downloaded the torrent before, update the download date.
# 
# Finally, send the torrent metainfo file as a response.
def download(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    # Get the torrent file
    torrent = get_object_or_404(MusicTorrent, pk=pk)

    # Get the object representing the user downloading the torrent
    (torrent_download, created) = MusicTorrentDownload.objects.get_or_create(
        torrent=torrent, user=request.user
    )

    # Update the timestamp of the last download, if necessary
    if not created:
        torrent_download.download_datetime = timezone.now()
        torrent_download.save()

    # Build the announce URL specific to the user downloading the torrent,
    # containing the user's passkey
    announce_url = EXTERNAL_URL + reverse(
        "tracker:bittorrent_announce",
        kwargs={
            "passkey": request.user.passkey.key,
            "torrent_type": "music",
        },
    )

    # Build the torrent filename
    release = torrent.release
    release_group = release.release_group

    encode_format = torrent.get_encode_format_display().replace(" /", "", 1)
    release_format = release.get_release_format_display()

    filename = (
        f"{TRACKER_NAME} {release.date} - "
        f"{release_group.name} ({release.label}, {release.catalog_number}) "
        f"[{encode_format}, {release_format}]"
    )

    # Update the announce URL in the torrent, then serve it
    with torrent.metainfo_file.open("br") as f:
        metainfo_decoded = bdecode(f)
        metainfo_decoded["announce"] = announce_url

        return HttpResponse(
            bencode(metainfo_decoded),
            headers={
                "Content-Type": "application/x-bittorrent",
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
