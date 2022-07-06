from django.db import models
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.core import serializers

from root import messages, renderers
from root.utils.get_parameters import fill_typed_get_parameters
from torrent.models.music import MusicArtist, MusicRelease, MusicReleaseGroup
from torrent.forms.music.release import MusicReleaseFormAdd, MusicReleaseFormEdit


def add(request):
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'release_group': (True, int, "must be an integer") })
	except ValueError as e:
		return renderers.render_http_bad_request(request, e)
	
	fk = get_object_or_404(MusicReleaseGroup, pk=get_params['release_group'])
	
	if request.method == 'POST':
		form = MusicReleaseFormAdd(fk, request.POST)
		
		if form.is_valid():
			release = form.save()
			messages.creation(request, 'Created release.')
			return redirect('torrent:music_release_view', pk=release.pk)
	else:
		form = MusicReleaseFormAdd(fk)
	
	return render(request, 'torrent/music/release/add.html', { 'form': form })


def view(request, pk):
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'artist': (False, int, "must be an integer") })
	except ValueError as e:
		return renderers.render_http_bad_request(request, e)
	
	try:
		release = MusicRelease.objects\
			.select_related('release_group')\
			.prefetch_related('torrents__downloads')\
			.get(pk=pk)
	except MusicRelease.DoesNotExist:
		return renderers.render_http_not_found(request, 'Release not found.')
	
	template_args = \
		{ 'release_group': release.release_group
		, 'release': release }
	
	if 'artist' in get_params:
		template_args['artist'] = get_object_or_404(MusicArtist, pk=get_params['artist'])
	
	return render(request, 'torrent/music/release/view.html', template_args)


def edit(request, pk):
	release = get_object_or_404(MusicRelease, pk=pk)
	
	if request.method == 'POST':
		form = MusicReleaseFormEdit(request.POST, instance=release)
		
		if form.is_valid():
			release = form.save()
			messages.modification(request, 'Modified release.')
			return redirect('torrent:music_release_view', pk=release.pk)
	else:
		form = MusicReleaseFormEdit(instance=release)
	
	return render(request, 'torrent/music/release/edit.html', { 'form': form, 'release': release })


def delete(request, pk):
	release = get_object_or_404(MusicRelease, pk=pk)
	
	if 'confirmation' in request.GET:
		if request.GET['confirmation'] == 'yes':
			try:
				release.delete()
				messages.deletion(request, 'Deleted release.')
				return redirect('torrent:music_release_group_view', pk=release.release_group.pk)
			except models.ProtectedError:
				messages.failure(request, 'A release that contains torrents cannot be deleted.')
		
		return redirect('torrent:music_release_view', pk=release.pk)
	
	return render(request, 'torrent/music/release/delete.html', { 'release': release })


def view_json(request, pk):
	release = get_object_or_404(MusicRelease, pk=pk)
	data = serializers.serialize('json', [release])
	return HttpResponse(data, content_type='application/json')
