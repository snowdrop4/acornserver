from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from markupfield.fields import MarkupField


class UserManager(BaseUserManager):
	def create_user(self, username, email, password):
		user = self.model(username=username, email=self.normalize_email(email))
		user.set_password(password)
		
		user.save(using=self._db)
		return user
	
	def create_superuser(self, username, email, password):
		user = self.create_user(username, email, password)
		user.is_superuser = True
		user.is_staff = True
		
		user.save(using=self._db)
		return user


# Any value not given a default value, and not marked as nullable, will need to filled in somehow.
#
# If creating a user through a web form, the form must include these non-nullable values.
#
# If creating a user manually in some function somewhere, the values in the user object
# must be set before it is saved to the database.
class User(AbstractBaseUser, PermissionsMixin):
	username = models.CharField(max_length=20, unique=True)
	email = models.EmailField(max_length=256, unique=True)
	
	is_superuser = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)
	
	# Pass the timezone.now function as the default value. `timezone.now()` will be called upon creation of a user,
	# and the result of this will be used as the default value.
	join_datetime = models.DateTimeField(default=timezone.now)
	
	user_bio = MarkupField(markup_type='markdown', escape_html=True, default='')
	
	# Register a custom manager as managing this model.
	objects = UserManager()
	
	# Set the 'username' field as the unique identifier for a User object.
	# 
	# USERNAME_FIELD could be set to 'email' or anything else. I don't know why it is called 'USERNAME_FIELD'.
	USERNAME_FIELD = "username"
	
	# Make the django 'python3 manage.py createsuperuser' command work by telling it that it needs to also ask for email.
	REQUIRED_FIELDS = ["email"]
	
	def __str__(self):
		return self.username
