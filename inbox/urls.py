from django.urls import path

from .views import InboxView, ThreadReplyView, ThreadCreateView

app_name = "inbox"
urlpatterns = [
    path("", InboxView.as_view(), name="inbox_view"),
    path("thread/create", ThreadCreateView.as_view(), name="thread_create"),
    path("thread/view/<int:pk>", ThreadReplyView.as_view(), name="thread_view"),
]
