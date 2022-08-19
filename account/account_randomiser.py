import random
import string

from django.contrib.auth import get_user_model

from root.utils.random import random_str

from .models import User


def create_random_user() -> User:
	username = random_str(5)
	email    = random_str(5) + '@' + random_str(5) + '.com'
	password = random_str(20)
	
	return get_user_model().objects.create_user(username, email, password)
