from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.core import serializers

from root import messages, renderers
from root.utils.get_parameters import fill_typed_get_parameters
from torrent.models.music import MusicArtist, MusicReleaseGroup
from torrent.forms.music.release_group import MusicReleaseGroupForm
from torrent.forms.music.contribution import MusicContributionFormWithArtistFK


def add(request):
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'artist': (True, int, "must be an integer") })
	except ValueError as e:
		return renderers.render_http_bad_request(request, e)
	
	artist = get_object_or_404(MusicArtist, pk=get_params['artist'])
	
	if request.method == 'POST':
		release_group_form = MusicReleaseGroupForm(request.POST)
		contribution_form = MusicContributionFormWithArtistFK(artist, request.POST)
		
		if release_group_form.is_valid() and contribution_form.is_valid():
			release_group = release_group_form.save()
			
			contribution = contribution_form.save(commit=False)
			contribution.artist = artist
			contribution.release_group = release_group
			contribution.save()
			
			messages.creation(request, 'Created release group.')
			return redirect('torrent:music_release_group_view', pk=release_group.pk)
	else:
		release_group_form = MusicReleaseGroupForm()
		contribution_form = MusicContributionFormWithArtistFK(artist)
	
	template_args = \
		{ 'release_group_form': release_group_form 
		, 'contribution_form':  contribution_form }
	
	return render(request, 'torrent/music/release_group/add.html', template_args)


def view(request, pk):
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'artist': (False, int, "must be an integer") })
	except ValueError as e:
		return renderers.render_http_bad_request(request, e)
	
	release_group = get_object_or_404(MusicReleaseGroup, pk=pk)
	
	template_args = { 'release_group': release_group }
	
	if 'artist' in get_params:
		template_args['artist'] = get_object_or_404(MusicArtist, pk=get_params['artist'])
	
	return render(request, 'torrent/music/release_group/view.html', template_args )


def edit(request, pk):
	release_group = get_object_or_404(MusicReleaseGroup, pk=pk)
	
	if request.method == 'POST':
		form = MusicReleaseGroupForm(request.POST, instance=release_group)
		
		if form.is_valid():
			release_group = form.save()
			messages.modification(request, 'Modified release group.')
			return redirect('torrent:music_release_group_view', pk=release_group.pk)
	else:
		form = MusicReleaseGroupForm(instance=release_group)
	
	return render(request, 'torrent/music/release_group/edit.html', { 'form': form, 'release_group': release_group })


def delete(request, pk):
	release_group = get_object_or_404(MusicReleaseGroup, pk=pk)
	
	if 'confirmation' in request.GET:
		if request.GET['confirmation'] == 'yes':
			try:
				release_group.delete()
				messages.deletion(request, 'Deleted release group.')
				return redirect('torrent:music_latest')
			except models.ProtectedError:
				messages.failure(request, 'A release group that contains releases cannot be deleted.')
		
		return redirect('torrent:music_release_group_view', pk=release_group.pk)
	
	return render(request, 'torrent/music/release_group/delete.html', { 'release_group': release_group })


def view_json(request, pk):
	release_group = get_object_or_404(MusicReleaseGroup, pk=pk)
	data = serializers.serialize('json', [release_group])
	return HttpResponse(data, content_type='application/json')
