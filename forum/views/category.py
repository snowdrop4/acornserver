from django.http import HttpResponse
from django.shortcuts import render

from root import renderers
from forum.models import ForumCategory
from root.type_annotations import AuthedHttpRequest


def view(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    try:
        category = (
            ForumCategory.objects.prefetch_related(
                "children__latest_post_thread__latest_post_author"
            )
            .prefetch_related("children__children")
            .get(pk=pk)
        )
    except ForumCategory.DoesNotExist:
        return renderers.render_http_not_found(request, "Category not found.")

    threads = (
        category.threads.order_by("-datetime")
        .select_related("author")
        .select_related("latest_post_author")
    )

    template_args = {"category": category, "threads": threads}

    return render(request, "forum/category/view.html", template_args)
