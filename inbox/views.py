from django.views import View
from django.db import Error, transaction
from django.db.models import Q, QuerySet
from django.utils import timezone
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

from root import renderers
from inbox.models import InboxThread, InboxMessage
from inbox.forms import MessageFormAdd


class InboxView(View):
	def get(self, request: HttpRequest) -> HttpResponse:
		threads = InboxThread.objects\
			.filter(Q(sender=request.user) | Q(receiver=request.user))\
			.order_by('-latest_message_datetime')\
			[:10]
		
		return render(request, 'inbox/view.html',
			{
				'threads': threads,
			}
		)


# TODO: add pagination
class ThreadView(View):
	def get_thread_and_messages(self, pk: int) -> tuple[InboxThread, QuerySet[InboxMessage]]:
		thread = get_object_or_404(InboxThread, pk=pk)
		messages = thread.messages.order_by('-pub_date')
		
		return (thread, messages)
	
	def get(self, request: HttpRequest, pk: int) -> HttpResponse:
		form = MessageFormAdd()
		(thread, messages) = self.get_thread_and_messages(pk)
		
		if thread.sender == request.user:
			thread.sender_unread_messages = 0
			thread.save()
		elif thread.receiver == request.user:
			thread.receiver_unread_messages = 0
			thread.save()
		
		return render(request, 'inbox/thread/view.html',
			{
				'form': form,
				'thread': thread,
				'thread_messages': messages,
			}
		)
	
	def post(self, request: HttpRequest, pk: int) -> HttpResponse:
		form = MessageFormAdd(request.POST)
		(thread, messages) = self.get_thread_and_messages(pk)
		
		if form.is_valid():
			now = timezone.now()
			
			message = form.save(commit=False)
			
			message.thread = thread
			message.sender = request.user
			
			message.pub_date = now
			message.mod_date = now
			
			if thread.sender == request.user:
				thread.receiver_unread_messages += 1
			elif thread.receiver == request.user:
				thread.sender_unread_messages += 1
			
			try:
				with transaction.atomic():
					thread.save()
					message.save()
			except Error as e:
				return renderers.render_http_server_error(request, f"Could not send reply. Error: {e}")
		
		return render(request, 'inbox/thread/view.html',
			{
				'form': form,
				'thread': thread,
				'thread_messages': messages,
			}
		)
