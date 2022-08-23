from typing import Any

from django.db import models
from django.core import serializers
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import DeleteView

from root import messages, renderers
from torrent.models.music import MusicArtist, MusicRelease, MusicReleaseGroup
from root.type_annotations import AuthedHttpRequest
from root.utils.get_parameters import fill_typed_get_parameters
from torrent.forms.music.release import MusicReleaseFormAdd, MusicReleaseFormEdit


def add(request: AuthedHttpRequest) -> HttpResponse:
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'release_group': (True, int, 'must be an integer') }
		)
	except ValueError as e:
		return renderers.render_http_bad_request(request, str(e))
	
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


def view(request: AuthedHttpRequest, pk: int) -> HttpResponse:
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'artist': (False, int, 'must be an integer') }
		)
	except ValueError as e:
		return renderers.render_http_bad_request(request, str(e))
	
	try:
		release = MusicRelease.objects\
			.select_related('release_group')\
			.prefetch_related('torrents__downloads')\
			.get(pk=pk)
	except MusicRelease.DoesNotExist:
		return renderers.render_http_not_found(request, 'Release not found.')
	
	template_args = {
		'release_group': release.release_group,
		'release': release,
	}
	
	if 'artist' in get_params:
		template_args['artist'] = get_object_or_404(MusicArtist, pk=get_params['artist'])
	
	return render(request, 'torrent/music/release/view.html', template_args)


def edit(request: AuthedHttpRequest, pk: int) -> HttpResponse:
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


class Delete(DeleteView):
	model = MusicRelease
	template_name = 'torrent/music/release/delete.html'  # template to use
	context_object_name = 'release'  # name of object in template
	
	def post(self, *args: Any, **kwargs: Any) -> HttpResponse:
		user = self.request.user
		release = self.get_object()
		
		if self.request.POST.get('confirm', 'no') == 'yes':
			# Only delete the release if the current user has the permission to delete releases,
			#  or if it was the current user created this release.
			if user.has_perm('torrent.delete_musicrelease') or user == release.creator:
				try:
					release.delete()
					messages.deletion(self.request, 'Deleted release.')
					return redirect('torrent:music_release_group_view', pk=release.release_group.pk)
				except models.ProtectedError:
					messages.failure(self.request, 'A release that contains torrents cannot be deleted.')
			else:
				messages.error(self.request, 'Insufficient permissions to delete release.')
		
		return redirect('torrent:music_release_view', pk=release.pk)


def view_json(request: AuthedHttpRequest, pk: int) -> HttpResponse:
	release = get_object_or_404(MusicRelease, pk=pk)
	data = serializers.serialize('json', [release])
	return HttpResponse(data, content_type='application/json')
