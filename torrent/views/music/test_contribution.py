from typing import cast

from django.test import TestCase, RequestFactory
from django.urls import reverse

import torrent.views.music.contribution as contribution_views
from torrent.models.music import MusicContribution
from root.type_annotations import AuthedWSGIRequest
from account.account_randomiser import create_random_user
from torrent.models.music_randomiser import (create_random_artist,
                                             create_random_release_group,)


class TestContribution(TestCase):
    def setUp(self) -> None:
        self.requestFactory = RequestFactory()
        self.user = create_random_user()

        self.artist, _ = create_random_artist()
        self.release_group, _ = create_random_release_group()

    def test_edit(self) -> None:
        contribution = MusicContribution.objects.create(
            artist=self.artist,
            release_group=self.release_group,
            contribution_type=MusicContribution.ContributionType.MAIN,
        )

        url = reverse("torrent:music_contribution_edit", kwargs={"pk": contribution.pk})
        data = {
            "contribution-contribution_type": MusicContribution.ContributionType.GUEST
        }

        request = cast(
            AuthedWSGIRequest,
            self.requestFactory.post(url, data)
        )
        request.user = self.user

        contribution_views.edit(request, contribution.pk)
        contribution.refresh_from_db()

        self.assertEquals(
            contribution.contribution_type, data["contribution-contribution_type"]
        )
