from django.contrib import admin

from .models import InboxThread, InboxMessage

admin.site.register(InboxThread)
admin.site.register(InboxMessage)
