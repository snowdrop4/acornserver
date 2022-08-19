from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from .models import ForumPost, ForumThread, ForumCategory

admin.site.register(ForumCategory, MPTTModelAdmin)
admin.site.register(ForumThread)
admin.site.register(ForumPost)
