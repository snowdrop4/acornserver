# Wrapping the django messages framework so we can work with our own types of messages.
# The standard message types aren't so good.

from django.http import HttpRequest
from django.contrib import messages


# Success (Something completed)
def success(request: HttpRequest, msg: str) -> None:
    messages.add_message(
        request, messages.INFO, msg, extra_tags="success", fail_silently=True
    )


# Failure (something commenced but couldn't complete)
def failure(request: HttpRequest, msg: str) -> None:
    messages.add_message(
        request, messages.INFO, msg, extra_tags="failure", fail_silently=True
    )


# Creation (something added or created)
def creation(request: HttpRequest, msg: str) -> None:
    messages.add_message(
        request, messages.INFO, msg, extra_tags="creation", fail_silently=True
    )


# Deletion (something removed or deleted)
def deletion(request: HttpRequest, msg: str) -> None:
    messages.add_message(
        request, messages.INFO, msg, extra_tags="deletion", fail_silently=True
    )


# Modification (something changed or modified)
def modification(request: HttpRequest, msg: str) -> None:
    messages.add_message(
        request, messages.INFO, msg, extra_tags="modification", fail_silently=True
    )


# Warning (something one ought to be careful of)
def warning(request: HttpRequest, msg: str) -> None:
    messages.add_message(
        request, messages.INFO, msg, extra_tags="warning", fail_silently=True
    )


# Error (something went wrong)
def error(request: HttpRequest, msg: str) -> None:
    messages.add_message(
        request, messages.INFO, msg, extra_tags="error", fail_silently=True
    )


# Information (something miscellaneous)
def information(request: HttpRequest, msg: str) -> None:
    messages.add_message(
        request, messages.INFO, msg, extra_tags="information", fail_silently=True
    )
