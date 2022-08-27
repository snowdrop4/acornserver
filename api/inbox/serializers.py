from rest_framework.serializers import ModelSerializer

from inbox.models import InboxThread, InboxMessage


class InboxThreadSerializer(ModelSerializer):
    class Meta:
        model = InboxThread
        fields = ["id", "title", "sender", "latest_message_datetime"]


class InboxMessageSerializer(ModelSerializer):
    class Meta:
        model = InboxMessage
        fields = ["id", "content", "mod_date", "pub_date"]
