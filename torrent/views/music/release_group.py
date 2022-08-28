from typing import Any

from django.db import models
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import DeleteView

from root import messages, renderers
from torrent.models.music import MusicArtist, MusicReleaseGroup
from root.type_annotations import AuthedHttpRequest
from root.utils.get_parameters import fill_typed_get_parameters
from torrent.forms.music.contribution import MusicContributionFormWithArtistFK
from torrent.forms.music.release_group import MusicReleaseGroupForm


def add(request: AuthedHttpRequest) -> HttpResponse:
    try:
        get_params = fill_typed_get_parameters(
            request, {"artist": (True, int, "must be an integer")}
        )
    except ValueError as e:
        return renderers.render_http_bad_request(request, str(e))

    artist = get_object_or_404(MusicArtist, pk=get_params["artist"])

    if request.method == "POST":
        release_group_form = MusicReleaseGroupForm(request.POST)
        contribution_form = MusicContributionFormWithArtistFK(artist, request.POST)

        if release_group_form.is_valid() and contribution_form.is_valid():
            release_group = release_group_form.save()

            contribution = contribution_form.save(commit=False)
            contribution.artist = artist
            contribution.release_group = release_group
            contribution.save()

            messages.creation(request, "Created release group.")
            return redirect("torrent:music_release_group_view", pk=release_group.pk)
    else:
        release_group_form = MusicReleaseGroupForm()
        contribution_form = MusicContributionFormWithArtistFK(artist)

    template_args = {
        "release_group_form": release_group_form,
        "contribution_form": contribution_form,
    }

    return render(request, "torrent/music/release_group/add.html", template_args)


def view(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    try:
        get_params = fill_typed_get_parameters(
            request, {"artist": (False, int, "must be an integer")}
        )
    except ValueError as e:
        return renderers.render_http_bad_request(request, str(e))

    release_group = get_object_or_404(
        MusicReleaseGroup.objects.prefetch_related("contributions__artist"), pk=pk
    )

    template_args: dict[str, Any] = {"release_group": release_group}

    if "artist" in get_params:
        template_args["artist"] = get_object_or_404(
            MusicArtist, pk=get_params["artist"]
        )

    return render(request, "torrent/music/release_group/view.html", template_args)


def edit(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    release_group = get_object_or_404(MusicReleaseGroup, pk=pk)

    if request.method == "POST":
        form = MusicReleaseGroupForm(request.POST, instance=release_group)

        if form.is_valid():
            release_group = form.save()
            messages.modification(request, "Modified release group.")
            return redirect("torrent:music_release_group_view", pk=release_group.pk)
    else:
        form = MusicReleaseGroupForm(instance=release_group)

    return render(
        request,
        "torrent/music/release_group/edit.html",
        {"form": form, "release_group": release_group},
    )


class Delete(DeleteView):
    model = MusicReleaseGroup
    template_name = "torrent/music/release_group/delete.html"  # template to use
    context_object_name = "release_group"  # name of object in template

    def post(self, *args: Any, **kwargs: Any) -> HttpResponse:
        user = self.request.user
        release_group = self.get_object()

        if self.request.POST.get("confirm", "no") == "yes":
            # Only delete the release group if the current user has the
            # permission to delete releases groups, or if it was the current
            # user created this release group.
            if (
                user.has_perm("torrent.delete_musicreleasegroup")
                or user == release_group.creator
            ):
                try:
                    release_group.delete()
                    messages.deletion(self.request, "Deleted release group.")
                    return redirect("torrent:music_latest")
                except models.ProtectedError:
                    messages.failure(
                        self.request,
                        "A release group that contains releases cannot be deleted.",
                    )
            else:
                messages.error(
                    self.request, "Insufficient permissions to delete release group."
                )

        return redirect("torrent:music_release_group_view", pk=release_group.pk)
