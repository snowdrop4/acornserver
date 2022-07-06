import string
import random

from django.contrib.auth import get_user_model

from root.utils.random import random_str


def create_random_user():
	username = random_str(5)
	email    = random_str(5) + '@' + random_str(5) + '.com'
	password = random_str(20)
	
	# Use `get_user_model` instead of simply importing the `User` model directly
	# See: https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#referencing-the-user-model
	return get_user_model().objects.create_user(username, email, password)
