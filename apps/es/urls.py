from django.urls import path

from . import views

app_name = "es"

urlpatterns = [
    path("", views.home, name="home"),
]

