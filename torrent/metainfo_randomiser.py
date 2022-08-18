from typing import IO
import tempfile
import hashlib
import random
import string

from bcoding import bencode


metainfo_template: dict = {
	'announce': 'https://example.com/1234567890/announce',
	'created by': 'qBittorrent v4.1.3',
	'creation date': 1551034473,
	'info': { 
		'length': 5,
		'name': 'single',
		'piece length': 16384,
		'private': 1
	}
}


def create_random_metainfo_file() -> IO[bytes]:
	random_string = ''.join(random.choices(string.ascii_letters, k=1000))
	random_infohash = hashlib.sha1(random_string.encode('utf-8')).digest()
	
	metainfo = metainfo_template.copy()
	metainfo['info']['pieces'] = random_infohash
	
	metainfo_file = tempfile.TemporaryFile()
	metainfo_file.write(bencode(metainfo))
	metainfo_file.seek(0)
	
	return metainfo_file
