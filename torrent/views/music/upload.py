from typing import cast

from django import forms
from django.db import Error, transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.files.uploadedfile import UploadedFile

from bcoding import bdecode

from root import messages, renderers
from torrent.metainfo import (
    get_torrent_size,
    get_torrent_file_listing,
    get_infohash_sha1_hexdigest,
)
from torrent.models.music import (
    MusicArtist,
    MusicRelease,
    MusicTorrent,
    MusicContribution,
    MusicReleaseGroup,
)
from root.type_annotations import AuthedHttpRequest
from torrent.forms.music.artist import MusicArtistForm
from torrent.forms.music.release import MusicReleaseForm
from torrent.forms.music.torrent import MusicTorrentForm
from torrent.forms.music.contribution import MusicContributionForm
from torrent.forms.music.release_group import MusicReleaseGroupForm

from .__utilities import instantiated_forms as in_forms
from .__utilities.instantiated_forms import PkProvider


def upload(request: AuthedHttpRequest) -> HttpResponse:
    # Sets of valid GET parameters and the corresponding forms that will be
    # used for the given parameters.
    #
    # The order of the forms is important here, as they will be instantiated in
    # this order.
    #
    # Since 'model_pk', 'contribution_select', and 'release_select' provide PKs
    # to the other forms through PkProvider, they must come first.
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

    # Throw an error if the GET parameters don't match any of the valid sets
    # of GET parameters.
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

    # TorrentForm is a file form, and is thus a special case.
    # It needs to be fed 'request.FILES' if the request was a POST.
    torrent_constructor: type[forms.ModelForm] = (
        lambda *args, **kwargs: MusicTorrentForm(*args, request.FILES, **kwargs)  # type: ignore
        if (request.method == "POST")
        else MusicTorrentForm(*args, **kwargs)
    )

    # Dictionary of all possible forms.
    model_forms = {
        "artist":              in_forms.MusicObjectForm(pks, "artist",        MusicArtistForm,       MusicArtist),
        "release_group":       in_forms.MusicObjectForm(pks, "release_group", MusicReleaseGroupForm, MusicReleaseGroup),
        "contribution":        in_forms.MusicObjectForm(pks, "contribution",  MusicContributionForm, MusicContribution),
        "release":             in_forms.MusicObjectForm(pks, "release",       MusicReleaseForm,      MusicRelease),
        "torrent":             in_forms.MusicObjectForm(pks, "torrent",       torrent_constructor,   MusicTorrent),
        "contribution_select": in_forms.MusicContributionSelectForm(pks),
        "release_select":      in_forms.MusicReleaseSelectForm(pks),
        "model_pk":            in_forms.MusicModelPkForm(pks),
    }

    # Remove the unneeded forms from model_forms.
    valid_forms = valid_get_parameters[tuple(request.GET.keys())]
    model_forms = {k: model_forms[k] for k in valid_forms}

    # Instantiate all the forms (whether as blank forms, or from POSTed data,
    # or from GETed parameters).
    for (k, v) in model_forms.items():
        v.instantiate(request)

    # If it was a POST and all the forms pass validation, save them to the
    # database and finally redirect to a view to display the new torrent.
    if request.method == "POST" and False not in [
        v.is_valid() for (k, v) in model_forms.items()
    ]:
        try:
            with transaction.atomic():
                artist_form = cast(
                    in_forms.MusicObjectForm | None,
                    model_forms.get("artist", None)
                )
                if artist_form and artist_form.from_pk is False:
                    artist_form.object.save()

                release_group_form = cast(
                    in_forms.MusicObjectForm | None,
                    model_forms.get("release_group", None)
                )
                if release_group_form and release_group_form.from_pk is False:
                    release_group_form.object.save()

                contribution_form = cast(
                    in_forms.MusicObjectForm | None,
                    model_forms.get("contribution", None)
                )
                if contribution_form and contribution_form.from_pk is False:
                    contribution_form.object.artist        = artist_form.object  # type: ignore
                    contribution_form.object.release_group = release_group_form.object  # type: ignore
                    contribution_form.object.save()

                release_form = cast(
                    in_forms.MusicObjectForm | None,
                    model_forms.get("release", None)
                )
                if release_form and release_form.from_pk is False:
                    release_form.object.release_group = release_group_form.object  # type: ignore
                    release_form.object.save()

                metainfo = cast(UploadedFile, request.FILES["torrent-metainfo_file"])
                metainfo.seek(0)
                metainfo_decoded = bdecode(metainfo)

                torrent_form = cast(
                    in_forms.MusicObjectForm,
                    model_forms.get("torrent", None)
                )
                torrent = cast(MusicTorrent, torrent_form.object)

                torrent.release = release_form.object  # type: ignore
                torrent.uploader = request.user
                torrent.infohash_sha1_hexdigest = get_infohash_sha1_hexdigest(metainfo_decoded)
                torrent.torrent_size = get_torrent_size(metainfo_decoded)
                torrent.torrent_files = get_torrent_file_listing(metainfo_decoded)

                torrent.save()
        except Error as e:
            return renderers.render_http_server_error(
                request, f"Could not upload torrent. Error: {e}"
            )

        messages.creation(request, "Uploaded torrent.")
        return redirect(
            "torrent:music_torrent_view", pk=torrent.pk
        )

    # Extract the actual django forms from our ObjectForm class, and turn that into a dictionary.
    template_args = {}
    for k, v in model_forms.items():
        template_args[k + "_form"] = v.form

    return render(request, "torrent/music/upload.html", template_args)
