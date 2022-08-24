from django.urls import path

from global_login_required import login_not_required

from .views import bittorrent_announce

app_name = 'tracker'
urlpatterns = [
    path('<str:passkey>/bittorrent/<str:torrent_type>', login_not_required(bittorrent_announce), name='bittorrent_announce'),
]
