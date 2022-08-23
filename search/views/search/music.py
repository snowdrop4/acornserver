from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator

from root import renderers
from search.forms.music import MusicAdvancedSearch
from torrent.models.music import MusicArtist, MusicReleaseGroup
from root.type_annotations import AuthedHttpRequest
from root.utils.get_parameters import fill_typed_get_parameters


def search(request: AuthedHttpRequest) -> HttpResponse:
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'page': (False, int, "must be an integer") })
	except ValueError as e:
		return renderers.render_http_bad_request(request, str(e))
	
	form = MusicAdvancedSearch(request.GET)
	
	template_args: dict[str, Any] = { 'form': form }
	
	if form.is_valid():
		query = None
		
		if form.cleaned_data['artist_name'] and form.cleaned_data['release_group_name']:
			model_name = 'release_group'
			query = MusicReleaseGroup.objects\
				.filter(name__contains=form.cleaned_data['release_group_name'])\
				.filter(contributions__artist__name__contains=form.cleaned_data['artist_name'])
		elif form.cleaned_data['artist_name']:
			model_name = 'artist'
			query = MusicArtist.objects.filter(name__contains=form.cleaned_data['artist_name'])
		elif form.cleaned_data['release_group_name']:
			model_name = 'release_group'
			query = MusicReleaseGroup.objects.filter(name__contains=form.cleaned_data['release_group_name'])
		
		if query is not None:
			current_page = get_params.get('page', 1)
			paginator = Paginator(query, 5)
			
			template_args['page'] = paginator.get_page(current_page)
			template_args['model_name'] = model_name
	
	return render(request, 'search/music.html', template_args)
