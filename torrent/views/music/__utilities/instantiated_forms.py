# This is used in `torrent/views/music/upload.py` to simplify the process of
# using multiple forms that must all correspond to each other and that may or
# may not be pre-filled and uneditable.

from abc import abstractmethod
from typing import cast

from django import forms
from django.db import models
from django.http import Http404
from django.forms import ModelChoiceField
from django.shortcuts import get_object_or_404

from torrent.forms.music import upload
from torrent.models.music import MusicArtist, MusicContribution, MusicReleaseGroup
from root.type_annotations import AuthedHttpRequest


# Wrapper around the basic python dictionary object that accepts values of
# type string and converts them to type int.
#
# If the conversion from string to integer fails, it throws a 404.
class PkProvider:
    def __init__(self, get_parameters: dict[str, str]):
        self.pks: dict[str, int] = {}

        for (k, vs) in get_parameters.items():
            for v in vs:
                self.__setitem__(k, v)

    def __setitem__(self, pk_name: str, pk_value: str | int) -> None:
        try:
            self.pks[pk_name] = int(pk_value)
        except ValueError:
            # TODO: Can't just return a `HttpResponseBadRequest` because we
            # aren't actually in a view.
            #
            # Only way to signal an error is use an exception here, but Http404
            # is technically wrong.
            raise Http404("The GET parameter '" + pk_name + "' must be an integer")

    def __getitem__(self, pk_name: str) -> int:
        return self.pks[pk_name]

    def __contains__(self, pk_name: str) -> bool:
        return pk_name in self.pks


# The value for the HTML ID for each field when rendered in the template.
def auto_id() -> str:
    return "upload-%s"


class BaseForm:
    def __init__(
        self,
        pk_provider: PkProvider,
        pk_name: str,
        form_class: type[forms.Form] | type[forms.ModelForm]
    ):
        self.pk_provider = pk_provider
        self.pk_name = pk_name

        self.form_class: type[forms.Form] | type[forms.ModelForm] = form_class
        self.form: forms.Form | forms.ModelForm

        self.is_valid_override = False

    def instantiate(self, request: AuthedHttpRequest) -> None:
        # If the request method is a POST, construct a form and object
        # based on the POSTed values.
        if request.method == "POST":
            self.instantiate_post(request)
        # Else, just create an empty form.
        else:
            self.instantiate_empty()

    def instantiate_post(self, request: AuthedHttpRequest) -> None:
        self.form = self.form_class(request.POST, auto_id=auto_id())

    def instantiate_empty(self) -> None:
        self.form = self.form_class(auto_id=auto_id())

    # For `is_valid()` to return true, a form needs to be BOTH bound and valid.
    # For a form to be considered bound by django, it must be constructed using
    # POST data (given as the first position argument to the constructor).
    #
    # If we construct a form with a primary key instead (by setting the named
    # argument `instance` in the constructor), django will not consider the
    # form bound.
    #
    # This is a problem, because for our purposes the form should still be
    # considered "valid" even though it wasn't "bound".
    #
    # By overriding the `is_valid()` method, and then setting `is_valid_override`
    # to True somewhere in our code at a later stage, we can create a form that
    # will pretend to be valid even though it was constructed with a primary key
    # and not POST data.
    def is_valid(self) -> bool:
        return self.is_valid_override or self.form.is_valid()

    def disable_all_fields(self) -> None:
        for (name, field) in self.form.fields.items():
            field.disabled = True


# Holds a hidden input field for an artist pk, which might be filled by
# javascript if the user autocompletes an artist.
class MusicModelPkForm(BaseForm):
    def __init__(self, pk_provider: PkProvider):
        super().__init__(pk_provider, "model_pk", upload.MusicModelPkForm)

    def instantiate_post(self, request: AuthedHttpRequest) -> None:
        super().instantiate_post(request)

        if self.form.is_valid():
            artist_pk_str = self.form.cleaned_data.get("artist_pk", "")

            if artist_pk_str != "":
                self.pk_provider["artist"] = artist_pk_str


# Partial class that extends BaseForm to let the form be instantiated from a PK
# provided by `pk_provider`.
#
# Any class inheriting this must implement `instantiate_pk`.
class MusicPkForm(BaseForm):
    @abstractmethod
    def instantiate_pk(self, pk: int) -> None:
        raise NotImplementedError

    def instantiate(self, request: AuthedHttpRequest) -> None:
        if self.pk_name in self.pk_provider:
            self.instantiate_pk(self.pk_provider[self.pk_name])
            self.is_valid_override = True
        else:
            super().instantiate(request)


