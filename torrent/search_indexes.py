# Haystack automatically searches each app directory for a 'search_indexes.py' file.

from haystack import indexes

from .models.music import MusicArtist, MusicReleaseGroup


# Every field instantiated with the named argument 'document=True' should have the same variable name.
# Every one of our classes here must have one field with 'document=True'.
# This is the data that Haystack will check when querying the index for a match.
# The name we'll use for all of these variables will be 'text'.
# 
# Any other fields we add to the index (apart from the one with `document=True`) will be to enable our search engine
# to return detailed information about the results without having to hit the main database itself (only the index).
# This is a performance optimisation.

class MusicArtistIndex(indexes.SearchIndex, indexes.Indexable):
	# model_attr: the attribute from the model that will be added to the index
	text = indexes.NgramField(document=True, model_attr='name')
	
	def get_model(self):
		return MusicArtist


class MusicReleaseGroupIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.NgramField(document=True, model_attr='name')
	
	group_type = indexes.MultiValueField(model_attr='group_type')
	
	def get_model(self):
		return MusicReleaseGroup
