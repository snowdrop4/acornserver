from django.test import TestCase, RequestFactory
from django.urls import reverse

from inbox.views import ThreadReplyView, ThreadCreateView
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
		thread = InboxThread.objects.get(pk=1)
		message = InboxMessage.objects.get(pk=1)
		
		self.assertEquals(thread.title, self.data["thread-title"])
		self.assertEquals(thread.sender,   self.user)
		self.assertEquals(thread.receiver, self.receiver)
		self.assertEquals(thread.sender_unread_messages,   0)
		self.assertEquals(thread.receiver_unread_messages, 1)
		
		self.assertEquals(message.thread, thread)
		self.assertEquals(message.content.raw, self.data["thread-content"])
		self.assertEquals(message.sender, self.user)
		
		dates = [message.pub_date, message.mod_date, thread.latest_message_datetime]
		self.assertTrue(all(i == dates[0] for i in dates))
