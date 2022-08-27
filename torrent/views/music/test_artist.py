import copy
from typing import cast

from django.test import TestCase, RequestFactory
from django.urls import reverse

import torrent.views.music.artist as artist_views
from torrent.models.music import MusicArtist
from root.type_annotations import AuthedWSGIRequest
from account.account_randomiser import create_random_user


class TestArtist(TestCase):
    def setUp(self) -> None:
        self.requestFactory = RequestFactory()
        self.user = create_random_user()

        self.data = {
            "artist-name": "Test, Test, and Away!",
            "artist-artist_type": MusicArtist.ArtistType.ARTIST,
        }

    def test_add(self) -> None:
        url = reverse("torrent:music_artist_add")

        request = cast(
            AuthedWSGIRequest,
            self.requestFactory.post(url, self.data)
        )
        request.user = self.user

        artist_views.add(request)
        artist = MusicArtist.objects.get(pk=1)

        self.assertEquals(artist.name, self.data["artist-name"])
        self.assertEquals(artist.artist_type, self.data["artist-artist_type"])

    def test_edit(self) -> None:
        args = {a.removeprefix("artist-"): b for (a, b) in self.data.items()}
        artist = MusicArtist.objects.create(**args)

        url = reverse("torrent:music_artist_edit", kwargs={"pk": artist.pk})

        modified_data = copy.deepcopy(self.data)
        modified_data["artist-name"] = "ooooooooooooooo"
        modified_data["artist-artist_type"] = MusicArtist.ArtistType.PERSON

        request = cast(
            AuthedWSGIRequest,
            self.requestFactory.post(url, modified_data)
        )
        request.user = self.user

        artist_views.edit(request, artist.pk)
        artist.refresh_from_db()

        self.assertEquals(artist.name, modified_data["artist-name"])
        self.assertEquals(artist.artist_type, modified_data["artist-artist_type"])
