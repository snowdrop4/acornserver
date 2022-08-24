from typing import Any

from django.db import Error, transaction
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from bcoding import bdecode

from root import messages, renderers
from torrent.metainfo import (get_torrent_size, get_torrent_file_listing,
                              get_infohash_sha1_hexdigest,)
from torrent.models.music import (MusicArtist, MusicRelease, MusicTorrent,
                                  MusicContribution, MusicReleaseGroup,)
from root.type_annotations import AuthedHttpRequest
from torrent.forms.music.artist import MusicArtistForm
from torrent.forms.music.release import MusicReleaseForm
from torrent.forms.music.torrent import MusicTorrentForm
from torrent.forms.music.contribution import MusicContributionForm
from torrent.forms.music.release_group import MusicReleaseGroupForm

from .__utilities import instantiated_forms


# Wrapper around the basic python dictionary object that accepts values of
# type string and converts them to type int.
#
# If the conversion from string to integer fails, it throws a 404.
class PkProvider:
    def __init__(self, get_parameters: dict[str, str]):
        self.pks: dict[str, int] = {}

        for k, vs in get_parameters.items():
            for v in vs:
                self.__setitem__(k, v)

    def __setitem__(self, pk_name: str, pk_value: str) -> None:
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


def upload(request: AuthedHttpRequest) -> HttpResponse:
    # Sets of valid GET parameters and the corresponding forms that will be
    # used for the given parameters.
    #
    # The order of the forms is important here, as they are instantiated in
    # this order.
    #
    # 'model_pk', 'contribution_select', and 'release_select' provide PKs to
    # the other forms through PkProvider, so they must come first.
    all_forms = (
        "model_pk",
        "contribution_select",
        "release_select",
        "artist",
        "release_group",
        "contribution",
        "release",
        "torrent",
    )
    valid_get_parameters = {
        (): all_forms,
        ("artist",): all_forms,
        ("contribution",): all_forms,
        ("contribution", "release"): all_forms,
        ("release_group",): ("release_select", "release_group", "release", "torrent"),
        ("release",): ("release", "torrent"),
    }

    # Throw an error if the GET parameters don't match any of the valid sets of GET parameters.
    if tuple(request.GET.keys()) not in valid_get_parameters.keys():
        valid_get_parameters_str = ", ".join(
            "(" + ", ".join(k) + ")" for k in valid_get_parameters.keys()
        )
        message = (
            "Invalid GET parameter(s). Valid GET parameters are: "
            + valid_get_parameters_str
        )
        return renderers.render_http_bad_request(request, message)

    # Create our PkProvider object.
    pks = PkProvider(request.GET)

    # TorrentForm is a file form, and is thus a special case. It needs to be fed 'request.FILES' if the request was a POST.
    torrent_constructor = (
        lambda *args, **kwargs: MusicTorrentForm(*args, request.FILES, **kwargs)
        if (request.method == "POST")
        else MusicTorrentForm(*args, **kwargs)
    )

    # Dictionary of all possible forms.
    model_forms = {
        "artist":              instantiated_forms.MusicObjectForm(pks, "artist",        MusicArtistForm,       MusicArtist),
        "release_group":       instantiated_forms.MusicObjectForm(pks, "release_group", MusicReleaseGroupForm, MusicReleaseGroup),
        "contribution":        instantiated_forms.MusicObjectForm(pks, "contribution",  MusicContributionForm, MusicContribution),
        "release":             instantiated_forms.MusicObjectForm(pks, "release",       MusicReleaseForm,      MusicRelease),
        "torrent":             instantiated_forms.MusicObjectForm(pks, "torrent",       torrent_constructor,   MusicTorrent),
        "contribution_select": instantiated_forms.MusicContributionSelectForm(pks),
        "release_select":      instantiated_forms.MusicReleaseSelectForm(pks),
        "model_pk":            instantiated_forms.MusicModelPkForm(pks),
    }

    # Remove the unneeded forms from model_forms.
    valid_forms = valid_get_parameters[tuple(request.GET.keys())]
    model_forms = {k: model_forms[k] for k in valid_forms}

    # Instantiate all the forms (whether as blank forms, or from POSTed data, or from GETed parameters).
    for k, v in model_forms.items():
        v.instantiate(request)

    # If it was a POST and all the forms pass validation, save them to the database and finally redirect
    #   to a view to display the new torrent.
    if request.method == "POST" and False not in [
        v.is_valid() for (k, v) in model_forms.items()
    ]:
        try:
            with transaction.atomic():
                if "artist" in model_forms and model_forms["artist"].from_pk is False:
                    model_forms["artist"].object.save()

                if ("release_group" in model_forms and model_forms["release_group"].from_pk is False):
                    model_forms["release_group"].object.save()

                if ("contribution" in model_forms and model_forms["contribution"].from_pk is False):
                    model_forms["contribution"].object.artist        = model_forms["artist"].object
                    model_forms["contribution"].object.release_group = model_forms["release_group"].object
                    model_forms["contribution"].object.save()

                if "release" in model_forms and model_forms["release"].from_pk is False:
                    model_forms["release"].object.release_group = model_forms["release_group"].object
                    model_forms["release"].object.save()

                metainfo = request.FILES["torrent-metainfo_file"]
                metainfo.seek(0)
                metainfo_decoded = bdecode(metainfo)

                model_forms["torrent"].object.release = model_forms["release"].object
                model_forms["torrent"].object.uploader = request.user
                model_forms["torrent"].object.infohash_sha1_hexdigest = get_infohash_sha1_hexdigest(metainfo_decoded)
                model_forms["torrent"].object.torrent_size = get_torrent_size(metainfo_decoded)
                model_forms["torrent"].object.torrent_files = get_torrent_file_listing(metainfo_decoded)

                model_forms["torrent"].object.save()
        except Error as e:
            return renderers.render_http_server_error(
                request, f"Could not upload torrent. Error: {e}"
            )

        messages.creation(request, "Uploaded torrent.")
        return redirect(
            "torrent:music_torrent_view", pk=model_forms["torrent"].object.pk
        )

    # Extract the actual django forms from our ObjectForm class, and turn that into a dictionary.
    template_args = {}
    for k, v in model_forms.items():
        template_args[k + "_form"] = v.form

    return render(request, "torrent/music/upload.html", template_args)
