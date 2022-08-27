from typing import Any, cast

from django import forms
from django.forms import ChoiceField
from django.db.models import QuerySet

from torrent.models.music import MusicArtist, MusicContribution
from torrent.widgets.music.artist import ArtistRadioSelect


class MusicContributionForm(forms.ModelForm):
    prefix = "contribution"

    class Meta:
        model = MusicContribution
        fields = ("contribution_type",)


class MusicContributionFormWithArtistFK(forms.ModelForm):
    prefix = "contribution"

    class Meta:
        model = MusicContribution
        fields = (
            "artist",
            "contribution_type",
        )

    def __init__(self, fk: MusicArtist, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.artist_fk = fk

        artist_field = cast(ChoiceField, self.fields["artist"])
        # Show the artist specified by `fk` (supplied by the query string)
        # as the default value.
        artist_field.choices = [("", fk)]
        # Make the field show as disabled to the user, and make django discard
        # the field even if it *is* POSTed.
        artist_field.disabled = True
        # Allow the field to be blank (this is necessary as django discards
        # POST data for fields marked as `disabled`).
        artist_field.required = False

    # Always return the artist as specified by `fk` for the value for the field.
    def clean_artist(self) -> MusicArtist:
        return self.artist_fk


class MusicContributionFormAdd(forms.ModelForm):
    prefix = "contribution"

    class Meta:
        model = MusicContribution
        fields = (
            "artist",
            "contribution_type",
        )
        widgets = {"artist": ArtistRadioSelect}

    def __init__(self, queryset: list, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        # Instead of setting `self.fields['artist'].queryset` and letting
        # django automatically fill in the choices, we need to manually
        # fill in `self.fields['artist'].choices` ourselves, as the queryset
        # is sliced (since it is from a `Paginator`).
        #
        # `self.fields['artist'].queryset` cannot be set to a sliced queryset,
        # as django filters the queryset as part of the validation step,
        # but sliced querysets cannot be filtered, as the docs explain:
        #
        #   "Also note that even though slicing an unevaluated QuerySet
        #    returns another unevaluated QuerySet, modifying it further
        #    (e.g., adding more filters, or modifying ordering) is not allowed,
        #    since that does not translate well into SQL and it would not
        #    have a clear meaning either."
        #
        # So we need to bypass this filtering stage by directly setting the
        # choices ourselves.
        artist_field = cast(ChoiceField, self.fields["artist"])
        artist_field.choices = [(a.pk, a.name) for a in queryset]


class MusicContributionFormArtistSearch(forms.Form):
    artist_name = forms.CharField(required=False, label="Artist")
