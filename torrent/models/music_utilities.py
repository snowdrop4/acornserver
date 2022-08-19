from django.db.models import QuerySet

from torrent.models.music import MusicRelease, MusicTorrent, MusicReleaseGroup

Torrents = list[MusicTorrent]
ReleaseDictionary = dict[MusicRelease, Torrents]
ReleaseGroupDictionary = dict[MusicReleaseGroup, ReleaseDictionary]


def group_torrents(torrents: QuerySet[MusicTorrent] | list[MusicTorrent]) -> ReleaseGroupDictionary:
	grouped: ReleaseGroupDictionary = { }
	
	for t in torrents:
		r  = t.release
		rg = r.release_group
		
		if rg in grouped:
			grouped[rg].setdefault(r, []).append(t)
		else:
			grouped[rg] = { r: [t] }
	
	return grouped
