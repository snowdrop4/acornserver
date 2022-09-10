from django.db import Error, transaction
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.views import View
from django.db.models import Q, QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model

from root import renderers
from inbox.forms import ThreadFormAdd, MessageFormAdd
from inbox.models import InboxThread, InboxMessage
from root.type_annotations import AuthedHttpRequest
from root.utils.get_parameters import fill_typed_get_parameters


class InboxView(View):
    def get(self, request: AuthedHttpRequest) -> HttpResponse:
        threads = (
            InboxThread.objects.filter(
                Q(sender=request.user) | Q(receiver=request.user)
            )
            .order_by("-latest_message_datetime")
            .select_related("receiver")
            .select_related("sender")[:10]
        )

        return render(request, "inbox/view.html", {"threads": threads})


class ThreadCreateView(View):
    def get(self, request: AuthedHttpRequest) -> HttpResponse:
        try:
            get_params = fill_typed_get_parameters(
                request, {"to": (False, int, "must be an integer")}
            )
        except ValueError as e:
            return renderers.render_http_bad_request(request, str(e))

        if "to" in get_params:
            receiver = get_object_or_404(get_user_model(), pk=get_params["to"])
            form = ThreadFormAdd(initial={"receiver": receiver.username})
        else:
            form = ThreadFormAdd()

        return render(request, "inbox/thread/add.html", {"form": form})

    def post(self, request: AuthedHttpRequest) -> HttpResponse:
        form = ThreadFormAdd(request.POST)

        if form.is_valid():
            now = timezone.now()
            receiver = form.cleaned_data["receiver"]

            thread = InboxThread(
                title=form.cleaned_data["title"],
                sender=request.user,
                receiver=receiver,
                latest_message_datetime=now,
            )

            message = InboxMessage(
                content=form.cleaned_data["content"],
                pub_date=now,
                mod_date=now,
                sender=request.user,
            )

            receiver.unread_messages += 1

            try:
                with transaction.atomic():
                    thread.save()

                    message.thread = thread
                    message.save()

                    receiver.save()
            except Error as e:
                return renderers.render_http_server_error(
                    request, f"Could not create thread. Error: {e}"
                )

            return redirect("inbox:thread_view", pk=thread.pk)

        return render(request, "inbox/thread/add.html", {"form": form})


# TODO: add pagination
class ThreadReplyView(View):
    def get_thread_and_messages(
        self, pk: int
    ) -> tuple[InboxThread, QuerySet[InboxMessage]]:
        try:
            thread = (
                InboxThread.objects.select_related("sender")
                .select_related("receiver")
                .get(pk=pk)
            )
        except InboxThread.DoesNotExist:
            raise Http404

        messages = thread.messages.order_by("-pub_date").select_related("sender")

        return (thread, messages)

    def get(self, request: AuthedHttpRequest, pk: int) -> HttpResponse:
        form = MessageFormAdd()
        (thread, messages) = self.get_thread_and_messages(pk)

        if thread.sender != request.user and thread.receiver != request.user:
            return renderers.render_http_forbidden(
                request, "Not authorised to view thread"
            )

        if thread.sender == request.user and thread.sender_unread_messages > 0:
            thread.sender_unread_messages = 0
            thread.save()

        if thread.receiver == request.user and thread.receiver_unread_messages > 0:
            request.user.unread_messages -= thread.receiver_unread_messages
            thread.receiver_unread_messages = 0

            try:
                with transaction.atomic():
                    thread.save()
                    request.user.save()
            except Error as e:
                return renderers.render_http_server_error(
                    request, f"Could not send reply. Error: {e}"
                )

        return render(
            request,
            "inbox/thread/view.html",
            {
                "form": form,
                "thread": thread,
                "thread_messages": messages,
            },
        )

    def post(self, request: AuthedHttpRequest, pk: int) -> HttpResponse:
        form = MessageFormAdd(request.POST)
        (thread, messages) = self.get_thread_and_messages(pk)

        if form.is_valid():
            now = timezone.now()

            message = form.save(commit=False)

            message.thread = thread
            message.sender = request.user

            message.pub_date = now
            message.mod_date = now

            # Increment the unread message count on the thread object
            # for the user who just received the message.
            if thread.sender == request.user:
                thread.receiver_unread_messages += 1
                message_target = thread.receiver
            elif thread.receiver == request.user:
                thread.sender_unread_messages += 1
                message_target = thread.sender
            else:
                return renderers.render_http_server_error(
                    request, "Could post reply to thread."
                )

            # Increment the unread message count on the user object of the
            # user who just received the message.
            message_target.unread_messages += 1  # type: ignore

            try:
                with transaction.atomic():
                    thread.save()
                    message.save()
                    message_target.save()  # type: ignore
            except Error as e:
                return renderers.render_http_server_error(
                    request, f"Could not send reply. Error: {e}"
                )

        return render(
            request,
            "inbox/thread/view.html",
            {
                # We need to reconstruct the form anew, so that it's blank again
                # and doesn't retain the contents of the message we just sent.
                "form": MessageFormAdd(),
                "thread": thread,
                "thread_messages": messages,
            },
        )
