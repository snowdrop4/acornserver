import random

from django.urls import reverse
from django.test import RequestFactory
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from root import messages

from root.news_article_randomiser import create_random_news_article

from account.account_randomiser import create_random_user

from forum.forum_randomiser import create_random_category, create_random_thread, create_random_post
from forum.models import ForumCategory

from torrent.views.music.upload import upload
from torrent.models.music_randomiser import (
	create_random_artist, create_random_release_group,
	create_random_contribution, create_random_release
)
from torrent.metainfo_randomiser import create_random_metainfo_file


def index(request: HttpRequest) -> HttpResponse:
	return render(request, 'debug/index.html')


def populate_music_database(request: HttpRequest) -> HttpResponse:
	user = create_random_user()
	
	# create 1 artist
	(artist, _) = create_random_artist()
	
	# create 4 release groups
	for _ in range(4):
		(release_group, _) = create_random_release_group()
		(contribution,  _) = create_random_contribution(artist, release_group)
		
		# create 3 releases for each release group
		for _ in range(3):
			(release, _) = create_random_release(release_group)
			
			with create_random_metainfo_file() as metainfo_file:
				torrent_data = \
					{ 'torrent-metainfo_file': metainfo_file
					, 'torrent-encode_format': 'FLC016' }
				
				# We don't need to provide the `release_group` pk,
				#   as the upload view deduces it from the `contribution` pk.
				data = \
					{ **{ 'model_pk-artist_pk':               str(artist.pk),       }
					, **{ 'contribution_select-contribution': str(contribution.pk), }
					, **{ 'release_select-release':           str(release.pk),      }
					, **torrent_data }
				
				request_factory = RequestFactory()
				request = request_factory.post(reverse('torrent:music_upload'), data, format='multipart')
				request.user = user
				
				upload(request)
	
	return render(request, 'debug/populate_database.html', { 'database_type': 'Music' })


def populate_forum_database(request: HttpRequest) -> HttpResponse:
	root = ForumCategory.objects.get(pk=1) # get the root category
	
	# create one category
	(category, _) = create_random_category(root)
	
	users = [ create_random_user() for _ in range(0, 10) ]
	
	# create 4 threads
	for _ in range(4):
		(thread, _) = create_random_thread(category, random.choice(users))
		
		# create 10 replies
		for _ in range(10):
			_ = create_random_post(category, thread, random.choice(users))
	
	return render(request, 'debug/populate_database.html', { 'database_type': 'Forum' })


def populate_news_database(request: HttpRequest) -> HttpResponse:
	(news_article, _) = create_random_news_article()
	
	return render(request, 'debug/populate_database.html', { 'database_type': 'News' })


def test_messages(request: HttpRequest) -> HttpResponse:
	messages.success(request,      'Something succeeded.')
	messages.failure(request,      'Something failed.')
	messages.creation(request,     'Something created.')
	messages.deletion(request,     'Something deleted.')
	messages.modification(request, 'Something modified.')
	messages.warning(request,      'Something warned.')
	messages.error(request,        'Something errored.')
	messages.information(request,  'Something informed.')
	
	return render(request, 'debug/test_messages.html')
