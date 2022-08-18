from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from inbox.models import InboxThread, InboxMessage
from .serializers import InboxThreadSerializer, InboxMessageSerializer


class InboxThreadView(APIView):
	"""
	:return: 10 most recently updated threads for the authenticated user
	"""
	permission_classes = [permissions.IsAuthenticated]
	
	def get(self, request: HttpRequest) -> HttpResponse:
		user = request.user.pk
		threads = InboxThread.objects\
			.filter(Q(sender=user) | Q(receiver=user))\
			.order_by('-latest_message_datetime')\
			[:10]
		
		serializer = InboxThreadSerializer(threads, many=True)
		return Response(serializer.data)


class InboxMessagesView(APIView):
	"""
	:return: 10 most recent messages for the specified thread
	"""
	
	permission_classes = [permissions.IsAuthenticated]
	
	def get(self, request: HttpRequest, thread_pk: int) -> HttpResponse:
		user = request.user.pk
		thread = get_object_or_404(InboxThread, pk=thread_pk)
		
		if thread.sender.pk == user or thread.receiver.pk == user:
			messages = thread.messages.order_by('-pub_date')[:10]
			serializer = InboxMessageSerializer(messages, many=True)
			return Response(serializer.data)
		else:
			raise PermissionDenied
