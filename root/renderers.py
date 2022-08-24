from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def render_http_bad_request(request: HttpRequest, message: str) -> HttpResponse:
    status_code_number = 400

    template_args = {
        "message": message,
        "status_code_number": status_code_number,
        "status_code_text": "Bad Request",
    }

    return render(
        request, "root/error_pages/base.html", template_args, status=status_code_number
    )


def render_http_forbidden(request: HttpRequest, message: str) -> HttpResponse:
    status_code_number = 403

    template_args = {
        "message": message,
        "status_code_number": status_code_number,
        "status_code_text": "Forbidden",
    }

    return render(
        request, "root/error_pages/base.html", template_args, status=status_code_number
    )


def render_http_not_found(request: HttpRequest, message: str) -> HttpResponse:
    status_code_number = 404

    template_args = {
        "message": message,
        "status_code_number": status_code_number,
        "status_code_text": "Not Found",
    }

    return render(
        request, "root/error_pages/base.html", template_args, status=status_code_number
    )


def render_http_server_error(request: HttpRequest, message: str) -> HttpResponse:
    status_code_number = 500

    template_args = {
        "message": message,
        "status_code_number": status_code_number,
        "status_code_text": "Internal Server Error",
    }

    return render(
        request, "root/error_pages/base.html", template_args, status=status_code_number
    )
