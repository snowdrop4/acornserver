from django.db import models
from django.contrib.auth import get_user_model

from markupfield.fields import MarkupField


class InboxThread(models.Model):
	title = models.CharField(max_length=256)
	
	sender = models.ForeignKey(
		get_user_model(),
		on_delete=models.SET_NULL,
		null=True,
		related_name='sent_inbox_threads'
	)
	
	receiver = models.ForeignKey(
		get_user_model(),
		on_delete=models.SET_NULL,
		null=True,
		related_name='received_inbox_threads'
	)
	
	class Meta:
		verbose_name = 'Inbox Thread'
		verbose_name_plural = 'Inbox Threads'


class InboxMessage(models.Model):
	thread = models.ForeignKey(InboxThread, on_delete=models.CASCADE, related_name='messages')
	content = MarkupField(markup_type='markdown', escape_html=True, default='')
	
	mod_date = models.DateTimeField(auto_now=True)
	pub_date = models.DateTimeField(auto_now_add=True)
	
	sender = models.ForeignKey(
		get_user_model(),
		on_delete=models.SET_NULL,
		null=True,
		related_name='sent_inbox_messages'
	)
	
	class Meta:
		verbose_name = 'Inbox Message'
		verbose_name_plural = 'Inbox Messages'
	
	def __str__(self):
		return self.content
