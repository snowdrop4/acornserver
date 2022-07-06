from typing import Dict, List

from torrent.models.music import MusicReleaseGroup, MusicRelease, MusicTorrent


TorrentList = List[MusicTorrent]
ReleaseDictionary = Dict[MusicRelease, TorrentList]
ReleaseGroupDictionary = Dict[MusicReleaseGroup, ReleaseDictionary]


def group_torrents(torrents: TorrentList) -> ReleaseGroupDictionary:
	grouped = { }
	
	for t in torrents:
		r  = t.release
		rg = r.release_group
		
		if rg in grouped:
			grouped[rg].setdefault(r, []).append(t)
		else:
			grouped[rg] = { r: [t] }
	
	return grouped
