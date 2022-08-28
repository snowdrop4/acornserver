from typing import Any

from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from torrent.models.music import MusicContribution, MusicReleaseGroup
from root.type_annotations import AuthedHttpRequest


def view_json(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    contribution = get_object_or_404(MusicContribution, pk=pk)
    to_serialize: list[Any] = [contribution]

    if request.GET.get("release_group", "") == "expand":
        to_serialize.append(
            get_object_or_404(MusicReleaseGroup, pk=contribution.release_group.pk)
        )

    data = serializers.serialize("json", to_serialize)
    return HttpResponse(data, content_type="application/json")


def view_releases_json(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    contribution = get_object_or_404(MusicContribution, pk=pk)

    data = {}

    for count, val in enumerate(contribution.release_group.releases.all()):
        data[count] = {"pk": val.pk, "str": str(val)}

    return JsonResponse(data)
