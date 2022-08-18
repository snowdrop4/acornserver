import os
from functools import reduce

from django.conf import settings
from django.test import TestCase

from bcoding import bdecode

import torrent.metainfo as mi


class TestMetainfo(TestCase):
	def setUp(self) -> None:
		multiTorrentPath = os.path.join(settings.BASE_DIR, 'test', 'metainfo-v1-multi.torrent')
		with open(multiTorrentPath, 'rb') as f:
			self.multiTorrent = bdecode(f)
		
		singleTorrentPath = os.path.join(settings.BASE_DIR, 'test', 'metainfo-v1-single.torrent')
		with open(singleTorrentPath, 'rb') as f:
			self.singleTorrent = bdecode(f)
	
	def test_get_announce(self) -> None:
		announce = 'https://example.com/1234567890/announce'
		mt = mi.get_announce(self.multiTorrent)
		st = mi.get_announce(self.singleTorrent)
		
		self.assertEquals(mt, announce)
		self.assertEquals(st, announce)
	
	def test_get_name(self) -> None:
		mt = mi.get_name(self.multiTorrent)
		st = mi.get_name(self.singleTorrent)
		
		self.assertEquals(mt, 'multi')
		self.assertEquals(st, 'single')
	
	def test_get_piece_length(self) -> None:
		mt = mi.get_piece_length(self.multiTorrent)
		st = mi.get_piece_length(self.singleTorrent)
		
		self.assertEquals(mt, 16384)
		self.assertEquals(st, 16384)
	
	def test_get_pieces(self) -> None:
		mt = mi.get_pieces(self.multiTorrent)
		st = mi.get_pieces(self.singleTorrent)
		
		f = lambda x, y: x and (len(y) == 20)
		
		self.assertEquals(reduce(f, mt, True), True)
		self.assertEquals(reduce(f, st, True), True)
	
	# get_length is only defined for single file torrents
	def test_get_length(self) -> None:
		st = mi.get_length(self.singleTorrent)
		
		self.assertEquals(st, 5)
	
	# get_files is only defined for multi file torrents
	def test_get_files(self) -> None:
		mt = mi.get_files(self.multiTorrent)
		
		self.assertEquals(len(mt), 2)
		
		(l0, p0) = mt[0]
		(l1, p1) = mt[1]
		
		self.assertEquals(l0, 5)
		self.assertEquals(p0, ['multi1'])
		
		self.assertEquals(l1, 5)
		self.assertEquals(p1, ['multi2'])
	
	def test_get_infohash_sha1_hexdigest(self) -> None:
		mt = mi.get_infohash_sha1_hexdigest(self.multiTorrent)
		st = mi.get_infohash_sha1_hexdigest(self.singleTorrent)
		
		self.assertEquals(mt, '2fc72769f06490d2ed07f8dead87da26a102d189')
		self.assertEquals(st, '88d5e81dcecfb78feb6e3361f08571d037e1f045')
