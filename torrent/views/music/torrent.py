from bcoding import bdecode

from django.shortcuts import redirect, render, get_object_or_404
from django.http import FileResponse
from django.utils import timezone

from root import messages, renderers
from root.utils.get_parameters import fill_typed_get_parameters
from torrent.metainfo import get_infohash_sha1_hexdigest, get_torrent_size, get_torrent_file_listing
from torrent.models.music import MusicArtist, MusicTorrent, MusicTorrentDownload, MusicRelease
from torrent.forms.music.torrent import MusicTorrentFormAdd, MusicTorrentFormEdit


def add(request):
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'release': (True, int, "must be an integer") })
	except ValueError as e:
		return renderers.render_http_bad_request(request, e)
	
	fk = get_object_or_404(MusicRelease, pk=get_params['release'])
	
	if request.method == 'POST':
		form = MusicTorrentFormAdd(fk, request.POST, request.FILES)
		
		if form.is_valid():
			# A torrent object requires more fields than the torrent form provides, so use `commit=False`
			# and then manually add these fields, before finally saving the torrent object.
			torrent = form.save(commit=False)
			
			metainfo = request.FILES['torrent-metainfo_file']
			metainfo.seek(0)
			metainfo_decoded = bdecode(metainfo)
			
			torrent.uploader = request.user
			torrent.infohash_sha1_hexdigest = get_infohash_sha1_hexdigest(metainfo_decoded)
			torrent.torrent_size  = get_torrent_size(metainfo_decoded)
			torrent.torrent_files = get_torrent_file_listing(metainfo_decoded)
			
			torrent.save()
			
			messages.creation(request, 'Created torrent.')
			return redirect('torrent:music_torrent_view', pk=torrent.pk)
	else:
		form = MusicTorrentFormAdd(fk)
	
	return render(request, 'torrent/music/torrent/add.html', { 'form': form })


def view(request, pk):
	try:
		get_params = fill_typed_get_parameters(request,
			{ 'artist': (False, int, "must be an integer") })
	except ValueError as e:
		return renderers.render_http_bad_request(request, e)
	
	try:
		torrent = MusicTorrent.objects\
			.select_related('release__release_group')\
			.get(pk=pk)
	except MusicTorrent.DoesNotExist:
		return renderers.render_http_not_found(request, 'Torrent not found.')
	
	template_args = \
		{ 'torrent': torrent
		, 'release': torrent.release
		, 'release_group': torrent.release.release_group }
	
	if 'artist' in get_params:
		template_args['artist'] = get_object_or_404(MusicArtist, pk=get_params['artist'])
	
	return render(request, 'torrent/music/torrent/view.html', template_args)


def edit(request, pk):
	torrent = get_object_or_404(MusicTorrent, pk=pk)
	
	if request.method == 'POST':
		form = MusicTorrentFormEdit(request.POST, request.FILES, instance=torrent)
		
		if form.is_valid():
			torrent = form.save()
			messages.modification(request, 'Modified torrent.')
			return redirect('torrent:music_torrent_view', pk=torrent.pk)
	else:
		form = MusicTorrentFormEdit(instance=torrent)
	
	return render(request, 'torrent/music/torrent/edit.html', { 'form': form, 'torrent': torrent })


def delete(request, pk):
	torrent = get_object_or_404(MusicTorrent, pk=pk)
	
	if 'confirmation' in request.GET:
		if request.GET['confirmation'] == 'yes':
			torrent.delete()
			messages.deletion(request, 'Deleted torrent.')
			return redirect('torrent:music_release_view', pk=torrent.release.pk)
		
		return redirect('torrent:music_torrent_view', pk=torrent.pk)
	
	return render(request, 'torrent/music/torrent/delete.html', { 'torrent': torrent })


# Register the torrent in the user's downloads if the user has not downloaded the torrent before.
# If the user has already downloaded the torrent before, update the download date.
# Finally, send the torrent metainfo file as a response.
def download(request, pk):
	torrent = get_object_or_404(MusicTorrent, pk=pk)
	
	(torrent_download, created) = MusicTorrentDownload.objects.get_or_create(torrent=torrent, user=request.user)
	
	if not created:
		torrent_download.download_datetime = timezone.now()
		torrent_download.save()
	
	return FileResponse(torrent.metainfo_file, as_attachment=True)
