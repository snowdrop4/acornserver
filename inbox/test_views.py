import random
from typing import cast

from django.test import TestCase, RequestFactory
from django.urls import reverse

from inbox.views import InboxView, ThreadReplyView, ThreadCreateView
from inbox.inbox_randomiser import create_random_thread, create_random_message
from account.account_randomiser import create_random_user

from .models import InboxThread, InboxMessage


class TestThread(TestCase):
    def setUp(self) -> None:
        self.requestFactory = RequestFactory()
        self.user = create_random_user()
        self.receiver = create_random_user()

        self.data = {
            "thread-title": "Test Thread 123456789",
            "thread-receiver": self.receiver.username,
            "thread-content": "# Header 1\n\nOne, two, three.\n\n## Header 2\n\n* item 1\nitem 2",
        }

    def test_create_thread(self) -> None:
        url = reverse("inbox:thread_create")

        request = self.requestFactory.post(url, self.data)
        request.user = self.user

        ThreadCreateView.as_view()(request)
        thread = cast(InboxThread, InboxThread.objects.last())
        message = cast(InboxMessage, InboxMessage.objects.last())

        self.assertEquals(thread.title, self.data["thread-title"])
        self.assertEquals(thread.sender, self.user)
        self.assertEquals(thread.receiver, self.receiver)
        self.assertEquals(thread.sender_unread_messages, 0)
        self.assertEquals(thread.receiver_unread_messages, 1)

        self.assertEquals(message.thread, thread)
        self.assertEquals(message.content.raw, self.data["thread-content"])
        self.assertEquals(message.sender, self.user)

        dates = [message.pub_date, message.mod_date, thread.latest_message_datetime]
        self.assertTrue(all(i == dates[0] for i in dates))

    # Test the unread messages count on the user model
    def test_unread_messages(self) -> None:
        url = reverse("inbox:thread_create")
        request = self.requestFactory.post(url, self.data)
        request.user = self.user

        threads = []

        # Test unread message count increment:
        for i in range(1, 3):
            ThreadCreateView.as_view()(request)
            threads.append(cast(InboxThread, InboxThread.objects.last()))

            self.receiver.refresh_from_db()
            self.assertEquals(self.receiver.unread_messages, i)

        # Test unread message count decrement:
        for i in range(1, -1, -1):
            data = {"pk": threads[i].pk}

            url = reverse("inbox:thread_view", kwargs=data)
            request = self.requestFactory.get(url)
            request.user = self.receiver

            ThreadReplyView.as_view()(request, **data)
            self.assertEquals(self.receiver.unread_messages, i)


class TestThreadQueries(TestCase):
    def setUp(self) -> None:
        self.requestFactory = RequestFactory()
        self.user = create_random_user()

        self.other_users = [create_random_user() for i in range(0, 10)]

        self.threads = []

        for i in range(0, 10):
            if random.randint(0, 1) == 1:
                sender = self.user
                receiver = random.choice(self.other_users)
            else:
                sender = random.choice(self.other_users)
                receiver = self.user

            (thread, thread_data, message, message_data) = create_random_thread(
                sender, receiver
            )

            self.threads.append(thread)

            for i in range(0, 5):
                create_random_message(thread, random.choice([sender, receiver]))

    def test_inbox_view_queries(self) -> None:
        request = self.requestFactory.get(reverse("inbox:inbox_view"))
        request.user = self.user

        with self.assertNumQueries(1):
            InboxView.as_view()(request)

    def test_thread_reply_view_queries(self) -> None:
        # Get a random thread
        thread = random.choice(self.threads)

        # Set the unread message count for the thread to 0 before we run the view,
        # otherwise the view might do an SQL UPDATE on the object to mark the
        # unread message as read.
        thread.sender_unread_messages = 0
        thread.receiver_unread_messages = 0
        thread.save()

        data = {"pk": thread.pk}

        request = self.requestFactory.get(reverse("inbox:thread_view", kwargs=data))
        request.user = self.user

        with self.assertNumQueries(2):
            ThreadReplyView.as_view()(request, **data)
