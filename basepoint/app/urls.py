from django.urls import path
from .views import login_view, register_view,logout_view,create_worker,dashboard,activate

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('create-worker/', create_worker, name='create_worker'),
    path('', dashboard, name='dashboard'),
    path('activate/<str:token>/', activate, name='activate'),
    # Inne ścieżki URL dla innych widoków
]
