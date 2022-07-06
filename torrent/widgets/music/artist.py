from django import forms


class ArtistRadioSelect(forms.RadioSelect):
	template_name = 'torrent/music/artist/RadioSelect.html'
	option_template_name = 'torrent/music/artist/RadioSelectOption.html'
