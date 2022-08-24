from django import forms


class MusicModelPkForm(forms.Form):
    prefix = "model_pk"

    artist_pk = forms.CharField(widget=forms.HiddenInput(), required=False)


class MusicContributionSelectForm(forms.Form):
    prefix = "contribution_select"

    contribution = forms.ChoiceField(
        choices=(), required=False, label="Select a release group"
    )


class MusicReleaseSelectForm(forms.Form):
    prefix = "release_select"

    release = forms.ChoiceField(choices=(), required=False, label="Select a release")
