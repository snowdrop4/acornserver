from torrent.models.music import MusicReleaseGroup, MusicRelease, MusicTorrent


TorrentList = list[MusicTorrent]
ReleaseDictionary = dict[MusicRelease, TorrentList]
ReleaseGroupDictionary = dict[MusicReleaseGroup, ReleaseDictionary]


def group_torrents(torrents: TorrentList) -> ReleaseGroupDictionary:
	grouped: ReleaseGroupDictionary = { }
	
	for t in torrents:
		r  = t.release
		rg = r.release_group
		
		if rg in grouped:
			grouped[rg].setdefault(r, []).append(t)
		else:
			grouped[rg] = { r: [t] }
	
	return grouped
