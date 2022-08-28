from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from torrent.models.music import MusicArtist
from root.type_annotations import AuthedHttpRequest


def view_json(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    artist = get_object_or_404(MusicArtist, pk=pk)
    data = serializers.serialize("json", [artist])
    return HttpResponse(data, content_type="application/json")


def view_contributions_json(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    artist = get_object_or_404(MusicArtist, pk=pk)

    data = {}

    for count, val in enumerate(artist.contributions.all()):
        data[count] = {
            "pk": val.pk,
            "str": f"{val.get_contribution_type_display()} - {str(val.release_group)}",
        }

    return JsonResponse(data)
