from typing import Any

from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator

from root import renderers
from account.models import User
from search.forms.user import UserSearchForm
from root.type_annotations import AuthedHttpRequest
from root.utils.get_parameters import fill_typed_get_parameters


def search(request: AuthedHttpRequest) -> HttpResponse:
    try:
        get_params = fill_typed_get_parameters(
            request, {"page": (False, int, "must be an integer")}
        )
    except ValueError as e:
        return renderers.render_http_bad_request(request, str(e))

    form = UserSearchForm(request.GET)

    template_args: dict[str, Any] = {"form": form}

    if form.is_valid() and (username := form.cleaned_data["username"]):
        query = User.objects.filter(username__icontains=username).order_by("pk")
        paginator = Paginator(query, 5)
        template_args["page"] = paginator.get_page(get_params.get("page", 1))

    return render(request, "search/user.html", template_args)
