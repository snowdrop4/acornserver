from django.http import JsonResponse

from torrent.models.music import MusicReleaseGroup


def autocomplete(request):
	if 'q' in request.GET:
		search_term = request.GET['q']
		results = MusicReleaseGroup.objects.filter(name__contains=search_term)[:5]
		
		success = {
			'results': [ (i.pk, i.name, i.get_absolute_url()) for i in results ]
		}
		
		return JsonResponse(success)
	
	error = { "error": "This function requires a GET parameter, 'q' for the search term." }
	return JsonResponse(error)
