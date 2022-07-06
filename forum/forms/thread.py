from django import forms

from forum.models import ForumThread


class ThreadFormAdd(forms.ModelForm):
	prefix = 'thread'
	
	class Meta:
		model = ForumThread
		fields = ('title', 'body')
