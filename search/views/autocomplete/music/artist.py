from django.http import HttpRequest, HttpResponse, JsonResponse

from torrent.models.music import MusicArtist
from root.type_annotations import AuthedHttpRequest


def autocomplete(request: AuthedHttpRequest) -> HttpResponse:
	if 'q' in request.GET:
		search_term = request.GET['q']
		results = MusicArtist.objects.filter(name__contains=search_term)[:5]
		
		success = {
			'results': [ (i.pk, i.name, i.get_absolute_url()) for i in results ]
		}
		
		return JsonResponse(success)
	
	error = { "error": "This function requires a GET parameter, 'q' for the search term." }
	return JsonResponse(error)
