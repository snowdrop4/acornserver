import copy
from typing import Any

from django.test import TestCase, RequestFactory
from django.urls import reverse

import torrent.views.music.release_group as release_group_views
from torrent.models.music import MusicContribution, MusicReleaseGroup
from account.account_randomiser import create_random_user
from torrent.models.music_randomiser import create_random_artist


class TestReleaseGroup(TestCase):
	def setUp(self) -> None:
		self.requestFactory = RequestFactory()
		self.user = create_random_user()
		
		self.artist, _ = create_random_artist()
		
		self.data = {
			'release_group-name': 'ASDF1234',
			'release_group-group_type': MusicReleaseGroup.GroupType.LP
		}
		
		self.contribution_data = {
			'contribution-contribution_type': MusicContribution.ContributionType.COMPOSER
		}
	
	def test_add(self) -> None:
		url = reverse('torrent:music_release_group_add') + '?artist=' + str(self.artist.pk)
		
		request: Any = self.requestFactory.post(url, { **self.data, **self.contribution_data })
		request.user = self.user
		
		release_group_views.add(request)
		release_group = MusicReleaseGroup.objects.get(pk=1)
		
		self.assertEquals(release_group.name,       self.data['release_group-name'])
		self.assertEquals(release_group.group_type, self.data['release_group-group_type'])
	
	def test_edit(self) -> None:
		args = { a.removeprefix('release_group-'): b for (a, b) in self.data.items() }
		release_group = MusicReleaseGroup.objects.create(**args)
		
		url = reverse('torrent:music_release_group_edit', kwargs={ 'pk': release_group.pk })
		
		modified_data = copy.deepcopy(self.data)
		modified_data['release_group-name'] = 'blueberry'
		modified_data['release_group-group_type'] = MusicReleaseGroup.GroupType.EP
		
		request: Any = self.requestFactory.post(url, modified_data)
		request.user = self.user
		
		release_group_views.edit(request, release_group.pk)
		release_group.refresh_from_db()
		
		self.assertEquals(release_group.name,       modified_data['release_group-name'])
		self.assertEquals(release_group.group_type, modified_data['release_group-group_type'])
