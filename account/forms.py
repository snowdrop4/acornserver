from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _


class SignUpForm(UserCreationForm):
	prefix = 'signup'
	
	def __init__(self, *args: Any, **kwargs: Any):
		super().__init__(*args, **kwargs)
		
		# Since the password fields are specified within UserCreationForm directly
		#   (without using ModelForm functionality like we are using with the
		#   username and email fields), we cannot just specify the help text by
		#   setting `help_texts` in the `Meta` class. The password fields have
		#   already been created at this point.
		self.fields['password2'].help_text = None
	
	class Meta:
		model = get_user_model()
		# Password fields are already included by `UserCreationForm`, which we
		#   inherit from, so we don't include them here.
		fields = ('username', 'email')


class UserProfileForm(forms.ModelForm):
	prefix = 'profile'
	
	class Meta:
		model = get_user_model()
		fields = ('user_bio', )


class UserUsernameForm(forms.ModelForm):
	prefix = 'account'
	
	class Meta:
		model = get_user_model()
		fields = ('username', )


class UserEmailForm(forms.ModelForm):
	prefix = 'account'
	
	class Meta:
		model = get_user_model()
		fields = ('email', )
