from django import forms

from forum.models import ForumPost


class PostFormAdd(forms.ModelForm):
	prefix = 'post'
	
	class Meta:
		model = ForumPost
		fields = ('body',)
		
		labels = {
			'body': (''),
		}
