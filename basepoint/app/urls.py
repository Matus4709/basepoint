from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('create-worker/', create_worker, name='create_worker'),
    path('', dashboard, name='dashboard'),
    path('activate/<str:token>/', activate, name='activate'),
    path('reset-password-confirm/<str:token>/', reset_password, name='reset_password_confirm'),
    path('login/reset_password_view/', reset_password_view, name='reset_password_view'),
    # Inne ścieżki URL dla innych widoków
    #######################################
    path('produkty/', getAllProducts, name='produkty'),
    path('produkty/<id>', getOneProduct),
    path('kategorie/', getAllCategory),
    path('kategorie/<id>', getOneCategory),
    path('dodajProdukt/<id>', addNewProduct),
]
