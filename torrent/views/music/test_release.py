import copy

from django.urls import reverse
from django.test import TestCase, RequestFactory

from torrent.models.music import MusicRelease
from torrent.models.music_randomiser import random_date, create_random_release_group
from account.account_randomiser import create_random_user
import torrent.views.music.release as release_views


class TestRelease(TestCase):
	def setUp(self):
		self.requestFactory = RequestFactory()
		self.user = create_random_user()
		
		self.release_group, _ = create_random_release_group()
		
		self.date = random_date()
		
		self.data = {
			'release-date': '%d-%02d-%02d' % (self.date.year, self.date.month, self.date.day),
			'release-label': 'apple',
			'release-catalog_number': 'banana',
			'release-release_format': MusicRelease.ReleaseFormat.WEB
		}
		
	def test_add(self):
		url = reverse('torrent:music_release_add') + '?release_group=' + str(self.release_group.pk)
		
		request = self.requestFactory.post(url, self.data)
		request.user = self.user
		
		release_views.add(request)
		release = MusicRelease.objects.get(pk=1)
		
		self.assertEquals(release.date,  self.date)
		self.assertEquals(release.label, self.data['release-label'])
		self.assertEquals(release.catalog_number, self.data['release-catalog_number'])
		self.assertEquals(release.release_format, self.data['release-release_format'])
	
	def test_edit(self):
		args = { a.removeprefix('release-'): b for (a, b) in self.data.items() }
		args['date'] = self.date
		args['release_group'] = self.release_group
		release = MusicRelease.objects.create(**args)
		
		url = reverse('torrent:music_release_edit', kwargs={ 'pk': release.pk })
		
		modified_data = copy.deepcopy(self.data)
		modified_data['release-label'] = 'strawberry'
		
		request = self.requestFactory.post(url, modified_data)
		request.user = self.user
		
		release_views.edit(request, release.pk)
		release.refresh_from_db()
		
		self.assertEquals(release.date,  self.date)
		self.assertEquals(release.label, modified_data['release-label'])
		self.assertEquals(release.catalog_number, modified_data['release-catalog_number'])
		self.assertEquals(release.release_format, modified_data['release-release_format'])
