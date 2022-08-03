from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer

from inbox.models import InboxThread, InboxMessage


class InboxThreadSerializer(ModelSerializer):
	class Meta:
		model = InboxThread
		fields = ['title', 'sender', 'latest_message_datetime']


class InboxMessageSerializer(ModelSerializer):
	class Meta:
		model = InboxMessage
		fields = ['content', 'mod_date', 'pub_date']
