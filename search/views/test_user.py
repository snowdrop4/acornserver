from typing import cast

from django.test import TestCase, RequestFactory
from django.urls import reverse

from account.models import User
from search.views.user import search as user_search
from root.type_annotations import AuthedWSGIRequest
from account.account_randomiser import create_random_user


class TestUserQueries(TestCase):
    def setUp(self) -> None:
        self.requestFactory = RequestFactory()
        self.user = create_random_user()

        self.other_users = [
            User.objects.create_user(f"user{i}", f"user{i}@example.com", f"asdf{i}")
            for i in range(0, 10)
        ]

    def test_inbox_view(self) -> None:
        url = reverse("search:user_search")
        request = cast(
            AuthedWSGIRequest, self.requestFactory.get(url, {"username": "user"})
        )
        request.user = self.user

        with self.assertNumQueries(2):
            user_search(request)
