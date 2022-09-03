from django.http import HttpResponse, JsonResponse

from torrent.models.music import MusicReleaseGroup
from root.type_annotations import AuthedHttpRequest


def autocomplete(request: AuthedHttpRequest) -> HttpResponse:
    if "q" in request.GET:
        search_term = request.GET["q"]
        results = MusicReleaseGroup.objects.filter(name__icontains=search_term)[:5]

        return JsonResponse(
            {"results": [(i.pk, i.name, i.get_absolute_url()) for i in results]}
        )

    return JsonResponse(
        {"error": "This function requires a GET parameter, 'q' for the search term."}
    )
