from django.urls import path, re_path

from . import views

app_name = "es"

urlpatterns = [
    path("", views.home, name="home"),
    path("publicacao_site/counter.php", views.counter_php, name="counter_php"),
    re_path(r"^publicacao_site/(?P<path>.+)$", views.publicacao_site, name="publicacao_site"),
]
