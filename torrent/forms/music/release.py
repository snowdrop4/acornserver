from typing import Any

from django import forms

from torrent.models.music import MusicRelease, MusicReleaseGroup


class MusicReleaseForm(forms.ModelForm):
	prefix = 'release'
	
	class Meta:
		model = MusicRelease
		fields = ('date', 'label', 'catalog_number', 'release_format')


class MusicReleaseFormAdd(forms.ModelForm):
	prefix = 'release'
	
	class Meta:
		model = MusicRelease
		fields = ('release_group', 'date', 'label', 'catalog_number', 'release_format')
	
	def __init__(self, fk: MusicReleaseGroup, *args: Any, **kwargs: Any):
		super().__init__(*args, **kwargs)
		
		self.release_group_fk = fk
		
		# Show the release group specified by `fk` (supplied by the query string) as the default value.
		self.fields['release_group'].choices = [('', fk)]
		# Make the field show as disabled to the user, and make django discard the field even if it *is* POSTed.
		self.fields['release_group'].disabled = True
		# Allow the field to be blank (this is necessary as django discards POST data for fields marked as `disabled`).
		self.fields['release_group'].required = False
	
	# Always return the release group as specified by `fk` for the value for the field.
	def clean_release_group(self) -> MusicReleaseGroup:
		return self.release_group_fk


class MusicReleaseFormEdit(forms.ModelForm):
	prefix = 'release'
	
	class Meta:
		model = MusicRelease
		fields = ('release_group', 'date', 'label', 'catalog_number', 'release_format')
	
	def __init__(self, *args: Any, **kwargs: Any):
		super().__init__(*args, **kwargs)
		
		# Performance: Restrict the choices to the current release group,
		#   rather than every single release group in the database.
		self.fields['release_group'].choices = [('', kwargs['instance'].release_group)]
		self.fields['release_group'].disabled = True
