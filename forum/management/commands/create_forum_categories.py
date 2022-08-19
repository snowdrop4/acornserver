from typing import Any

from django.core.management.base import BaseCommand, CommandError

from forum.models import ForumCategory

categories = {
	'Tracker': {
		'News':        None,
		'Suggestions': None,
	},
	'Media': {
		'Music':      None,
		'Literature': None,
		'Television': None,
		'Film':       None,
		'Games':      None,
	},
	'Wissenschaft': {
		'Mathematics': None,
		'Physics':     None,
		'Chemistry':   None,
		'Biology':     None,
		'History':     None,
		'Philosophy':  None,
	},
	'Technology': {
		'Bittorrent':        None,
		'Programming':       None,
		'Operating Systems': None,
		'Hardware':          None,
	},
	'Support': {
		'Tracker Help': None,
		'Client Help':  None,
		'Bugs':         None,
	}
}


# To run: `python manage.py create_forum_categories`
class Command(BaseCommand):
	help = 'Create default forum categories'
	
	def handle(self, *args: Any, **options: Any) -> None:
		try:
			root = ForumCategory.objects.get(pk=1)
		except ForumCategory.DoesNotExist:
			root = ForumCategory(parent=None, title='root', folder=True)
			root.save()
		
		self.create_categories(categories, root)
	
	def create_categories(self, parent: dict, parent_obj: ForumCategory) -> None:
		for (k, v) in parent.items():
			if v is None:
				ForumCategory(parent=parent_obj, title=k, folder=False).save()
			else:
				child_obj = ForumCategory(parent=parent_obj, title=k, folder=True)
				child_obj.save()
				self.create_categories(v, child_obj)
