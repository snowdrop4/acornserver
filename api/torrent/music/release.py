from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from torrent.models.music import MusicRelease
from root.type_annotations import AuthedHttpRequest


def view_json(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    release = get_object_or_404(MusicRelease, pk=pk)
    data = serializers.serialize("json", [release])
    return HttpResponse(data, content_type="application/json")
