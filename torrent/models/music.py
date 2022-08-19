import datetime
from typing import Any

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib import auth
from django.db.models import QuerySet, signals
from django.dispatch.dispatcher import receiver

from django_countries.fields import CountryField

from torrent.models import torrent


# An artist. E.g., 'fox capture plan'.
class MusicArtist(models.Model):
	class ArtistType(models.TextChoices):
		ARTIST = 'ART', 'Artist'
		CIRCLE = 'CRC', 'Dōjin circle'
		PERSON = 'PER', 'Person'
	
	name = models.CharField(max_length=256)
	formed = models.DateField(null=True, blank=True)
	disbanded = models.DateField(null=True, blank=True)
	country = CountryField(null=True, blank=True)
	artist_type = models.CharField(max_length=3, choices=ArtistType.choices, default=ArtistType.ARTIST)
	
	# User who added the artist to the database
	creator = models.ForeignKey(auth.get_user_model(),
		on_delete=models.SET_NULL, null=True, related_name='created_musicartists'
	)
	
	def get_absolute_url(self) -> str:
		return reverse('torrent:music_artist_view', kwargs={ 'pk': self.pk })
	
	def __str__(self) -> str:
		return self.name
	
	class Meta:
		verbose_name = 'Artist'
		verbose_name_plural = 'Artists'


# A release group is associated with one or more artists and one or more releases.
# 
# E.g., the album 'BUTTERFLY' is associated with the artist
#   'fox capture plan' and one release.
class MusicReleaseGroup(models.Model):
	class GroupType(models.TextChoices):
		LP     = 'LP', 'LP'
		EP     = 'EP', 'EP'
		SINGLE = 'SN', 'Single'
	
	name = models.CharField(max_length=256)
	group_type = models.CharField(max_length=2, choices=GroupType.choices)
	contributors = models.ManyToManyField(MusicArtist, through='MusicContribution', related_name='release_groups')
	
	# User who added the artist to the database
	creator = models.ForeignKey(auth.get_user_model(),
		on_delete=models.SET_NULL, null=True, related_name='created_musicreleasegroups'
	)
	
	def get_earliest_release_date(self) -> datetime.date:
		return min(self.releases.values_list('date', flat=True), default=datetime.date(1, 1, 1))
	
	# Used in the templates `as_table.html` and `as_table_no_header.html`
	#   inside `torrent/templates/torrent/music/release_group/`.
	def get_releases_by_newest_prefetch_related(self) -> QuerySet["MusicRelease"]:
		return self.releases.order_by('-date')\
			.prefetch_related('torrents__downloads')\
			.prefetch_related('torrents__peers')
	
	def get_releases_by_oldest_prefetch_related(self) -> QuerySet["MusicRelease"]:
		return self.releases.order_by('date')\
			.prefetch_related('torrents__downloads')\
			.prefetch_related('torrents__peers')
	
	def get_absolute_url(self) -> str:
		return reverse('torrent:music_release_group_view', kwargs={ 'pk': self.pk })
	
	def __str__(self) -> str:
		return f"{self.group_type} - {self.name}"
	
	class Meta:
		verbose_name = 'Release Group'
		verbose_name_plural = 'Release Groups'


# The specific contribution an artist had to a release group.
class MusicContribution(models.Model):
	class ContributionType(models.TextChoices):
		MAIN       = 'MA', 'Main'
		GUEST      = 'GU', 'Guest'
		COMPOSER   = 'CP', 'Composer'
		CONDUCTOR  = 'CD', 'Conductor'
		DJCOMPILER = 'DJ', 'DJ/Compiler'
		REMIXER    = 'RM', 'Remixer'
		PRODUCER   = 'PR', 'Producer'
		VOCALS     = 'VO', 'Vocals'
	
	artist = models.ForeignKey(MusicArtist, on_delete=models.CASCADE, related_name='contributions')
	release_group = models.ForeignKey(MusicReleaseGroup, on_delete=models.CASCADE, related_name='contributions')
	contribution_type = models.CharField(max_length=2, choices=ContributionType.choices)
	
	# User who added the artist to the database
	creator = models.ForeignKey(auth.get_user_model(),
		on_delete=models.SET_NULL, null=True, related_name='created_musiccontribution'
	)
	
	def __str__(self) -> str:
		return f"'{self.artist.name}' as {self.contribution_type} in '{self.release_group.name}'"
	
	class Meta:
		verbose_name = 'Contribution'
		verbose_name_plural = 'Contributions'
		
		# Make it so that an artist can only have one contribution to a release group.
		unique_together = (('artist', 'release_group'),)