# Class to group up a form based on a model with an object based on that same model.
class MusicObjectForm(MusicPkForm):
    def __init__(
        self,
        pk_provider: PkProvider,
        pk_name: str,
        form_class: type[forms.ModelForm],
        object_class: type[models.Model],
    ):
        super().__init__(pk_provider, pk_name, form_class)

        self.form_class: type[forms.ModelForm]
        self.form: forms.ModelForm

        self.object_class: type[models.Model] = object_class
        self.object: models.Model

        # Whether the form was constructed from a primary key (used to tell us
        # if we need to save the object or not)
        self.from_pk = False

    def instantiate_pk(self, pk: int) -> None:
        self.object = get_object_or_404(self.object_class, pk=pk)
        self.form = self.form_class(instance=self.object, auto_id=auto_id())
        self.disable_all_fields()
        self.from_pk = True

    def instantiate_post(self, request: AuthedHttpRequest) -> None:
        super().instantiate_post(request)

        if self.form.is_valid():
            self.object = self.form.save(commit=False)


class MusicContributionSelectForm(MusicPkForm):
    def __init__(self, pk_provider: PkProvider):
        super().__init__(
            pk_provider, "contribution", upload.MusicContributionSelectForm
        )

        self.object: models.Model | None = None

    def populate_choices(self) -> None:
        contribution_field = cast(ModelChoiceField, self.form.fields["contribution"])
        choices: list[tuple[str, str]] = [("", "---------")]

        if "artist" in self.pk_provider:
            artist = get_object_or_404(MusicArtist, pk=self.pk_provider["artist"])

            for i in artist.contributions.all():
                choices.append(
                    (str(i.pk), f"{i.get_contribution_type_display()} - {i.release_group}")
                )

            contribution_field.choices = choices

            if "contribution" in self.pk_provider:
                initial = cast(dict[str, str], self.form.initial)
                initial["contribution"] = str(self.pk_provider["contribution"])
        else:
            contribution_field.choices = choices
            self.disable_all_fields()

    def instantiate_pk(self, pk: int) -> None:
        super().instantiate_empty()

        self.object = get_object_or_404(MusicContribution, pk=pk)
        self.pk_provider["artist"] = self.object.artist.pk
        self.pk_provider["release_group"] = self.object.release_group.pk

        self.populate_choices()

    def instantiate_post(self, request: AuthedHttpRequest) -> None:
        super().instantiate_post(request)
        self.populate_choices()

        if self.form.is_valid():
            pk_str = self.form.cleaned_data.get("contribution", "")

            # Do nothing if the key doesn't exist, or its value is just ''.
            # (i.e., the blank '---------' option with value '' was selected).
            if pk_str != "":
                self.pk_provider["contribution"] = pk_str

                self.object = get_object_or_404(
                    MusicContribution, pk=self.pk_provider["contribution"]
                )
                self.pk_provider["artist"] = self.object.artist.pk
                self.pk_provider["release_group"] = self.object.release_group.pk

    def instantiate_empty(self) -> None:
        super().instantiate_empty()
        self.populate_choices()


class MusicReleaseSelectForm(MusicPkForm):
    def __init__(self, pk_provider: PkProvider):
        super().__init__(pk_provider, "release", upload.MusicReleaseSelectForm)

        self.object = None

    def populate_choices(self) -> None:
        release_field = cast(ModelChoiceField, self.form.fields["release"])
        choices: list[tuple[str, str]] = [("", "---------")]

        if "release_group" in self.pk_provider:
            release_group = get_object_or_404(
                MusicReleaseGroup, pk=self.pk_provider["release_group"]
            )

            for i in release_group.releases.all():
                choices.append((str(i.pk), str(i)))

            release_field.choices = choices

            if "release" in self.pk_provider:
                initial = cast(dict[str, str], self.form.initial)
                initial["release"] = str(self.pk_provider["release"])
        else:
            release_field.choices = choices
            self.disable_all_fields()

    def instantiate_pk(self, pk: int) -> None:
        super().instantiate_empty()
        self.populate_choices()

    def instantiate_post(self, request: AuthedHttpRequest) -> None:
        super().instantiate_post(request)
        self.populate_choices()

        if self.form.is_valid():
            pk_str = self.form.cleaned_data.get("release", "")

            # Do nothing if the key doesn't exist, or its value is just ''.
            # (i.e., the blank '---------' option with value '' was selected).
            if pk_str != "":
                self.pk_provider["release"] = pk_str

    def instantiate_empty(self) -> None:
        super().instantiate_empty()
        self.populate_choices()
