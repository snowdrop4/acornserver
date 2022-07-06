import os
from hashlib import sha1
from functools import partial

from django.db import models
from django.utils import timezone

from picklefield.fields import PickledObjectField


# Given a FileField, returns the sha1 digest of that file.
def file_sha1_hexdigest(file: models.FileField) -> str:
	hasher = sha1()
	
	# The file is already open, but we use `open()` to change the mode to make sure that it is set to `rb`.
	# We don't need to close the file at the end of this function as we're only changing the mode, not actually opening it.
	file.open(mode='rb')
	
	# 32768 chunk size is untested for performance
	for chunk in iter(partial(file.read, 32768), b''):
		hasher.update(chunk)
	
	return hasher.hexdigest()


# Returns the path that the uploaded `.torrent` file should be saved to, relative to MEDIA_ROOT (which is set in `acorn/settings.py`).
# `MEDIA_ROOT/torrents/<sha1 hash of the uploaded file>.torrent`
def upload_to(instance, _):
	return os.path.join('torrents', file_sha1_hexdigest(instance.metainfo_file) + '.torrent')


# The reason that this model doesn't specify a mechanism to refer to
# the uploader and downloader is because it is an abstract model.
# 
# As this is an abstract model, you cannot add a ManyToManyField through an intermediary model, as that intermediary model
# would require a foreign key that refers this model, but foreign keys cannot refer to abstract models.
class Torrent(models.Model):
	metainfo_file = models.FileField(upload_to=upload_to)
	
	# `unique=True` does two things here:
	# 
	# 1. Makes it so we can't upload duplicate torrents.
	# 2. Creates a database index on the field, which makes accessing a torrent by infohash just as fast as 
	#    accessing a torrent by primary key, which we will be doing a lot.
	infohash_sha1_hexdigest = models.CharField(max_length=40, unique=True)
	
	torrent_size = models.IntegerField()
	torrent_files = PickledObjectField()
	
	upload_datetime = models.DateTimeField(default=timezone.now)
	
	class Meta:
		abstract = True


class Peer(models.Model):
	peer_id = models.CharField(max_length=20, unique=True)
	peer_ip = models.GenericIPAddressField()
	peer_port = models.IntegerField()
	last_seen = models.DateTimeField(default=timezone.now)
	
	def __str__(self):
		return self.peer_id + " " + self.peer_ip + " " + str(self.peer_port) + " " + str(self.last_seen)
	
	class Meta:
		abstract = True
