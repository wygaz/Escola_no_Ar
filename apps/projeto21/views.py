# apps/projeto21/views.py
from django.shortcuts import render

def landing(request):
    return render(request, "projeto21/landing.html")
