from django.http import HttpResponse
from django.shortcuts import render

from forum.models import ForumCategory
from root.type_annotations import AuthedHttpRequest


def view(request: AuthedHttpRequest) -> HttpResponse:
    # Every category must be a child of a root category at `pk=1`.
    #
    # The children of the root category are assumed to have `folder` set
    # to `True`, which indicates that users can't post to that category.
    #
    # The root category won't be visible to users, but having a root category
    # greatly simplifies the code for the forum because it can be represented
    # as a simple tree branching down from one root node.
    try:
        root = (
            ForumCategory.objects
            .prefetch_related("children__children__latest_post_thread__latest_post_author")
            .prefetch_related("children__children__children")
            .get(pk=1)
        )
    except ForumCategory.DoesNotExist:
        # If the root category doesn't exist, create one.
        root = ForumCategory(parent=None, title="root", folder=True)
        root.save()

    return render(request, "forum/index.html", {"root": root})
