from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegisterForm
from django.db import connection
from django.contrib.auth.hashers import make_password

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)  # Użyj nazwy pola 'username'
        if user is not None:
            login(request, user)
            # Przekieruj użytkownika na odpowiednią stronę
            return redirect('login')  # Przykładowa nazwa strony głównej
        else:
            messages.error(request, 'Nieprawidłowe dane logowania.')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        NIP = request.POST.get('NIP')
        company_name = request.POST.get('company_name')
        country = request.POST.get('country')
        phone_number = request.POST.get('phone_number')
        name_contact = request.POST.get('name_contact')
        postcode = request.POST.get('postcode')
        city = request.POST.get('city')
        address = request.POST.get('address')
        
        # Sprawdzenie, czy hasła są identyczne
        if password1 != password2:
            messages.error(request, 'Hasła nie są identyczne.')
            return redirect('register')
        
         # Zaszyfrowanie hasła
        hashed_password = make_password(password1)
        
        # Zapisanie danych do bazy danych
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO app_account (email, password, NIP, company_name, country, phone_number, name_contact ,address ,city ,postcode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [email, hashed_password, NIP, company_name,country,phone_number,name_contact,address,city,postcode])
        
        messages.success(request, f'Konto zostało utworzone dla {email}. Możesz się teraz zalogować.')
        return redirect('login')
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Przykładowa nazwa strony logowania
