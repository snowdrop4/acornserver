from django.db import Error, transaction
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

from root import messages, renderers
from forum.models import ForumThread, ForumCategory
from forum.forms.post import PostFormAdd
from forum.forms.thread import ThreadFormAdd
from root.type_annotations import AuthedHttpRequest
from root.utils.get_parameters import fill_typed_get_parameters


def view(request: AuthedHttpRequest, pk: int) -> HttpResponse:
    try:
        thread = (
            ForumThread.objects.select_related("category")
            .select_related("author")
            .prefetch_related("replies__author")
            .get(pk=pk)
        )
    except ForumThread.DoesNotExist:
        return renderers.render_http_not_found(request, "Thread not found.")

    category = thread.category

    if request.method == "POST":
        form = PostFormAdd(request.POST)

        if form.is_valid():
            post = form.save(commit=False)

            now = timezone.now()

            # category
            category.post_count += 1
            category.latest_post_thread = thread

            # thread
            thread.post_count += 1
            thread.latest_post_author = request.user
            thread.latest_post_datetime = now

            # post
            post.thread = thread
            post.author = request.user
            post.post_number = thread.post_count
            post.datetime = now

            try:
                with transaction.atomic():
                    post.save()
                    thread.save()
                    category.save()
            except Error as e:
                return renderers.render_http_server_error(
                    request, f"Could not post reply. Error: {e}"
                )

            messages.creation(request, "Posted reply.")
            return redirect("forum:thread_view", pk=thread.pk)
    else:
        form = PostFormAdd()

    template_args = {"form": form, "thread": thread, "category": category}

    return render(request, "forum/thread/view.html", template_args)


def add(request: AuthedHttpRequest) -> HttpResponse:
    try:
        get_params = fill_typed_get_parameters(
            request, {"category": (True, int, "must be an integer")}
        )
    except ValueError as e:
        return renderers.render_http_bad_request(request, str(e))

    category = get_object_or_404(ForumCategory, pk=get_params["category"])

    if request.method == "POST":
        form = ThreadFormAdd(request.POST)

        if form.is_valid():
            thread = form.save(commit=False)

            now = timezone.now()

            # thread
            thread.category = category
            thread.author = request.user
            thread.post_number = 1
            thread.datetime = now
            thread.latest_post_author = request.user
            thread.latest_post_datetime = now

            # category
            category.post_count += 1
            category.thread_count += 1

            try:
                with transaction.atomic():
                    thread.save()
                    category.latest_post_thread = thread
                    category.save()
            except Error as e:
                return renderers.render_http_server_error(
                    request, f"Could not create thread. Error: {e}"
                )

            messages.creation(request, "Created thread.")
            return redirect("forum:thread_view", pk=thread.pk)
    else:
        form = ThreadFormAdd()

    return render(
        request, "forum/thread/add.html", {"form": form, "category": category}
    )
