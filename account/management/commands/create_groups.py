from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from torrent.models.music import (
	MusicArtist, MusicReleaseGroup, MusicContribution, MusicRelease, MusicTorrent
)

groups = {
	'Admin': {
		MusicArtist:       ['add', 'change', 'delete', 'view'],
		MusicReleaseGroup: ['add', 'change', 'delete', 'view'],
		MusicContribution: ['add', 'change', 'delete', 'view'],
		MusicRelease:      ['add', 'change', 'delete', 'view'],
		MusicTorrent:      ['add', 'change', 'delete', 'view'],
	},
	'Member': {
		MusicArtist:       ['add', 'view'],
		MusicReleaseGroup: ['add', 'view'],
		MusicContribution: ['add', 'view'],
		MusicRelease:      ['add', 'view'],
		MusicTorrent:      ['add', 'view'],
	}
}


# To run: `python manage.py create_groups`
class Command(BaseCommand):
	help = 'Create default user groups'
	
	def handle(self, *args, **options):
		for (group_name, models) in groups.items():
			
			# Create the group, if it doesn't exist
			group, _ = Group.objects.get_or_create(name=group_name)
			
			# Clear old permissions, if any
			group.permissions.set([])
			
			for (model, verbs) in models.items():
				for verb in verbs:
					# Django automatically generates permission names in the form
					#   `add_model`, `change_model`, `delete_model`, and `view_model`,
					#   where `model` is the name of the model.
					permission_codename = f'{verb}_{model._meta.model_name}'
					
					# Get the ContentType of the model for the permission we are trying to set.
					# 
					# We can use the ContentType of the model to disambiguate in case there happens
					#   to be two models from different apps that have the same name.
					permission_content_type = ContentType.objects.get_for_model(model)
					
					try:
						# Get the actual Permission object we need, ...
						permission = Permission.objects.get(
							codename=permission_codename,
							content_type=permission_content_type
						)
						
						# ... and add it to the group.
						group.permissions.add(permission)
					except Permission.DoesNotExist:
						raise CommandError(f'Permission \'{permission_codename}\' does not exist.')