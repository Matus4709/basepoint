from django.urls import path
from .views import login_view, register_view,logout_view,create_worker,dashboard,activate,reset_password_view,reset_password,workers_list,delete_worker, my_account,delete_account,edit_account
from . import views
urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('create-worker/', create_worker, name='create_worker'),
    path('dashboard/', dashboard, name='dashboard'),
    path('activate/<str:token>/', activate, name='activate'),
    path('reset-password-confirm/<str:token>/', reset_password, name='reset_password_confirm'),
    path('login/reset_password_view/', reset_password_view, name='reset_password_view'),
    path('workers-list/', workers_list, name='workers-list'),
    path('workers-list/delete-worker/<int:id>', delete_worker, name='delete_worker'),
    path('my-account/', my_account, name='my_account'),
    path('my-account/delete-account/', delete_account, name='delete_account'),
    path('my-account/edit-account/', edit_account, name='edit_account'),
    path('my-account/edit-account-worker/', edit_account, name='edit_account'),

    path('get_access_token/', views.get_access_token, name='get_access_token'),

    path('offers/', views.offers, name='offers'),
    path('orders-list/', views.orders_list, name='orders-list'),
    path('invoices/', views.invoices, name='invoices'),
    path('statistics/', views.statistics, name='statistics'),
    path('', views.welcome, name='welcome'),

    # Inne ścieżki URL dla innych widoków
]
