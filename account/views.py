from typing import Any

from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render, get_object_or_404

from .forms import SignUpForm, UserProfileForm, UserUsernameForm, UserEmailForm
from root import messages
from torrent.models.music_utilities import group_torrents


def signup(request: HttpRequest) -> HttpResponse:
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('root:homepage')
	else:
		form = SignUpForm()
	
	return render(request, 'account/authentication/signup.html', { 'form': form })


def profile_view(request: HttpRequest, pk: int) -> HttpResponse:
	user = get_object_or_404(get_user_model(), pk=pk)
	
	uploads = user.music_uploads\
		.select_related('release__release_group')\
		.prefetch_related('downloads')\
		.order_by('upload_datetime')[:10]
	
	downloads = user.music_downloads\
		.select_related('torrent__release__release_group')\
		.prefetch_related('torrent__downloads')\
		.order_by('download_datetime')[:10]
	
	latest_uploads   = group_torrents(uploads)
	latest_downloads = group_torrents([ i.torrent for i in downloads ])
	
	return render(request, 'account/profile/view.html',
		{
			'target_user': user,
			'latest_uploads': latest_uploads,
			'latest_downloads': latest_downloads
		}
	)

# For editing things like biography/avatar/etc.
def profile_edit(request: HttpRequest) -> HttpResponse:
	user = request.user
	
	if request.method == 'POST':
		form = UserProfileForm(request.POST, instance=user)
		
		if form.is_valid():
			user = form.save()
			messages.modification(request, 'Modified profile information.')
			return redirect('account:profile_view', pk=user.pk)
	else:
		form = UserProfileForm(instance=user)
	
	return render(request, 'account/profile/edit_profile.html',
		{ 'form': form, 'target_user': user }
	)

# For editing things like username/email/passkey/etc.
# 
# This view contains three forms, and the template contains a hidden
# field identifying which form was submitted.
def account_edit(request: HttpRequest) -> HttpResponse:
	user = request.user
	
	forms: dict[str, Any] = {
		'username_form': UserUsernameForm,
		'email_form': UserEmailForm,
		'password_form': PasswordChangeForm
	}
	
	forms_kwargs = {
		'username_form': { 'instance': user },
		'email_form': { 'instance': user },
		'password_form': { 'user': user },
	}
	
	forms_messages = {
		'username_form': 'Modified username.',
		'email_form': 'Modified email.',
		'password_form': 'Modified password'
	}
	
	if (
		request.method == 'POST' and
		'form_type' in request.POST and
		request.POST['form_type'] in forms
	):
		form_type = request.POST['form_type']
		
		# Instantiate the POSTed form with the POST data
		forms[form_type] = forms[form_type](data=request.POST, **forms_kwargs[form_type])
		
		if forms[form_type].is_valid():
			user = forms[form_type].save()
			messages.modification(request, forms_messages[form_type])
			
			# Special case for the password form; we need to refresh the session
			if form_type == 'password_form':
				update_session_auth_hash(request, user)
			
			return redirect('account:profile_view', pk=user.pk)
	else:
		form_type = ''
	
	# Instantiate the non-POSTed forms
	for (k, v) in forms.items():
		if k != form_type:
			forms[k] = forms[k](**forms_kwargs[k])
	
	return render(request, 'account/profile/edit_account.html',
		{
			'target_user': user,
			**forms
		}
	)
