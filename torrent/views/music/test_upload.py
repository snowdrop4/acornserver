import os
from typing import Any

from django.conf import settings
from django.test import TestCase, RequestFactory
from django.urls import reverse

from torrent.models.music import (MusicArtist, MusicRelease, MusicTorrent,
                                  MusicContribution, MusicReleaseGroup,)
from account.account_randomiser import create_random_user
from torrent.views.music.upload import upload
from torrent.models.music_randomiser import (create_random_artist,
                                             create_random_release,
                                             create_random_contribution,
                                             create_random_release_group,)


class TestUpload(TestCase):
    def setUp(self) -> None:
        self.requestFactory = RequestFactory()

        # We need a user, since the view obviously expects a user to be logged in.
        self.user = create_random_user()

        # The URL of our form.
        self.url = reverse("torrent:music_upload")

        # The file handler for the torrent file.
        torrent_path = os.path.join(
            settings.BASE_DIR, "test", "metainfo-v1-multi.torrent"
        )
        self.torrent_file = open(torrent_path, "rb")

        #
        # Generic data that can be reused in each of the tests as POST data.
        #
        self.artist_data = {
            "artist-name": "Test, Test, and Away!",
        }

        self.release_group_data = {
            "release_group-name": "9000 Tests and an Album ain't one",
            "release_group-group_type": MusicReleaseGroup.GroupType.LP,
        }

        self.contribution_data = {
            "contribution-contribution_type": MusicContribution.ContributionType.MAIN
        }

        self.release_data = {
            "release-date": "2001-02-03",
            "release-label": "Django Records",
            "release-catalog_number": "DR-0001CD",
            "release-release_format": MusicRelease.ReleaseFormat.COMPACT_DISC,
        }

        self.torrent_data = {
            "torrent-metainfo_file": self.torrent_file,
            "torrent-encode_format": MusicTorrent.EncodeFormat.FLAC16,
        }

    def tearDown(self) -> None:
        self.torrent_file.close()

    def check_artist(self, artist: MusicArtist, data: dict) -> None:
        self.assertEquals(artist.name, data["artist-name"])

    def check_release_group(self, release_group: MusicReleaseGroup, data: dict) -> None:
        self.assertEquals(release_group.name, data["release_group-name"])
        self.assertEquals(release_group.group_type, data["release_group-group_type"])

    def check_contribution(self, contribution: MusicContribution, data: dict) -> None:
        self.assertEquals(
            contribution.contribution_type, data["contribution-contribution_type"]
        )

    def check_release(self, release: MusicRelease, data: dict) -> None:
        self.assertEquals(release.date.strftime("%Y-%m-%d"), data["release-date"])
        self.assertEquals(release.label, data["release-label"])
        self.assertEquals(release.catalog_number, data["release-catalog_number"])
        self.assertEquals(release.release_format, data["release-release_format"])

    def check_torrent(self, torrent: MusicTorrent, data: dict) -> None:
        self.assertEquals(torrent.uploader, self.user)
        self.assertEquals(torrent.encode_format, data["torrent-encode_format"])

    def check_relations(
        self,
        artist: MusicArtist,
        release_group: MusicReleaseGroup,
        contribution: MusicContribution,
        release: MusicRelease,
        torrent: MusicTorrent,
    ) -> None:
        self.assertEquals(contribution.artist, artist)
        self.assertEquals(contribution.release_group, release_group)
        self.assertEquals(release.release_group, release_group)
        self.assertEquals(torrent.release, release)

    def check_everything(self, **kwargs: Any) -> None:
        ao, ad = kwargs.get("artist")
        self.check_artist(ao, ad)

        go, gd = kwargs.get("release_group")
        self.check_release_group(go, gd)

        co, cd = kwargs.get("contribution")
        self.check_contribution(co, cd)

        ro, rd = kwargs.get("release")
        self.check_release(ro, rd)

        to, td = kwargs.get("torrent")
        self.check_torrent(to, td)

        self.check_relations(ao, go, co, ro, to)

    # Test the basic form without autocomplete or autofill.
    def test_from_new(self) -> None:
        data = {
            **self.artist_data,
            **self.release_group_data,
            **self.contribution_data,
            **self.release_data,
            **self.torrent_data,
        }

        request: Any = self.requestFactory.post(self.url, data, format="multipart")
        request.user = self.user

        upload(request)

        artist = MusicArtist.objects.get(pk=1)
        release_group = MusicReleaseGroup.objects.get(pk=1)
        contribution = MusicContribution.objects.get(pk=1)
        release = MusicRelease.objects.get(pk=1)
        torrent = MusicTorrent.objects.get(pk=1)

        self.check_everything(
            artist=(artist, data),
            release_group=(release_group, data),
            contribution=(contribution, data),
            release=(release, data),
            torrent=(torrent, data),
        )

    # Test the form with the artist autocompleted.
    def test_autocompleted_artist(self) -> None:
        # Create a throwaway artist to increment the PK counter,
        # to additionally test that the right PK is going through.
        (_, _)                = create_random_artist()
        (artist, artist_data) = create_random_artist()

        data = {
            **{"model_pk-artist_pk": "2",},
            **self.release_group_data,
            **self.contribution_data,
            **self.release_data,
            **self.torrent_data,
        }

        request: Any = self.requestFactory.post(self.url, data, format="multipart")
        request.user = self.user

        upload(request)

        release_group = MusicReleaseGroup.objects.get(pk=1)
        contribution = MusicContribution.objects.get(pk=1)
        release = MusicRelease.objects.get(pk=1)
        torrent = MusicTorrent.objects.get(pk=1)

        self.check_everything(
            artist=(artist, artist_data),
            release_group=(release_group, data),
            contribution=(contribution, data),
            release=(release, data),
            torrent=(torrent, data),
        )

    # Test the form with the artist autocompleted and the contribution selected
    # from an autofill candidate.
    def test_autofilled_contribution(self) -> None:
        # Create a throwaway artist to increment the PK counter, to additionally
        # test that the right PK is going through.
        (_, _) = create_random_artist()
        (artist, artist_data) = create_random_artist()

        # Do the same for release_group, this time with two throwaways so we
        # don't get overlapping PKs with artist.
        (_, _) = create_random_release_group()
        (_, _) = create_random_release_group()
        (release_group, release_group_data) = create_random_release_group()

        (contribution, contribution_data) = create_random_contribution(
            artist, release_group
        )

        data = {
            **{
                "model_pk-artist_pk": "2",
            },
            **{
                "contribution_select-contribution": "1",
            },  # The upload view deduces the release_group pk from the contribution pk
            **self.release_data,
            **self.torrent_data,
        }

        request: Any = self.requestFactory.post(self.url, data, format="multipart")
        request.user = self.user

        upload(request)

        release = MusicRelease.objects.get(pk=1)
        torrent = MusicTorrent.objects.get(pk=1)

        self.check_everything(
            artist=(artist, artist_data),
            release_group=(release_group, release_group_data),
            contribution=(contribution, contribution_data),
            release=(release, data),
            torrent=(torrent, data),
        )

    # Test the form with the artist autocompleted and the contribution and
    # release selected from the autofill candidates.
    def test_autofilled_release(self) -> None:
        # Create a throwaway artist to increment the PK counter, to additionally
        # test that the right PK is going through.
        (_, _) = create_random_artist()
        (artist, artist_data) = create_random_artist()

        # Do the same for release_group, this time with two throwaways so we
        # don't get overlapping PKs with artist.
        (_, _) = create_random_release_group()
        (_, _) = create_random_release_group()
        (release_group, release_group_data) = create_random_release_group()

        (contribution, contribution_data) = create_random_contribution(
            artist, release_group
        )

        # And again for release.
        (_, _) = create_random_release(release_group)
        (_, _) = create_random_release(release_group)
        (_, _) = create_random_release(release_group)
        (release, release_data) = create_random_release(release_group)

        data = {
            **{"model_pk-artist_pk": "2",},
            # The upload view deduces the release_group pk from the contribution pk
            **{"contribution_select-contribution": "1",},
            **{"release_select-release": "4",},
            **self.torrent_data,
        }

        request: Any = self.requestFactory.post(self.url, data, format="multipart")
        request.user = self.user

        upload(request)

        torrent = MusicTorrent.objects.get(pk=1)

        self.check_everything(
            artist=(artist, artist_data),
            release_group=(release_group, release_group_data),
            contribution=(contribution, contribution_data),
            release=(release, release_data),
            torrent=(torrent, data),
        )

    # Test the form with the artist set by GET parameter.
    def test_get_parameter_artist(self) -> None:
        (_, _) = create_random_artist()
        (artist, artist_data) = create_random_artist()

        data = {
            **self.release_group_data,
            **self.contribution_data,
            **self.release_data,
            **self.torrent_data,
        }

        request: Any = self.requestFactory.post(
            self.url + "?artist=2", data, format="multipart"
        )
        request.user = self.user

        upload(request)

        release_group = MusicReleaseGroup.objects.get(pk=1)
        contribution = MusicContribution.objects.get(pk=1)
        release = MusicRelease.objects.get(pk=1)
        torrent = MusicTorrent.objects.get(pk=1)

        self.check_everything(
            artist=(artist, artist_data),
            release_group=(release_group, data),
            contribution=(contribution, data),
            release=(release, data),
            torrent=(torrent, data),
        )

    # Test the form with the contribution set by GET parameter.
    def test_get_parameter_contribution(self) -> None:
        # Create a throwaway artist to increment the PK counter, to additionally
        # test that the right PK is going through.
        (_, _) = create_random_artist()
        (artist, artist_data) = create_random_artist()

        # Do the same for release_group, this time with two throwaways so we
        # don't get overlapping PKs with artist.
        (_, _) = create_random_release_group()
        (_, _) = create_random_release_group()
        (release_group, release_group_data) = create_random_release_group()

        (contribution, contribution_data) = create_random_contribution(
            artist, release_group
        )

        data = {**self.release_data, **self.torrent_data}

        request: Any = self.requestFactory.post(
            self.url + "?contribution=1", data, format="multipart"
        )
        request.user = self.user

        upload(request)

        release = MusicRelease.objects.get(pk=1)
        torrent = MusicTorrent.objects.get(pk=1)

        self.check_everything(
            artist=(artist, artist_data),
            release_group=(release_group, release_group_data),
            contribution=(contribution, contribution_data),
            release=(release, data),
            torrent=(torrent, data),
        )

    # Test the form with the contribution set by GET parameter.
    def test_get_parameter_release_group(self) -> None:
        # Create a throwaway artist to increment the PK counter, to additionally
        # test that the right PK is going through.
        (_, _) = create_random_artist()
        (artist, artist_data) = create_random_artist()

        # Do the same for release_group, this time with two throwaways so we
        # don't get overlapping PKs with artist.
        (_, _) = create_random_release_group()
        (_, _) = create_random_release_group()
        (release_group, release_group_data) = create_random_release_group()

        (contribution, contribution_data) = create_random_contribution(
            artist, release_group
        )

        data = {**self.release_data, **self.torrent_data}

        request: Any = self.requestFactory.post(
            self.url + "?release_group=3", data, format="multipart"
        )
        request.user = self.user

        upload(request)

        release = MusicRelease.objects.get(pk=1)
        torrent = MusicTorrent.objects.get(pk=1)

        self.check_everything(
            artist=(artist, artist_data),
            release_group=(release_group, release_group_data),
            contribution=(contribution, contribution_data),
            release=(release, data),
            torrent=(torrent, data),
        )

    # Test the form with the contribution set by GET parameter.
    def test_get_parameter_release(self) -> None:
        # Create a throwaway artist to increment the PK counter, to additionally
        # test that the right PK is going through.
        (_, _) = create_random_artist()
        (artist, artist_data) = create_random_artist()

        # Do the same for release_group, this time with two throwaways so we
        # don't get overlapping PKs with artist.
        (_, _) = create_random_release_group()
        (_, _) = create_random_release_group()
        (release_group, release_group_data) = create_random_release_group()

        (contribution, contribution_data) = create_random_contribution(
            artist, release_group
        )

        # And again for release.
        (_, _) = create_random_release(release_group)
        (_, _) = create_random_release(release_group)
        (_, _) = create_random_release(release_group)
        (release, release_data) = create_random_release(release_group)

        data = {**self.torrent_data}

        request: Any = self.requestFactory.post(
            self.url + "?release=4", data, format="multipart"
        )
        request.user = self.user

        upload(request)

        torrent = MusicTorrent.objects.get(pk=1)

        self.check_everything(
            artist=(artist, artist_data),
            release_group=(release_group, release_group_data),
            contribution=(contribution, contribution_data),
            release=(release, release_data),
            torrent=(torrent, data),
        )
