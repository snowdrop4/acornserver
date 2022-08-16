from django import forms

from inbox.models import InboxMessage


class MessageFormAdd(forms.ModelForm):
	prefix = 'message'
	
	class Meta:
		model = InboxMessage
		fields = ('content',)
		
		labels = {
			'content': (''),
		}

