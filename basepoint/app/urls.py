from django.urls import path
from .views import login_view, register_view,logout_view,create_worker,dashboard

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('create-worker/', create_worker, name='create_worker'),
    path('', dashboard, name='dashboard'),
    # Inne ścieżki URL dla innych widoków
]
