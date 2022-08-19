# Functions that create random entries in the database based on the models in `music.py`.
# This is for using in automated testing and seeding the database with data for development.

from typing import Any
import random

from django_countries import countries

from root.utils.random import random_str, random_date
from torrent.models.music import MusicArtist, MusicReleaseGroup, MusicContribution, MusicRelease


def create_random_artist() -> tuple[MusicArtist, dict]:
	data = {
		'artist-name': random_str(),
		'artist-artist_type': random.choice(MusicArtist.ArtistType.values),
		'artist-country': random.choice(countries)
	}
	
	args = { a.removeprefix('artist-'): b for (a, b) in data.items() }
	artist = MusicArtist.objects.create(**args)
	
	return artist, data


def create_random_release_group() -> tuple[MusicReleaseGroup, dict]:
	data = {
		'release_group-name': random_str(),
		'release_group-group_type': random.choice(MusicReleaseGroup.GroupType.values)
	}
	
	args = { a.removeprefix('release_group-'): b for (a, b) in data.items() }
	release_group = MusicReleaseGroup.objects.create(**args)
	
	return release_group, data


def create_random_contribution(
		artist: MusicArtist,
		release_group: MusicReleaseGroup
	) -> tuple[MusicContribution, dict]:
	data = { 'contribution-contribution_type': random.choice(MusicContribution.ContributionType.values) }
	
	args = { a.removeprefix('contribution-'): b for (a, b) in data.items() }
	contribution = MusicContribution.objects.create(**args, artist=artist, release_group=release_group)
	
	return contribution, data


def create_random_release(release_group: MusicReleaseGroup) -> tuple[MusicRelease, dict]:
	date = random_date()
	
	data: dict[str, Any] = {
		'release-date': '%d-%02d-%02d' % (date.year, date.month, date.day),
		'release-label': random_str(),
		'release-catalog_number': random_str(),
		'release-release_format': random.choice(MusicRelease.ReleaseFormat.values)
	}
	
	args = { a.removeprefix('release-'): b for (a, b) in data.items() }
	args['date'] = date
	args['release_group'] = release_group
	release = MusicRelease.objects.create(**args)
	
	return release, data
