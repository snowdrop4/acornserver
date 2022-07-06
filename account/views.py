from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import PermissionDenied

from .forms import SignUpForm, UserProfileForm
from root import messages
from torrent.models.music_utilities import group_torrents


def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('root:homepage')
	else:
		form = SignUpForm()
	
	return render(request, 'account/authentication/signup.html', { 'form': form })


def profile_view(request, pk):
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
		{ 'target_user': user
		, 'latest_uploads': latest_uploads
		, 'latest_downloads': latest_downloads })


def profile_edit(request, pk):
	if request.user.pk is not pk:
		raise PermissionDenied
	
	user = get_object_or_404(get_user_model(), pk=pk)
	
	if request.method == 'POST':
		form = UserProfileForm(request.POST, instance=user)
		
		if form.is_valid():
			user = form.save()
			messages.modification(request, 'Modified profile.')
			return redirect('account:profile_view', pk=user.pk)
	else:
		form = UserProfileForm(instance=user)
	
	return render(request, 'account/profile/edit.html', { 'form': form, 'target_user': user })
