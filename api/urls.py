from django.urls import path

from .inbox.views import InboxThreadView, InboxMessagesView

app_name = 'api'
urlpatterns = [
    path('inbox/threads', InboxThreadView.as_view(), name='inbox_threads_view'),

    path('inbox/thread/<int:thread_pk>/messages',
        InboxMessagesView.as_view(),
        name='inbox_messages_view'
    ),
]
