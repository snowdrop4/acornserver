from django.db import models, IntegrityError
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404

from root import messages, renderers
from root.utils.get_parameters import fill_typed_get_parameters
from torrent.models.music import MusicArtist, MusicReleaseGroup, MusicContribution
from torrent.forms.music.contribution import (
	MusicContributionForm, MusicContributionFormAdd,
	MusicContributionFormArtistSearch
)


def add(request):
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'release_group': (True, int, "must be an integer")
			, 'page': (False, int, "must be an integer") }
		)
	except ValueError as e:
		return renderers.render_http_bad_request(request, e)
	
	release_group = get_object_or_404(MusicReleaseGroup, pk=get_params['release_group'])
	
	search_form = MusicContributionFormArtistSearch(request.GET)
	
	template_args = {
		'search_form': search_form,
		'release_group': release_group,
	}
	
	if search_form.is_valid() and search_form.cleaned_data['artist_name']:
		query = MusicArtist.objects.filter(name__contains=search_form.cleaned_data['artist_name'])
		
		paginator = Paginator(query, 5)
		current_page_num = get_params.get('page', 1)
		page = paginator.get_page(current_page_num)
		
		if request.method == 'POST':
			contribution_form = MusicContributionFormAdd(page.object_list, request.POST)
			
			if contribution_form.is_valid():
				contribution = contribution_form.save(commit=False)
				contribution.release_group = release_group
				
				try:
					contribution.save()
				except IntegrityError:
					messages.failure(request, 'Release groups cannot have \
						multiple contributions from the same artist.')
				else:
					messages.creation(request, 'Created contribution.')
				
				
				return redirect('torrent:music_release_group_view', pk=release_group.pk)
		else:
			contribution_form = MusicContributionFormAdd(page.object_list)
		
		template_args['page'] = page
		template_args['contribution_form'] = contribution_form
	
	return render(request, 'torrent/music/contribution/add.html', template_args)


def edit(request, pk):
	contribution = get_object_or_404(MusicContribution, pk=pk)
	
	if request.method == 'POST':
		form = MusicContributionForm(request.POST, instance=contribution)
		
		if form.is_valid():
			contribution = form.save()
			messages.modification(request, 'Modified contribution.')
			return redirect('torrent:music_release_group_view', pk=contribution.release_group.pk)
	else:
		form = MusicContributionForm(instance=contribution)
	
	return render(
		request, 'torrent/music/contribution/edit.html',
		{ 'form': form, 'contribution': contribution }
	)


def delete(request, pk):
	contribution = get_object_or_404(MusicContribution, pk=pk)
	
	if 'confirmation' in request.GET:
		release_group = contribution.release_group
		
		if request.GET['confirmation'] == 'yes':
			try:
				contribution.delete()
				messages.deletion(request, 'Deleted contribution.')
				return redirect('torrent:music_release_group_view', pk=release_group.pk)
			except models.ProtectedError:
				messages.failure(request, 'A contribution cannot be deleted\
					if it is the only contribution to a release group.')
		
		return redirect('torrent:music_release_group_view', pk=release_group.pk)
	
	return render(
		request, 'torrent/music/contribution/delete.html',
		{ 'contribution': contribution }
	)


def view_json(request, pk):
	contribution = get_object_or_404(MusicContribution, pk=pk)
	to_serialize = [contribution]
	
	if request.GET.get('release_group', '') == 'expand':
		to_serialize.append(get_object_or_404(MusicReleaseGroup, pk=contribution.release_group.pk))
	
	data = serializers.serialize('json', to_serialize)
	return HttpResponse(data, content_type='application/json')


def view_releases_json(request, pk):
	contribution = get_object_or_404(MusicContribution, pk=pk)
	
	data = { }
	
	for count, val in enumerate(contribution.release_group.releases.all()):
		data[count] = { 'pk': val.pk, 'str': str(val) }
	
	return JsonResponse(data)
