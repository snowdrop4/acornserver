from django.db import models
from django.contrib import auth

from mptt.models import MPTTModel, TreeForeignKey
from markupfield.fields import MarkupField


class ForumCategory(MPTTModel):
	parent = TreeForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
	
	title = models.CharField(max_length=256)
	
	# false: users may post threads to this category
	# true: users may not post threads to this category
	folder = models.BooleanField()
	
	thread_count = models.IntegerField(default=0)
	post_count = models.IntegerField(default=0)
	
	latest_post_thread = models.ForeignKey('ForumThread', on_delete=models.SET_NULL, null=True, blank=True)
	
	def __str__(self) -> str:
		return self.title
	
	class Meta:
		verbose_name = 'Category'
		verbose_name_plural = 'Categories'


class ForumContent(models.Model):
	body = MarkupField(markup_type='markdown', escape_html=True, max_length=4096)
	
	datetime = models.DateTimeField()
	post_number = models.IntegerField()
	
	class Meta:
		abstract = True


class ForumThread(ForumContent):
	category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='threads')
	
	title = models.CharField(max_length=256)
	author = models.ForeignKey(auth.get_user_model(), on_delete=models.SET_NULL, null=True, related_name='forum_threads')
	post_count = models.IntegerField(default=1)
	
	latest_post_author = models.ForeignKey(auth.get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
	latest_post_datetime = models.DateTimeField(null=True, blank=True)
	
	@property
	def reply_count(self) -> int:
		return self.post_count - 1
	
	def __str__(self) -> str:
		return self.title
	
	class Meta:
		verbose_name = 'Thread'
		verbose_name_plural = 'Threads'


class ForumPost(ForumContent):
	thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='replies')
	author = models.ForeignKey(auth.get_user_model(), on_delete=models.SET_NULL, null=True, related_name='forum_posts')
	
	class Meta:
		verbose_name = 'Post'
		verbose_name_plural = 'Posts'
