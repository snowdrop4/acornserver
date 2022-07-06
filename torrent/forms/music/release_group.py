from django import forms

from torrent.models.music import MusicReleaseGroup


class MusicReleaseGroupForm(forms.ModelForm):
	prefix = 'release_group'
	
	class Meta:
		model = MusicReleaseGroup
		fields = ('name', 'group_type')
