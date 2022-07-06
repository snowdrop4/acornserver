from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
	model = get_user_model()
	
	fieldsets = (
		(_('Account'), {'fields': ('username', 'email', 'password', )}),
		(_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		(_('Dates'), {'fields': ('last_login', 'join_datetime')}),
		(_('Profile'), {'fields': ('user_bio', )}),
	)
	
	list_display = ('username', 'email', 'is_superuser', 'is_staff')
	list_filter = ('is_superuser', 'is_staff')
	
	search_fields = ('email',)
	ordering = ('email',)
	filter_horizontal = ()


admin.site.register(get_user_model(), UserAdmin)
