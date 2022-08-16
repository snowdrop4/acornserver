from django.urls import path
from django.contrib.auth import views as auth_views

from .views import InboxView, ThreadView


app_name = 'inbox'
urlpatterns = [
	path('',                     InboxView.as_view(),  name='inbox_view'),
	path('thread/view/<int:pk>', ThreadView.as_view(), name='thread_view')
]
