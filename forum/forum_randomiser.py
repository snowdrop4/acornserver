from django.utils import timezone

from account.models import User
from root.utils.random import random_str, random_prose
from forum.models import ForumCategory, ForumThread, ForumPost


def create_random_category(parent: ForumCategory) -> tuple[ForumCategory, dict]:
	data = {
		'category-title': random_str(),
		'category-folder': False
	}
	
	args = { a.removeprefix('category-'): b for (a, b) in data.items() }
	category = ForumCategory.objects.create(**args, parent=parent)
	
	return category, data


def create_random_thread(category: ForumCategory, author: User) -> tuple[ForumThread, dict]:
	data = {
		'thread-title': random_str(),
		'thread-body': random_prose()
	}
	
	now = timezone.now()
	
	args = { a.removeprefix('thread-'): b for (a, b) in data.items() }
	thread = ForumThread.objects.create(**args,
		category=category, author=author, datetime=now, post_number=1,
	)
	
	category.latest_post_thread = thread
	category.save()
	
	return thread, data


def create_random_post(category: ForumCategory, thread: ForumThread, author: User) -> tuple[ForumPost, dict]:
	data = { 'post-body': random_prose() }
	
	now = timezone.now()
	
	# category
	category.post_count += 1
	category.latest_post_thread = thread
	
	# thread
	thread.post_count += 1
	thread.latest_post_author = author
	thread.latest_post_datetime = now
	
	args = { a.removeprefix('post-'): b for (a, b) in data.items() }
	post = ForumPost.objects.create(**args,
		thread=thread, author=author, datetime=now,
		post_number=thread.post_count,
	)
	
	thread.save()
	category.save()
	
	return post, data
