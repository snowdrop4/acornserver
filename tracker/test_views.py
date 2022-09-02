import os
from typing import cast

from django.conf import settings
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from bcoding import bdecode, bencode

from torrent import metainfo
from torrent.models.music import MusicTorrent, MusicTorrentPeer
from account.account_randomiser import create_random_user
from torrent.models.music_randomiser import (
    create_random_artist,
    create_random_release,
    create_random_contribution,
    create_random_release_group,
)

from .views import bittorrent_announce


class TestAnnounce(TestCase):
    def setUp(self) -> None:
        self.requestFactory = RequestFactory()
        self.user = create_random_user()

        # Read the example torrent file and get the relevant information from it
        torrent_path = os.path.join(
            settings.BASE_DIR, "test", "metainfo-v1-multi.torrent"
        )
        self.torrent_file = open(torrent_path, "rb")
        self.metainfo  = bdecode(self.torrent_file)
        infohash_bytes = metainfo.get_infohash_sha1_digest(self.metainfo)
        infohash_hex   = metainfo.get_infohash_sha1_hexdigest(self.metainfo)
        torrent_size   = metainfo.get_torrent_size(self.metainfo)
        torrent_files  = metainfo.get_torrent_file_listing(self.metainfo)

        # Construct our database objects
        (self.artist,        _) = create_random_artist()
        (self.release_group, _) = create_random_release_group()
        (self.contribution,  _) = create_random_contribution(
            self.artist, self.release_group
        )
        (self.release, _) = create_random_release(self.release_group)
        self.torrent = MusicTorrent.objects.create(
            release=self.release,
            uploader=self.user,
            infohash_sha1_hexdigest=infohash_hex,
            torrent_size=torrent_size,
            torrent_files=torrent_files,
        )

        # Build our request GET parameters
        self.data = {
            "info_hash": infohash_bytes,
            "peer_id": "abcdefghijklmnopqrst",
            "ip": "127.0.0.1",
            "port": 4096,
            "uploaded": 1337,
            "downloaded": 69,
            "left": 420,
            "event": "empty",
        }

    def tearDown(self) -> None:
        self.torrent_file.close()

    # check to see if the upload/download totals are updated in the User object,
    # and that the MusicTorrentPeer object is created correctly
    def test_announce(self) -> None:
        url = reverse(
            "tracker:bittorrent_announce",
            kwargs={
                "passkey": self.user.passkey.key,
                "torrent_type": "music",
            },
        )

        request = self.requestFactory.get(url, self.data)

        now = timezone.now()

        bittorrent_announce(request, self.user.passkey.key, "music")

        self.user.refresh_from_db()
        peer = cast(MusicTorrentPeer, MusicTorrentPeer.objects.first())

        self.assertEqual(self.user.uploaded, self.data["uploaded"])
        self.assertEqual(self.user.downloaded, self.data["downloaded"])

        self.assertEqual(peer.torrent, self.torrent)
        self.assertEqual(peer.peer_id, self.data["peer_id"])
        self.assertEqual(peer.peer_ip, self.data["ip"])
        self.assertEqual(peer.peer_port, self.data["port"])
        self.assertEqual(peer.peer_bytes_left, self.data["left"])

        self.assertTrue((peer.last_seen - now).seconds < 2)

    # Check to see if an announce with an invalid passkey is rejected
    def test_invalid_passkey(self) -> None:
        url = reverse(
            "tracker:bittorrent_announce",
            kwargs={
                "passkey": "asdf1234",
                "torrent_type": "music",
            },
        )

        request = self.requestFactory.get(url, self.data)

        response = bittorrent_announce(request, "asdf1234", "music")

        self.assertEqual(
            response.content, bencode({"failure reason": "invalid passkey"})
        )
