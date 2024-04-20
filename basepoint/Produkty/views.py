from django.shortcuts import render
from django.http import HttpResponse
from .models import *

# Create your views here.


def getAllCategory(request):
    getAllCategoryNames = Kategories.objects.all()
    return HttpResponse(getAllCategoryNames)


def getOneCategory(request, id): #id
    #getAllCategoryName = Kategories.objects.all() #  (request) ->, -> (getAllCategoryName) (to co będzie wyswietlane decydujemy w modelu w tym przypadku name)
    #jeden = Kategories.objects.get(pk=1) #kategoria o danym id
    #getCategoryProducts = Products.objects.filter(kategory=5) # Pobierz produkty pod daną kategorią
    getCategoryName = Kategories.objects.get(pk=id)
    return HttpResponse(getCategoryName.name)


def getAllProducts(request):
    allProducts = Products.objects.all()
    data = {'produkty': allProducts}
    return render(request, 'allProductsView.html', data)


def getOneProduct(request, id):
    getProduct = Products.objects.get(pk=id)
    data = {'getProduct': getProduct}
    return render(request,'specificProduct.html',data)















