from typing import Any

from django.http import HttpResponse
from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from root import messages, renderers
from search.forms.music import MusicAdvancedSearchForm
from torrent.models.music import MusicArtist, MusicReleaseGroup
from root.type_annotations import AuthedHttpRequest
from root.utils.get_parameters import fill_typed_get_parameters


def search(request: AuthedHttpRequest) -> HttpResponse:
    try:
        get_params = fill_typed_get_parameters(request, {"page": (False, int, "must be an integer")})
    except ValueError as e:
        return renderers.render_http_bad_request(request, str(e))

    form = MusicAdvancedSearchForm(request.GET)

    template_args: dict[str, Any] = {"form": form}

    if form.is_valid():
        query: QuerySet[MusicReleaseGroup] | QuerySet[MusicArtist]

        artist_name = form.cleaned_data["artist_name"]
        release_group_name = form.cleaned_data["release_group_name"]

        if artist_name and release_group_name:
            query = (
                MusicReleaseGroup.objects.filter(name__icontains=release_group_name)
                .filter(contributions__artist__name__icontains=artist_name)
                .order_by("pk")
            )
            return _search_release_group(request, form, query, get_params)
        elif release_group_name:
            query = MusicReleaseGroup.objects.filter(name__icontains=release_group_name).order_by("pk")
            return _search_release_group(request, form, query, get_params)
        elif artist_name:
            query = MusicArtist.objects.filter(name__icontains=artist_name).order_by("pk")
            return _search_artist(request, form, query, get_params)

    return render(request, "search/music.html", template_args)


def _search_artist(
    request: AuthedHttpRequest,
    form: MusicAdvancedSearchForm,
    query: QuerySet[MusicArtist],
    get_params: dict[str, Any],
) -> HttpResponse:
    if len(query) == 1:
        messages.information(request, "Redirected to lone matching artist for query.")
        return redirect(query[0].get_absolute_url())

    paginator = Paginator(query, 5)
    template_args: dict[str, Any] = {"form": form, "page": paginator.get_page(get_params.get("page", 1))}

    return render(request, "search/music_artist.html", template_args)


def _search_release_group(
    request: AuthedHttpRequest,
    form: MusicAdvancedSearchForm,
    query: QuerySet[MusicReleaseGroup],
    get_params: dict[str, Any],
) -> HttpResponse:
    if len(query) == 1:
        messages.information(request, "Redirected to lone matching release group for query.")
        return redirect(query[0].get_absolute_url())

    paginator = Paginator(query, 5)
    template_args: dict[str, Any] = {"form": form, "page": paginator.get_page(get_params.get("page", 1))}

    return render(request, "search/music_release_group.html", template_args)
