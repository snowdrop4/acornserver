from django.http import HttpRequest
from django.core.handlers.wsgi import WSGIRequest

from account.models import User


class AuthedWSGIRequest(WSGIRequest):
    user: User


# The type for the user object in a HttpRequest object is
# Union[User, AnonymousUser], which causes the type checker to throw an
# error if we try to use the user object as if it was always of type User
# (i.e., as if it was a real, logged in, user).
class AuthedHttpRequestBase(HttpRequest):
    user: User


AuthedHttpRequest = AuthedWSGIRequest | AuthedHttpRequestBase
