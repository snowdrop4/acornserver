from django import forms

from torrent.models.music import MusicArtist


class MusicArtistForm(forms.ModelForm):
	prefix = 'artist'
	
	class Meta:
		model = MusicArtist
		fields = ('name',)


class MusicArtistFormAdd(forms.ModelForm):
	prefix = 'artist'
	
	class Meta:
		model = MusicArtist
		fields = ('name', 'formed', 'disbanded', 'country', 'artist_type')


class MusicArtistFormEdit(forms.ModelForm):
	prefix = 'artist'
	
	class Meta:
		model = MusicArtist
		fields = ('name', 'formed', 'disbanded', 'country', 'artist_type')
