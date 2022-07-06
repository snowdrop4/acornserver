Torrent tracker. Fixes some of the annoyances with Gazelle.

* Multiple artists with the same name all get different pages.
* Well-typed separation between:
	* artists (who may have any contributory relationship to a release group, such as "composer", "producer", "main", and so on)
	* release groups (the abstract concept of an release, that groups specific releases together)
	* releases (specific pressings of an album, special editions, alternate editions, and so on)
	* torrents (an encode of a release)
* The upload page is dynamic. Typing in the name of an artist brings up an autocomplete function, which consequently allows one to select from a list of pre-existing release groups and releases.
* Torrents can be uploaded from any page, with the relevant details filled in on the upload page. For example:
	* One can click "Upload Release Group" on an artist's page, to skip the artist part of the upload page, and directly add a new release group to the artist, a new release to the release group, and torrent to the release.
	* One can click "Upload Release" on a release group's page, to skip the artist and release group part of the upload page, and directly add a new release to the release group and torrent to the release.
* Not PHP.
* More to come.

![Release group page](/screenshots/release-group-page.png)

![Upload page](/screenshots/upload-page.png)
