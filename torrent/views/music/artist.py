from typing import Any

from django.db import models
from django.core import serializers
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import DeleteView

from root import messages
from torrent.models.music import MusicArtist, MusicRelease, MusicReleaseGroup
from root.type_annotations import AuthedHttpRequest
from torrent.forms.music.artist import MusicArtistFormAdd, MusicArtistFormEdit


def add(request: AuthedHttpRequest) -> HttpResponse:
	if request.method == 'POST':
		form = MusicArtistFormAdd(request.POST)
		
		if form.is_valid():
			artist = form.save()
			messages.creation(request, 'Created artist.')
			return redirect('torrent:music_artist_view', pk=artist.pk)
	else:
		form = MusicArtistFormAdd()
	
	return render(request, 'torrent/music/artist/add.html', { 'form': form })


def view(request: AuthedHttpRequest, pk: int) -> HttpResponse:
	artist = get_object_or_404(MusicArtist, pk=pk)
	
	# `torrents` and `peers` both used in template, so prefetch them now to save database time
	contributions = artist.contributions\
		.prefetch_related('release_group__releases__torrents__downloads')\
		.prefetch_related('release_group__releases__torrents__peers')\
		.all()
	
	# Construct a dictionary like: { role: { release_group: [releases] } }
	#   so that the template can simply iterate over to display
	#   each release for every release group, grouped by contribution type. 
	releases_by_release_groups_by_roles: dict[str, dict[MusicReleaseGroup, QuerySet[MusicRelease]]] = { }
	
	for i in contributions:
		contribution_type = i.get_contribution_type_display()
		release_group     = i.release_group
		releases          = i.release_group.releases.all()
		
		releases_by_release_groups_by_roles.setdefault(contribution_type, { })
		releases_by_release_groups_by_roles[contribution_type][release_group] = releases
	
	template_args = {
		'releases_by_release_groups_by_roles': releases_by_release_groups_by_roles,
		'artist': artist
	}
	
	return render(request, 'torrent/music/artist/view.html', template_args)


def edit(request: AuthedHttpRequest, pk: int) -> HttpResponse:
	artist = get_object_or_404(MusicArtist, pk=pk)
	
	if request.method == 'POST':
		form = MusicArtistFormEdit(request.POST, instance=artist)
		
		if form.is_valid():
			artist = form.save()
			messages.modification(request, 'Modified artist.')
			return redirect('torrent:music_artist_view', pk=artist.pk)
	else:
		form = MusicArtistFormEdit(instance=artist)
	
	return render(request, 'torrent/music/artist/edit.html', { 'form': form, 'artist': artist })


class Delete(DeleteView):
	model = MusicArtist
	template_name = 'torrent/music/artist/delete.html'  # template to use
	context_object_name = 'artist'  # name of object in template
	
	def post(self, *args: Any, **kwargs: Any) -> HttpResponse:
		user = self.request.user
		artist = self.get_object()
		
		if self.request.POST.get('confirm', 'no') == 'yes':
			# Only delete the artist if the current user has the permission to delete artists,
			#  or if it was the current user created this artist.
			if user.has_perm('torrent.delete_musicartist') or user == artist.creator:
				try:
					artist.delete()
					messages.deletion(self.request, 'Deleted artist.')
					return redirect('torrent:music_latest')
				except models.ProtectedError:
					messages.failure(self.request,
						'An artist that contains release groups cannot be deleted.'
					)
			else:
				messages.error(self.request, 'Insufficient permissions to delete artist.')
		
		return redirect('torrent:music_artist_view', pk=artist.pk)


def view_json(request: AuthedHttpRequest, pk: int) -> HttpResponse:
	artist = get_object_or_404(MusicArtist, pk=pk)
	data = serializers.serialize('json', [artist])
	return HttpResponse(data, content_type='application/json')


def view_contributions_json(request: AuthedHttpRequest, pk: int) -> HttpResponse:
	artist = get_object_or_404(MusicArtist, pk=pk)
	
	data = { }
	
	for count, val in enumerate(artist.contributions.all()):
		data[count] = {
			'pk':  val.pk,
			'str': f'{val.get_contribution_type_display()} - {str(val.release_group)}'
		}
	
	return JsonResponse(data)
