from django.shortcuts import render
from django.http import HttpResponse
from .models import Products

# Create your views here.
def getAll(request):
    zapytanie = Products.objects.all()
    return HttpResponse(zapytanie)
