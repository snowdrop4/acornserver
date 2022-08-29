from django import forms


class MusicAdvancedSearchForm(forms.Form):
    artist_name        = forms.CharField(required=False, label='Artist')
    release_group_name = forms.CharField(required=False, label='Release Group')
