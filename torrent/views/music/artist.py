from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.db import models

from root import messages
from torrent.models.music import MusicArtist
from torrent.forms.music.artist import MusicArtistFormAdd, MusicArtistFormEdit


def add(request):
	if request.method == 'POST':
		form = MusicArtistFormAdd(request.POST)
		
		if form.is_valid():
			artist = form.save()
			messages.creation(request, 'Created artist.')
			return redirect('torrent:music_artist_view', pk=artist.pk)
	else:
		form = MusicArtistFormAdd()
	
	return render(request, 'torrent/music/artist/add.html', { 'form': form })


def view(request, pk):
	artist = get_object_or_404(MusicArtist, pk=pk)
	
	contributions = artist.contributions.prefetch_related('release_group__releases__torrents__downloads').all()
	
	# { role: { release_group: [releases] } }
	releases_by_release_groups_by_roles = { }
	
	for i in contributions:
		releases_by_release_groups_by_roles.setdefault(i.get_contribution_type_display(), { })
		releases_by_release_groups_by_roles[i.get_contribution_type_display()][i.release_group] = i.release_group.releases.all()
	
	template_args = {
		'releases_by_release_groups_by_roles': releases_by_release_groups_by_roles,
		'artist': artist
	}
	
	return render(request, 'torrent/music/artist/view.html', template_args)


def edit(request, pk):
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


def delete(request, pk):
	artist = get_object_or_404(MusicArtist, pk=pk)
	
	if 'confirmation' in request.GET:
		if request.GET['confirmation'] == 'yes':
			try:
				artist.delete()
				messages.deletion(request, 'Deleted artist.')
				return redirect('torrent:music_latest')
			except models.ProtectedError:
				messages.failure(request, 'An artist that contains release groups cannot be deleted.')
		
		return redirect('torrent:music_artist_view', pk=artist.pk)
	
	return render(request, 'torrent/music/artist/delete.html', { 'artist': artist })


def view_json(request, pk):
	artist = get_object_or_404(MusicArtist, pk=pk)
	data = serializers.serialize('json', [artist])
	return HttpResponse(data, content_type='application/json')


def view_contributions_json(request, pk):
	artist = get_object_or_404(MusicArtist, pk=pk)
	
	data = { }
	
	for count, val in enumerate(artist.contributions.all()):
		data[count] = {
			'pk':  val.pk,
			'str': val.get_contribution_type_display() + " - " + str(val.release_group)
		}
	
	return JsonResponse(data)
