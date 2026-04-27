from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "es/home.html",
        {
            "page_title": "Escola Sabatina",
            "hide_global_header": False,
            "hide_global_footer": False,
        },
    )

