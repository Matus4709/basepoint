from django.urls import path
from .views import generateInvoice, addNewProduct, editProduct, allProducts, oneProduct, deleteProduct, login_view, register_view,logout_view,create_worker,dashboard,activate,reset_password_view,reset_password,workers_list,delete_worker, my_account,delete_account,edit_account
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
    path('invoices/', views.invoices, name='invoices'),
    path('statistics/', views.statistics, name='statistics'),
    path('', views.welcome, name='welcome'),
    path('orders-list/', views.orders_list, name='orders_list'),
    path('details-orders/<str:pk>/', views.details_orders, name='details_orders'),
    path('generate-pdf/<str:order_id>', views.generate_pdf, name='generate_pdf'),

    path('addNewProduct/', addNewProduct, name='addNewProduct'),
    path('editProduct/<id>', editProduct, name='editProduct'),
    path('allProducts/', allProducts, name='allProducts'),
    path('oneProducts/<id>', oneProduct, name='oneProduct'),
    path('deleteProduct/<id>', deleteProduct, name='deleteProduct'),

    path('contact/contact-list', views.contact_list, name="contact_list"),
    path('contact/contact-add', views.contact_add, name="contact_add"),
    path('contact/contact-chat/<int:id>', views.contact_chat, name="contact_chat"),

    path('support/',views.support_view, name="support_view"),
    path('support/contact-chat-support/<int:id>',views.contact_chat_support, name="contact_chat_support"),
    path('support/contact-end/<int:id>',views.end_contact, name="end_contact"),
    path('support/delete-chat/<int:id>',views.delete_chat, name="delete_chat"),
    
    path('generateInvoice/<id>', views.generateInvoice, name="generateInvoice")


    # Inne ścieżki URL dla innych widoków
]
