from django.urls import path

from . import views as root_views


app_name = 'root'
urlpatterns = [
	path('', root_views.homepage, name='homepage'),
]
