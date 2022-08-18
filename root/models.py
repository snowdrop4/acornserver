from django.db import models

from markupfield.fields import MarkupField


class NewsArticle(models.Model):
	title = models.CharField(max_length=256)
	content = MarkupField(markup_type='markdown', escape_html=True, default='')
	mod_date = models.DateTimeField(auto_now=True)
	pub_date = models.DateTimeField(auto_now_add=True)
	
	def __str__(self) -> str:
		return self.title
