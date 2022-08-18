# This is used in `torrent/views/music/upload.py` to simplify the process of using multiple forms that must
#   all correspond to each other and that may or may not be pre-filled and uneditable.

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from torrent.models.music import MusicArtist, MusicReleaseGroup, MusicContribution
from torrent.forms.music import upload


# The value for the HTML ID for each field when rendered in the template.
def auto_id() -> str:
	return 'upload-%s'


class BaseForm:
	def __init__(self, pk_provider: dict, pk_name, form_class):
		self.pk_provider = pk_provider
		self.pk_name = pk_name
		
		self.form_class = form_class
		self.form = None
		
		self.is_valid_override = False
	
	def instantiate(self, request: HttpRequest) -> None:
		# If the request method is a POST, construct a form and object based on the POSTed values.
		if request.method == 'POST':
			self.instantiate_post(request)
		# Else, just create an empty form.
		else:
			self.instantiate_empty()
	
	def instantiate_post(self, request: HttpRequest) -> None:
		self.form = self.form_class(request.POST, auto_id=auto_id())
	
	def instantiate_empty(self) -> None:
		self.form = self.form_class(auto_id=auto_id())
	
	# For `is_valid()` to return true, a form needs to be BOTH bound and valid. For a form to be considered bound
	#   by django, it must be constructed using POST data (given as the first position argument to the constructor).
	# 
	# If we construct a form with a primary key instead (by setting the named argument `instance` in the constructor),
	#   django will not consider the form bound.
	# 
	# This is a problem, because for our purposes the form should still be considered "valid" even though it wasn't "bound".
	# 
	# By overriding the `is_valid()` method, and then setting `is_valid_override` to True somewhere in our code at a later stage,
	#   we can create a form that will pretend to be valid even though it was constructed with a primary key and not POST data.
	def is_valid(self) -> bool:
		return self.is_valid_override or self.form.is_valid()
	
	def disable_all_fields(self) -> None:
		for (name, field) in self.form.fields.items():
			field.disabled = True


# Holds a hidden input field for an artist pk, which might be filled by javascript if the user autocompletes an artist.
class MusicModelPkForm(BaseForm):
	def __init__(self, pk_provider: dict):
		super().__init__(pk_provider, 'model_pk', upload.MusicModelPkForm)
	
	def instantiate_post(self, request: HttpRequest) -> None:
		super().instantiate_post(request)
		
		if self.form.is_valid():
			artist_pk_str = self.form.cleaned_data.get('artist_pk', '')
			
			if artist_pk_str != '':
				self.pk_provider['artist'] = artist_pk_str


# Partial class that extends BaseForm to let the form be instantiated from a PK provided by `pk_provider`.
# Any class inheriting this must implement `instantiate_pk`.
class MusicPkForm(BaseForm):
	def instantiate(self, request: HttpRequest) -> None:
		if self.pk_name in self.pk_provider:
			self.instantiate_pk(self.pk_provider[self.pk_name])
			self.is_valid_override = True
		else:
			super().instantiate(request)


# Class to group up a form based on a model with an object based on that same model.
class MusicObjectForm(MusicPkForm):
	def __init__(self, pk_provider: dict, pk_name, form_class, object_class):
		super().__init__(pk_provider, pk_name, form_class)
		
		self.object_class = object_class
		self.object = None
		
		# Whether the form was constructed from a primary key (used to tell us if we need to save the object or not)
		self.from_pk = False
		
	def instantiate_pk(self, pk: int) -> None:
		self.object = get_object_or_404(self.object_class, pk=pk)
		self.form = self.form_class(instance=self.object, auto_id=auto_id())
		self.disable_all_fields()
		self.from_pk = True
		
	def instantiate_post(self, request: HttpRequest) -> None:
		super().instantiate_post(request)
		
		if self.form.is_valid():
			self.object = self.form.save(commit=False)


class MusicContributionSelectForm(MusicPkForm):
	def __init__(self, pk_provider: dict):
		super().__init__(pk_provider, 'contribution', upload.MusicContributionSelectForm)
		
		self.object = None
		
	def populate_choices(self) -> None:
		if 'artist' in self.pk_provider:
			artist = get_object_or_404(MusicArtist, pk=self.pk_provider['artist'])
			
			choices = [('', '---------')]
			
			for i in artist.contributions.all():
				choices.append((i.pk, f"{i.get_contribution_type_display()} - {i.release_group}"))
			
			self.form.fields['contribution'].choices = choices
			
			if 'contribution' in self.pk_provider:
				self.form.initial['contribution'] = self.pk_provider['contribution']
		else:
			self.form.fields['contribution'].choices = [('', '---------')]
			self.disable_all_fields()
	
	def instantiate_pk(self, pk: int) -> None:
		super().instantiate_empty()
		
		self.object = get_object_or_404(MusicContribution, pk=pk)
		self.pk_provider['artist'] = self.object.artist.pk
		self.pk_provider['release_group'] = self.object.release_group.pk
		
		self.populate_choices()
	
	def instantiate_post(self, request: HttpRequest) -> None:
		super().instantiate_post(request)
		self.populate_choices()
		
		if self.form.is_valid():
			pk_str = self.form.cleaned_data.get('contribution', '')
			
			# Do nothing if the key doesn't exist, or its value is just ''.
			# (i.e., the blank '---------' option with value '' was selected).
			if pk_str != '':
				self.pk_provider['contribution'] = pk_str
				
				self.object = get_object_or_404(MusicContribution, pk=self.pk_provider['contribution'])
				self.pk_provider['artist'] = self.object.artist.pk
				self.pk_provider['release_group'] = self.object.release_group.pk
	
	def instantiate_empty(self) -> None:
		super().instantiate_empty()
		self.populate_choices()


class MusicReleaseSelectForm(MusicPkForm):
	def __init__(self, pk_provider: dict):
		super().__init__(pk_provider, 'release', upload.MusicReleaseSelectForm)
		
		self.object = None
	
	def populate_choices(self) -> None:
		if 'release_group' in self.pk_provider:
			release_group = get_object_or_404(MusicReleaseGroup, pk=self.pk_provider['release_group'])
			
			choices = [('', '---------')]
			
			for i in release_group.releases.all():
				choices.append((i.pk, str(i)))
			
			self.form.fields['release'].choices = choices
			
			if 'release' in self.pk_provider:
				self.form.initial['release'] = self.pk_provider['release']
		else:
			self.form.fields['release'].choices = [('', '---------')]
			self.disable_all_fields()
	
	def instantiate_pk(self, pk: int) -> None:
		super().instantiate_empty()
		self.populate_choices()
	
	def instantiate_post(self, request: HttpRequest) -> None:
		super().instantiate_post(request)
		self.populate_choices()
		
		if self.form.is_valid():
			pk_str = self.form.cleaned_data.get('release', '')
			
			# Do nothing if the key doesn't exist, or its value is just ''.
			# (i.e., the blank '---------' option with value '' was selected).
			if pk_str != '':
				self.pk_provider['release'] = pk_str
	
	def instantiate_empty(self) -> None:
		super().instantiate_empty()
		self.populate_choices()
