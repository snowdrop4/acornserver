from django.utils import timezone

from account.models import User
from root.utils.random import random_str, random_prose

from .models import InboxThread, InboxMessage


def create_random_message(
    thread: InboxThread, sender: User
) -> tuple[InboxMessage, dict]:
    now = timezone.now()

    message_data = {
        "message-thread": thread,
        "message-content": random_prose(),
        "message-mod_date": now,
        "message-pub_date": now,
        "message-sender": sender,
    }

    message_args = {a.removeprefix("message-"): b for (a, b) in message_data.items()}
    message = InboxMessage.objects.create(**message_args)

    return (message, message_data)


def create_random_thread(
    sender: User, receiver: User
) -> tuple[InboxThread, dict, InboxMessage, dict]:
    now = timezone.now()

    thread_data = {
        "thread-title": random_str(),
        "thread-sender": sender,
        "thread-receiver": receiver,
        "thread-latest_message_datetime": now,
    }

    thread_args = {a.removeprefix("thread-"): b for (a, b) in thread_data.items()}
    thread = InboxThread.objects.create(**thread_args)

    (message, message_data) = create_random_message(thread, sender)

    return (thread, thread_data, message, message_data)
