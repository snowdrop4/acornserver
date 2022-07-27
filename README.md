# About

Torrent tracker. Fixes some of the annoyances with Gazelle.

Multiple artists with the same name all get different pages, owing to a well-typed separation between:

* artists (who may have any contributory relationship to a release group, such as "composer", "producer", "main", and so on)
* release groups (the abstract concept of an release, that groups specific releases together)
* releases (specific pressings of an album, special editions, alternate editions, and so on)
* torrents (an encode of a release)

The upload page is dynamic. Typing in the name of an artist brings up an autocomplete function, which allows one to select from a list of pre-existing release groups and releases for said artist.

Torrents can be uploaded from any page, with the relevant details filled in on the upload page. For example:

* One can click "Upload Release Group" on an artist's page, to skip the artist part of the upload page, and directly add a new release group to the artist, a new release to the release group, and torrent to the release.
* One can click "Upload Release" on a release group's page, to skip the artist and release group part of the upload page, and directly add a new release to the release group and torrent to the release.

# Screenshots

![Release group page](/screenshots/release-group-page.png)

![Upload page](/screenshots/upload-page.png)

# Feature List & Roadmap

* 🟩 Robust database schema
	- 🟩 capable of disambiguating multiple artists with the same name
* 🟩 Search
	- 🟩 with autocomplete
	- 🟨 advanced search with filters
* 🟩 metainfo uploading
* 🟩 metainfo downloading
* 🟩 bittorrent announce
* 🟩 Progressive upload page
	- 🟩 fields can be autocompleted by searching for an artist or album
	- 🟩 fields can be autocompleted by clicking "upload here" on an artist/release group/release page
* 🟩 Artist pages
	- 🟩 artist portrait image
	- 🟩 artist country flag
	- 🟨 artist biography
* 🟩 Release group pages
	- 🟩 album art image
* 🟩 Release pages
	- 🟩 album art image
* 🟩 Torrent pages
* 🟨 Web torrent support
	- ability to stream an album
	- ability to stream album art
* 🟩 Forum
	- 🟩 Threads
	- 🟩 Categories
* 🟩 Users
	- 🟩 User biography
	- 🟨 User avatar
	- 🟨 User inbox/messaging system
	- 🟩 Latest downloads/uploads
	- 🟨 Download/uploads list
	- 🟨 Download/upload totals and ratio
	- 🟩 Permissions system
	- 🟨 User classes
* 🟨 Requests
* 🟩 News

# Requirements

* Python >=3.10

# Dependancies

* django
* django-glrm
* django-markupfield
* django-picklefield
* django-debug-toolbar
* django-countries
* django-mptt
* bcoding
* markdown

# Development

## Installing

1. Install [pyenv](https://github.com/pyenv/pyenv) (intructions in the `README.md`)
2. Install [pipenv](https://github.com/pypa/pipenv) with `pip3 install pipenv`
3. Run `pipenv install` from the repository directory to set up a virtual environment with the necessary python version and packages

## Running

Create the default user groups: `pipenv run python3 manage.py create_groups`
Create a super user account: `pipenv run python3 manage.py createsuperuser`
Run the server: `pipenv run python3 manage.py runserver`

## Testing

`pipenv run python3 manage.py test`

# License & Credits

MIT License. See [LICENSE.md](../master/LICENSE.md). Credits and licenses for images can be found in [CREDITS.md](../master/CREDITS.md).
