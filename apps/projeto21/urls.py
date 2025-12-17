# apps/projeto21/urls.py
from django.urls import path
from . import views

app_name = "projeto21"

urlpatterns = [
    path("", views.projeto21_home, name="home"),
    path("plano/", views.projeto21_home, name="plano"),  # alias (mesma view)
]