from django.urls import path

from .views.music import (
	artist, release_group, contribution, release, torrent, upload, latest
)


app_name = 'torrent'
urlpatterns = [
	path('music/artist/add',                artist.add,              name='music_artist_add'),
	path('music/artist/view/<int:pk>',      artist.view,             name='music_artist_view'),
	path('music/artist/edit/<int:pk>',      artist.edit,             name='music_artist_edit'),
	path('music/artist/delete/<int:pk>',    artist.Delete.as_view(), name='music_artist_delete'),
	path('music/artist/view/json/<int:pk>', artist.view_json,        name='music_artist_view_json'),
	path('music/artist/view/contributions/json/<int:pk>', artist.view_contributions_json, name='music_artist_view_contributions_json'),
	
	path('music/release_group/add',                release_group.add,              name='music_release_group_add'),
	path('music/release_group/view/<int:pk>',      release_group.view,             name='music_release_group_view'),
	path('music/release_group/edit/<int:pk>',      release_group.edit,             name='music_release_group_edit'),
	path('music/release_group/delete/<int:pk>',    release_group.Delete.as_view(), name='music_release_group_delete'),
	path('music/release_group/view/json/<int:pk>', release_group.view_json,        name='music_release_group_view_json'),
	
	path('music/contribution/add',                contribution.add,               name='music_contribution_add'),
	path('music/contribution/edit/<int:pk>',      contribution.edit,              name='music_contribution_edit'),
	path('music/contribution/delete/<int:pk>',    contribution.Delete.as_view(),  name='music_contribution_delete'),
	path('music/contribution/view/json/<int:pk>', contribution.view_json,         name='music_contribution_view_json'),
	path('music/contribution/view/releases/json/<int:pk>', contribution.view_releases_json, name='music_contribution_view_releases_json'),
	
	path('music/release/add',                release.add,              name='music_release_add'),
	path('music/release/view/<int:pk>',      release.view,             name='music_release_view'),
	path('music/release/edit/<int:pk>',      release.edit,             name='music_release_edit'),
	path('music/release/delete/<int:pk>',    release.Delete.as_view(), name='music_release_delete'),
	path('music/release/view/json/<int:pk>', release.view_json,        name='music_release_view_json'),
	
	path('music/torrent/add',               torrent.add,              name='music_torrent_add'),
	path('music/torrent/view/<int:pk>',     torrent.view,             name='music_torrent_view'),
	path('music/torrent/edit/<int:pk>',     torrent.edit,             name='music_torrent_edit'),
	path('music/torrent/delete/<int:pk>',   torrent.Delete.as_view(), name='music_torrent_delete'),
	path('music/torrent/download/<int:pk>', torrent.download,         name='music_torrent_download'),
	
	path('music/upload', upload.upload, name='music_upload'),
	
	path('music/latest', latest.latest_uploads, name='music_latest'),
]
