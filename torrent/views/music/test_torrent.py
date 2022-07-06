import os
import copy

from django.conf import settings
from django.urls import reverse
from django.test import TestCase, RequestFactory

from torrent.models.music import MusicTorrent
from torrent.models.music_randomiser import create_random_release, create_random_release_group
from account.account_randomiser import create_random_user
import torrent.views.music.torrent as torrent_views


class TestTorrent(TestCase):
	def setUp(self):
		self.requestFactory = RequestFactory()
		self.user = create_random_user()
		
		torrent_path = os.path.join(settings.BASE_DIR, 'test', 'metainfo-v1-multi.torrent')
		self.torrent_file = open(torrent_path, 'rb')
		
		self.release_group, _ = create_random_release_group()
		self.release, _ = create_random_release(self.release_group)
		
		self.torrent_data = {
			'torrent-metainfo_file': self.torrent_file,
			'torrent-encode_format': MusicTorrent.EncodeFormat.MP3VB2,
			'torrent-release': str(self.release.pk)
		}
	
	def tearDown(self):
		self.torrent_file.close()
	
	def test_add(self):
		url = reverse('torrent:music_torrent_add') + '?release=' + str(self.release.pk)
		
		request = self.requestFactory.post(url, self.torrent_data, format='multipart')
		request.user = self.user
		
		torrent_views.add(request)
		torrent = MusicTorrent.objects.get(pk=1)
		
		self.assertEquals(torrent.uploader, self.user)
		self.assertEquals(torrent.release.pk, self.release.pk)
		self.assertEquals(torrent.encode_format, self.torrent_data['torrent-encode_format'])
	
	def test_edit(self):
		# First, create a new torrent.
		url = reverse('torrent:music_torrent_add') + '?release=' + str(self.release.pk)
		
		request = self.requestFactory.post(url, self.torrent_data, format='multipart')
		request.user = self.user
		
		torrent_views.add(request)
		torrent = MusicTorrent.objects.get(pk=1)
		
		# Second, modify it.
		modified_data = copy.copy(self.torrent_data)
		modified_data['torrent-metainfo_file'] = '' # expected to be empty if we aren't modifying it
		modified_data['torrent-encode_format'] = MusicTorrent.EncodeFormat.FLAC24
		
		url = reverse('torrent:music_torrent_edit', kwargs={ 'pk': torrent.pk })
		
		request = self.requestFactory.post(url, modified_data, format='multipart')
		request.user = self.user
		
		torrent_views.edit(request, torrent.pk)
		torrent.refresh_from_db()
		
		self.assertEquals(torrent.uploader.pk, self.user.pk)
		self.assertEquals(torrent.release.pk, self.release.pk)
		self.assertEquals(torrent.encode_format, modified_data['torrent-encode_format'])
