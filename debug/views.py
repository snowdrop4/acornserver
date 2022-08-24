import random
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from django.shortcuts import render

from root import messages
from forum.models import ForumCategory
from root.type_annotations import AuthedHttpRequest
from forum.forum_randomiser import (create_random_post, create_random_thread,
                                    create_random_category,)
from account.account_randomiser import create_random_user
from torrent.views.music.upload import upload
from torrent.metainfo_randomiser import create_random_metainfo_file
from root.news_article_randomiser import create_random_news_article
from torrent.models.music_randomiser import (create_random_artist,
                                             create_random_release,
                                             create_random_contribution,
                                             create_random_release_group,)


def index(request: AuthedHttpRequest) -> HttpResponse:
    return render(request, "debug/index.html")


def populate_music_database(request: AuthedHttpRequest) -> HttpResponse:
    user = create_random_user()

    # create 1 artist
    (artist, _) = create_random_artist()

    # create 4 release groups
    for _ in range(4):
        (release_group, _) = create_random_release_group()
        (contribution,  _) = create_random_contribution(artist, release_group)

        # create 3 releases for each release group
        for _ in range(3):
            (release, _) = create_random_release(release_group)

            with create_random_metainfo_file() as metainfo_file:
                torrent_data = {
                    "torrent-metainfo_file": metainfo_file,
                    "torrent-encode_format": "FLC016",
                }

                # We don't need to provide the `release_group` pk,
                #   as the upload view deduces it from the `contribution` pk.
                data: dict[str, Any] = {
                    **{ "model_pk-artist_pk": str(artist.pk), },
                    **{ "contribution_select-contribution": str(contribution.pk), },
                    **{ "release_select-release": str(release.pk), },
                    **torrent_data,
                }

                request_factory = RequestFactory()
                request = request_factory.post(
                    reverse("torrent:music_upload"), data, format="multipart"
                )  # type: ignore
                request.user = user

                upload(request)

    return render(request, "debug/populate_database.html", {"database_type": "Music"})


def populate_forum_database(request: AuthedHttpRequest) -> HttpResponse:
    root = ForumCategory.objects.get(pk=1)  # get the root category

    # create one category
    (category, _) = create_random_category(root)

    users = [create_random_user() for _ in range(0, 10)]

    # create 4 threads
    for _ in range(4):
        (thread, _) = create_random_thread(category, random.choice(users))

        # create 10 replies
        for _ in range(10):
            _ = create_random_post(category, thread, random.choice(users))

    return render(request, "debug/populate_database.html", {"database_type": "Forum"})


def populate_news_database(request: AuthedHttpRequest) -> HttpResponse:
    (news_article, _) = create_random_news_article()

    return render(request, "debug/populate_database.html", {"database_type": "News"})


def test_messages(request: AuthedHttpRequest) -> HttpResponse:
    messages.success(     request, "Something succeeded.")
    messages.failure(     request, "Something failed.")
    messages.creation(    request, "Something created.")
    messages.deletion(    request, "Something deleted.")
    messages.modification(request, "Something modified.")
    messages.warning(     request, "Something warned.")
    messages.error(       request, "Something errored.")
    messages.information( request, "Something informed.")

    return render(request, "debug/test_messages.html")
