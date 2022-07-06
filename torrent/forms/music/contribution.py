from django import forms

from torrent.models.music import MusicContribution
from torrent.widgets.music.artist import ArtistRadioSelect


class MusicContributionForm(forms.ModelForm):
	prefix = 'contribution'
	
	class Meta:
		model = MusicContribution
		fields = ('contribution_type',)


class MusicContributionFormWithArtistFK(forms.ModelForm):
	prefix = 'contribution'
	
	class Meta:
		model = MusicContribution
		fields = ('artist', 'contribution_type',)
	
	def __init__(self, artist_fk, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.artist_fk = artist_fk
		
		# Show the artist specified by `artist_fk` (supplied by the query string) as the default value.
		self.fields['artist'].choices = [('', artist_fk)]
		# Make the field show as disabled to the user, and make django discard the field even if it *is* POSTed.
		self.fields['artist'].disabled = True
		# Allow the field to be blank (this is necessary as django discards POST data for fields marked as `disabled`).
		self.fields['artist'].required = False
	
	# Always return the artist as specified by `artist_fk` for the value for the field.
	def clean_artist(self):
		return self.artist_fk


class MusicContributionFormAdd(forms.ModelForm):
	prefix = 'contribution'
	
	class Meta:
		model = MusicContribution
		fields = ('artist', 'contribution_type',)
		widgets = { 'artist': ArtistRadioSelect }
		
	def __init__(self, queryset, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		# Manually fill in `choices` here, rather than let django automatically
		#   infer the values by setting `queryset`, as the queryset
		#   will be sliced (since it is from a `Paginator`).
		# 
		# Django filters the queryset as part of the validation step,
		#   but sliced querysets cannot be filtered, as the docs explain:
		# 
		#   "Also note that even though slicing an unevaluated QuerySet
		#    returns another unevaluated QuerySet, modifying it further
		#    (e.g., adding more filters, or modifying ordering) is not allowed,
		#    since that does not translate well into SQL and it would not
		#    have a clear meaning either."
		self.fields['artist'].choices = [(a.pk, a.name) for a in queryset]


class MusicContributionFormArtistSearch(forms.Form):
	artist_name = forms.CharField(required=False, label='Artist')
