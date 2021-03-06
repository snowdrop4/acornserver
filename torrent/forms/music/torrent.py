from bcoding import bdecode

from django import forms

from torrent.models.music import MusicTorrent
from torrent.metainfo import validate_v1_metainfo


def clean_metainfo_file(self):
	metainfo = self.cleaned_data['metainfo_file']
	exception = forms.ValidationError("Invalid torrent file.")
	
	try:
		metainfo.seek(0)
		metainfo_decoded = bdecode(metainfo)
	except TypeError:
		raise exception
	else:
		if validate_v1_metainfo(metainfo_decoded) is False:
			raise exception
	
	return metainfo


class MusicTorrentForm(forms.ModelForm):
	prefix = 'torrent'
	
	class Meta:
		model = MusicTorrent
		fields = ('metainfo_file', 'encode_format')
	
	def clean_metainfo_file(self):
		return clean_metainfo_file(self)


class MusicTorrentFormAdd(forms.ModelForm):
	prefix = 'torrent'
	
	class Meta:
		model = MusicTorrent
		fields = ('release', 'metainfo_file', 'encode_format')
	
	def __init__(self, fk, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		# Set the default value for the `release` form field to the `release` specified by `fk`.
		# 
		# Additionally, restrict the possible values for the `release` form field
		#   to releases belonging to the same release group as the release specified by `fk`.
		self.fields['release'].queryset = fk.release_group.releases
		self.fields['release'].initial = fk
	
	def clean_metainfo_file(self):
		return clean_metainfo_file(self)


# Unlike most other edit forms where it is technically optional,
#   this form requires `instance` (the PK of a torrent) as a kwarg.
class MusicTorrentFormEdit(forms.ModelForm):
	prefix = 'torrent'
	
	class Meta:
		model = MusicTorrent
		fields = ('release', 'metainfo_file', 'encode_format')
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		# If `instance` is supplied as a kwarg, restrict the possible values for the `release` form field
		#   to releases belonging to the same release group as the current release.
		if 'instance' in kwargs:
			self.fields['release'].queryset = kwargs['instance'].release.release_group.releases
		# Otherwise, throw an error since we can't construct the form. If we don't narrow down the possible values
		#   for `release` then django will default to displaying every single release in the database which is nonsense.
		else:
			raise TypeError('MusicTorrentFormEdit() missing required keyword argument: \'instance\'')
	
	def clean_metainfo_file(self):
		return clean_metainfo_file(self)
