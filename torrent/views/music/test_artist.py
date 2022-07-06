import copy

from django.urls import reverse
from django.test import TestCase, RequestFactory

from torrent.models.music import MusicArtist
from account.account_randomiser import create_random_user
import torrent.views.music.artist as artist_views


class TestArtist(TestCase):
	def setUp(self):
		self.requestFactory = RequestFactory()
		self.user = create_random_user()
		
		self.data = {
			'artist-name': 'Test, Test, and Away!',
			'artist-artist_type': MusicArtist.ArtistType.ARTIST
		}
		
	def test_add(self):
		url = reverse('torrent:music_artist_add')
		
		request = self.requestFactory.post(url, self.data)
		request.user = self.user
		
		artist_views.add(request)
		artist = MusicArtist.objects.get(pk=1)
		
		self.assertEquals(artist.name,        self.data['artist-name'])
		self.assertEquals(artist.artist_type, self.data['artist-artist_type'])
	
	def test_edit(self):
		args = { a.removeprefix('artist-'): b for (a, b) in self.data.items() }
		artist = MusicArtist.objects.create(**args)
		
		url = reverse('torrent:music_artist_edit', kwargs={ 'pk': artist.pk })
		
		modified_data = copy.deepcopy(self.data)
		modified_data['artist-name'] = 'ooooooooooooooo'
		modified_data['artist-artist_type'] = MusicArtist.ArtistType.PERSON
		
		request = self.requestFactory.post(url, modified_data)
		request.user = self.user
		
		artist_views.edit(request, artist.pk)
		artist.refresh_from_db()
		
		self.assertEquals(artist.name,        modified_data['artist-name'])
		self.assertEquals(artist.artist_type, modified_data['artist-artist_type'])
