from django.shortcuts import render

from torrent.models.music import MusicTorrent

from torrent.models.music_utilities import group_torrents


def latest_uploads(request):
	torrents = MusicTorrent.objects\
		.select_related('release__release_group')\
		.prefetch_related('downloads')\
		.order_by('-upload_datetime')[:10]
	
	grouped = group_torrents(torrents)
	
	return render(request, 'torrent/music/latest.html', { 'grouped_torrents': grouped })
