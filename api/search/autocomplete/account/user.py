from django.http import HttpResponse, JsonResponse

from account.models import User
from root.type_annotations import AuthedHttpRequest


def autocomplete(request: AuthedHttpRequest) -> HttpResponse:
    if "q" in request.GET:
        search_term = request.GET["q"]
        results = User.objects.filter(username__icontains=search_term)[:5]

        return JsonResponse(
            {"results": [(i.pk, i.username, i.get_absolute_url()) for i in results]}
        )

    return JsonResponse(
        {"error": "This function requires a GET parameter, 'q' for the search term."}
    )
