from django.urls import path
from . import views

app_name = "projeto21"

urlpatterns = [
    path("", views.landing, name="landing"),
]