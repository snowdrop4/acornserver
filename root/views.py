from django.http import HttpResponse
from django.shortcuts import render

from root.type_annotations import AuthedHttpRequest

from .models import NewsArticle


def homepage(request: AuthedHttpRequest) -> HttpResponse:
    articles = NewsArticle.objects.order_by("-pub_date")[:5]

    return render(request, "root/homepage.html", {"articles": articles})


def about(request: AuthedHttpRequest) -> HttpResponse:
    return render(request, "root/about.html", {})