# Prevent MusicContribution objects being deleted if the MusicReleaseGroup
#   object it references does not have any other contributions referencing it.
# 
# This is for the same reason we use `on_delete=models.PROTECT` on the foreign
#   keys for many models. It doesn't make sense to have orphaned torrents or
#   releases or release groups in our database.
@receiver(signals.pre_delete, sender=MusicContribution)
def contribution_pre_delete_signal_handler(
	sender: MusicContribution,
	instance: MusicContribution,
	**kwargs: Any
) -> None:
	if instance.release_group.contributions.count() == 1:
		raise models.ProtectedError(
			'A contribution cannot be deleted if it is the only contribution to a release group.',
			[instance]
		)


# A release is a specific pressing or edition that is distributed
#   through physical or digital mediums.
#
# E.g., the 2015-11-04 release on the CD format on the label 'Playwright'
#   with the catalog number 'PWT18' is tied to the release group for the
#   album 'BUTTERFLY' by the artist 'fox capture plan'.
class MusicRelease(models.Model):
	class ReleaseFormat(models.TextChoices):
		WEB          = 'WB', 'Web'
		COMPACT_DISC = 'CD', 'CD'
		VINYL        = 'VN', 'Vinyl'
	
	release_group = models.ForeignKey(MusicReleaseGroup, on_delete=models.PROTECT, related_name='releases')
	date = models.DateField()
	label = models.CharField(max_length=256)
	catalog_number = models.CharField(max_length=64)
	release_format = models.CharField(max_length=2, choices=ReleaseFormat.choices)
	
	# User who added the artist to the database
	creator = models.ForeignKey(auth.get_user_model(),
		on_delete=models.SET_NULL, null=True, related_name='created_musicreleases'
	)
	
	def get_absolute_url(self) -> str:
		return reverse('torrent:music_release_view', kwargs={ 'pk': self.pk })
	
	def __str__(self) -> str:
		return f"{self.date.strftime('%Y-%m-%d')}\
			, label: '{self.label}'\
			, cat#: '{self.catalog_number}'\
			, format: '{self.release_format}'"
	
	class Meta:
		verbose_name = 'Release'
		verbose_name_plural = 'Releases'


# A torrent file representing a specific encode of a release.
class MusicTorrent(torrent.Torrent):
	class EncodeFormat(models.TextChoices):
		FLAC16 = 'FLC016', 'FLAC / 16bit'
		FLAC24 = 'FLC024', 'FLAC / 24bit'
		MP3VB2 = 'MP3VB2', 'MP3 / V2'
		MP3VB0 = 'MP3VB0', 'MP3 / V0'
		MP3320 = 'MP3320', 'MP3 / 320'
	
	# Use `on_delete=models.PROTECT` instead of `on_delete=models.CASCADE` to 
	#   prevent the object referenced by this foreign key from being deleted.
	# 
	# Torrents are the whole point of this entire exercise, after all, so we
	#   don't want them to be accidentally lost just because someone deleted
	#   a MusicRelease/MusicReleaseGroup/Artist higher up in the heirarchy.
	# 
	# This has the effect of requiring that all child torrents be deleted FIRST,
	#   before any parent release/release group/artist can be deleted.
	release = models.ForeignKey(MusicRelease, on_delete=models.PROTECT, related_name='torrents')
	
	uploader = models.ForeignKey(auth.get_user_model(), on_delete=models.SET_NULL, null=True, related_name='music_uploads')
	downloaders = models.ManyToManyField(auth.get_user_model(), through='MusicTorrentDownload', related_name='downloaded_music_torrents')
	
	encode_format = models.CharField(max_length=6, choices=EncodeFormat.choices)
	
	def get_absolute_url(self) -> str:
		return reverse('torrent:music_torrent_view', kwargs={ 'pk': self.pk })
	
	def get_num_seeders(self) -> int:
		return self.peers.filter(peer_bytes_left__exact=0).count()
	
	def get_num_leechers(self) -> int:
		return self.peers.filter(peer_bytes_left__gt=0).count()
	
	def __str__(self) -> str:
		return f"'{self.encode_format}' encode of release: {self.release}"
	
	class Meta:
		verbose_name = 'MusicTorrent'
		verbose_name_plural = 'MusicTorrents'


class MusicTorrentPeer(torrent.Peer):
	torrent = models.ForeignKey(MusicTorrent, on_delete=models.CASCADE, related_name='peers')
	
	class Meta:
		verbose_name = 'MusicTorrent Peer'
		verbose_name_plural = 'MusicTorrent Peers'


class MusicTorrentDownload(models.Model):
	user = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='music_downloads')
	torrent = models.ForeignKey(MusicTorrent, on_delete=models.CASCADE, related_name='downloads')
	
	download_datetime = models.DateTimeField(default=timezone.now)
	
	class Meta:
		unique_together = (('user', 'torrent'),)
		verbose_name = 'MusicTorrent Download'
		verbose_name_plural = 'MusicTorrent Downloads'
