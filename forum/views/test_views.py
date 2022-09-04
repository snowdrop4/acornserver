import random
from typing import cast

from django.test import TestCase, RequestFactory
from django.urls import reverse

from forum.models import ForumThread, ForumCategory
from account.models import User
from forum.views.index import view as index_view
from forum.views.thread import view as thread_view
from forum.views.category import view as category_view
from root.type_annotations import AuthedWSGIRequest
from forum.forum_randomiser import (
    create_random_post,
    create_random_thread,
    create_random_category,
)
from account.account_randomiser import create_random_user


class TestQueries(TestCase):
    def setUp(self) -> None:
        self.requestFactory = RequestFactory()
        self.user = create_random_user()

        self.root = ForumCategory.objects.create(parent=None, title="root", folder=True)
        self.folders: list[ForumCategory] = []
        self.categories: list[ForumCategory] = []
        self.threads: list[ForumThread] = []
        self.posters: list[User] = [create_random_user() for i in range(0, 5)]

        # Create 3 top-level folder categories
        for i in range(0, 3):
            (parent, _) = child = create_random_category(self.root)
            self.folders.append(parent)

            # Create 3 non-folder children categories
            for i in range(0, 3):
                (child, _) = create_random_category(parent)
                self.categories.append(child)

                # Create 3 threads
                for i in range(0, 3):
                    op = random.choice(self.posters)
                    (thread, _) = create_random_thread(child, op)

                    # Create 3 posts
                    self.threads.append(thread)
                    (first_post, _) = create_random_post(child, thread, op)

                    for i in range(0, 2):
                        (post, _) = create_random_post(child, thread, op)

    def test_index_view_queries(self) -> None:
        url = reverse("forum:index_view")
        request = cast(AuthedWSGIRequest, self.requestFactory.get(url))
        request.user = self.user

        with self.assertNumQueries(4):
            index_view(request)

    def test_category_view_queries(self) -> None:
        url = reverse("forum:category_view", kwargs={"pk": self.categories[0].pk})
        request = cast(AuthedWSGIRequest, self.requestFactory.get(url))
        request.user = self.user

        with self.assertNumQueries(4):
            category_view(request, self.categories[0].pk)

    def test_thread_view_queries(self) -> None:
        url = reverse("forum:category_view", kwargs={"pk": self.threads[0].pk})
        request = cast(AuthedWSGIRequest, self.requestFactory.get(url))
        request.user = self.user

        with self.assertNumQueries(4):
            thread_view(request, self.threads[0].pk)

