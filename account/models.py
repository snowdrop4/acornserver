import random
import string
from typing import Any

from django.db import Error, models, transaction
from django.utils import timezone
from django.contrib import auth
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager

from markupfield.fields import MarkupField


class UserManager(BaseUserManager):
	def create_user(self, username: str, email: str, password: str) -> "User":
		user = self.model(username=username, email=self.normalize_email(email))
		user.set_password(password)
		
		with transaction.atomic():
			user.save()
			
			passkey = TorrentPasskey(user=user)
			passkey.save()
		
		return user
	
	def create_superuser(self, username: str, email: str, password: str) -> "User":
		user = self.create_user(username, email, password)
		
		user.is_superuser = True
		user.is_staff = True
		
		user.save()
		return user


class User(AbstractBaseUser, PermissionsMixin):
	# Custom Fields
	# ‾‾‾‾‾‾‾‾‾‾‾‾‾
	
	username = models.CharField( max_length=20,  unique=True)
	email    = models.EmailField(max_length=256, unique=True)
	
	is_superuser = models.BooleanField(default=False)
	is_staff     = models.BooleanField(default=False)
	
	join_datetime = models.DateTimeField(default=timezone.now)
	
	user_bio = MarkupField(markup_type='markdown', escape_html=True, default='', max_length=4096)
	
	# Number of bytes uploaded/downloaded
	uploaded   = models.PositiveBigIntegerField(default=0)
	downloaded = models.PositiveBigIntegerField(default=0)
	
	# Django nonsense
	# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
	
	# Register a custom manager as managing this model.
	objects = UserManager()
	
	# Set the 'username' field as the unique identifier for a User object.
	# 
	# USERNAME_FIELD could be set to `email` or anything else.
	# I don't know why it is called 'USERNAME_FIELD'.
	USERNAME_FIELD = "username"
	
	# Make the django 'python3 manage.py createsuperuser' command work
	# by telling it that it needs to also ask for email.
	REQUIRED_FIELDS = ["email"]
	
	def __str__(self) -> str:
		return self.username


KEY_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
def gen_passkey() -> str:
	return ''.join(random.choices(KEY_CHARACTERS, k=40))


class TorrentPasskey(models.Model):
	user = models.OneToOneField(auth.get_user_model(), on_delete=models.CASCADE, related_name='passkey')
	key  = models.CharField(max_length=40, unique=True, default=gen_passkey)
	
	def __init__(self, *args: Any, **kwargs: Any):
		super().__init__(*args, **kwargs)
	
	def __str__(self) -> str:
		return self.key
