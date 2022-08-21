from django import forms
from django.core.exceptions import ValidationError

from markupfield.widgets import MarkupTextarea

from inbox.models import InboxThread, InboxMessage
from account.models import User


class MessageFormAdd(forms.ModelForm):
	prefix = 'message'
	
	class Meta:
		model = InboxMessage
		fields = ('content',)
		
		labels = {
			'content': (''),
		}


class ThreadFormAdd(forms.Form):
	prefix = 'thread'
	
	title    = forms.CharField(label='Title', max_length=InboxThread._meta.get_field('title').max_length)
	receiver = forms.CharField(label='To',    max_length=InboxThread._meta.get_field('receiver').max_length)
	
	# Add an extra field to store content for the InboxMessage object that
	# we'll need to create along with the InboxThread object.
	content = forms.CharField(widget=MarkupTextarea, max_length=InboxMessage._meta.get_field('content').max_length)
	
	def __init__(self, *args, **kwargs):
		super().__init__(prefix='thread', *args, **kwargs)
	
	def clean_receiver(self, *args, **kwargs) -> User:
		username = self.cleaned_data['receiver']
		
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			raise ValidationError('User does not exist')
		
		return user
