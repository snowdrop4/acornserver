from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from .models import ForumCategory, ForumThread, ForumPost

admin.site.register(ForumCategory, MPTTModelAdmin)
admin.site.register(ForumThread)
admin.site.register(ForumPost)
