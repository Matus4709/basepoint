from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse,JsonResponse
import secrets
import os
from dotenv import load_dotenv
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
import json
from datetime import datetime
from .models import *
#from .forms import *

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            # Przekieruj użytkownika na stronę główną lub inną stronę
            return redirect('dashboard')
        else:
            # Wyświetl komunikat o błędzie logowania
            return render(request, 'login.html', {'error_message': 'Nieprawidłowy adres e-mail lub hasło'})
    
    return render(request, 'login.html')

def create_worker(request):
    user_type = request.user.user_type
    user_id = request.user.id
    with connection.cursor() as cursor:
                
                cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                account_data = [dict(zip(columns, row)) for row in rows]


    if user_type == 'owner':
        if request.method == 'POST':
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            name = request.POST.get('name')
            lastname = request.POST.get('lastname')
            user_type = 'employee'
            owner_user_id = request.user.id

            # Sprawdzenie, czy hasła są identyczne
            if password1 != password2:
                messages.error(request, 'Hasła nie są identyczne.')
                return redirect('register')
            
            # Zaszyfrowanie hasła
            hashed_password = make_password(password1)
            #Generowanie tokena aktywacyjnego
            token = secrets.token_hex(20)

            # Zapisanie danych do bazy danych
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO app_account (name, last_name, email, user_type, password, is_staff,is_superuser,owner_id_id, activation_token)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
                """, [name,lastname,email,user_type,hashed_password,False,False,owner_user_id,token])
            
            # Wysyłanie e-maila z potwierdzeniem
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            load_dotenv(os.path.join(BASE_DIR, '.env'))
            message = Mail(
                from_email='pichniarczykmarek@gmail.com',
                to_emails=email,
                subject='Potwierdzenie rejestracji - BASEPOINT',
                html_content='Witaj {email}, kliknij w ponizszy link, aby aktywowac konto:\n\n http://127.0.0.1:8000/activate/{token}/'.format(email=email, token=token))
            try:
                sg = SendGridAPIClient( os.getenv('API_SENDGRID'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)
            
            return HttpResponse("Link aktywacyjny został wysłany na adres mail.")
    else:
        return redirect('dashboard')

    return render(request, 'create_worker.html',{'user_type':user_type, 'account_data':account_data})

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

        #Generowanie tokena aktywacyjnego
        token = secrets.token_hex(20)
        
        # Zapisanie danych do bazy danych
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO app_account (password, email, country, NIP, company_name, phone_number, name_contact, city, address, postcode, is_superuser, user_type, is_staff,activation_token)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [hashed_password,email,country,NIP,company_name,phone_number,name_contact,city,address,postcode,False,'owner',False,token])
        
        # Wysyłanie e-maila z potwierdzeniem
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(BASE_DIR, '.env'))
        message = Mail(
            from_email='pichniarczykmarek@gmail.com',
            to_emails=email,
            subject='Potwierdzenie rejestracji - BASEPOINT',
            html_content='Witaj {email}, kliknij w ponizszy link, aby aktywowac konto:\n\n http://127.0.0.1:8000/activate/{token}/'.format(email=email, token=token))
        
        try:
            sg = SendGridAPIClient( os.getenv('API_SENDGRID'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)
        
        return HttpResponse("Sprawdź swój e-mail, aby aktywować konto.")
    
    return render(request, 'register.html')

def activate(request, token):
    with connection.cursor() as cursor:
        # Sprawdzenie czy istnieje użytkownik z podanym tokenem aktywacyjnym
        cursor.execute("SELECT * FROM app_account WHERE activation_token = %s", [token])
        user = cursor.fetchone()

        if not user:
            return HttpResponse("Nieprawidłowy token aktywacyjny")

        # Aktywacja konta
        cursor.execute("UPDATE app_account SET is_active = TRUE, activation_token = NULL WHERE activation_token = %s", [token])

    return HttpResponse("Twoje konto zostało aktywowane. Możesz się teraz <a href='/login'>zalogować</href>.")

def logout_view(request):
    logout(request)
    return redirect('welcome')  # Przykładowa nazwa strony logowania

def get_owner_id(email):
    with connection.cursor() as cursor:
        cursor.execute("SELECT owner_id_id FROM app_account WHERE email = %s", [email])
        row = cursor.fetchone()
        if row:
            owner_id = row[0]
            return owner_id
        else:
            return None

def dashboard(request):
    user_id = request.user.id
    user_type = None
    if request.user.is_authenticated:
        user_type = request.user.user_type
        if user_type == 'owner':
            with connection.cursor() as cursor:
                
                cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                account_data = [dict(zip(columns, row)) for row in rows]

            return render(request, 'dashboard.html', {'user_type': user_type,'account_data':account_data})
        
        elif user_type == 'employee':
            email = request.user.email
            owner_id = get_owner_id(email)
            user_id = request.user.id
            with connection.cursor() as cursor:
                
                cursor.execute("SELECT * FROM app_account WHERE %s = id;", [user_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                account_data = [dict(zip(columns, row)) for row in rows]
            

            return render(request, 'dashboard.html', {'user_type': user_type,'account_data':account_data})
        else:
            pass
    else:
        # Kod dla niezalogowanych użytkowników
        return redirect('login')
    
def reset_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        token = secrets.token_hex(20)

        # Zapisanie tokena resetu do bazy danych
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE app_account SET reset_password_token = (%s) WHERE email = (%s)
            """, [token,email])

        # Wysyłanie e-maila z potwierdzeniem
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(BASE_DIR, '.env'))
        message = Mail(
            from_email='pichniarczykmarek@gmail.com',
            to_emails=email,
            subject='Potwierdzenie rejestracji - BASEPOINT',
            html_content = 'Witaj {email}, kliknij w poniższy link, aby zresetować swoje hasło:\n\nhttp://127.0.0.1:8000/reset-password-confirm/{token}/'.format(email=email, token=token))
        try:
            sg = SendGridAPIClient( os.getenv('API_SENDGRID'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)
        
        return HttpResponse("Sprawdź swój e-mail, aby aktywować konto.")

    return render(request, 'reset_password_view.html')

def reset_password(request, token):
    with connection.cursor() as cursor:
        # Sprawdzenie czy istnieje użytkownik z podanym tokenem aktywacyjnym
        cursor.execute("SELECT email FROM app_account WHERE reset_password_token = %s", [token])
        user_mail = cursor.fetchone()

        if not user_mail:
            return HttpResponse("Nieprawidłowy token resetowania hasła!")

        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 != password2:
                messages.error(request, 'Hasła nie są identyczne.')
                return redirect('login')
            # Walidacja bezpieczeństwa hasła
            if len(password1) < 8:
                messages.error(request, 'Hasło jest za krótkie. Minimum 8 znaków.')
                return redirect('login')
            hashed_password = make_password(password1)
            # Zmiana hasła
            cursor.execute("UPDATE app_account SET password = %s, reset_password_token = NULL WHERE reset_password_token = %s", [hashed_password,token])
            return HttpResponse("Twoje hasło zostało zmienione. Możesz się teraz <a href='/login'>zalogować</href>.")
        
    return render(request, 'reset_password_confirm.html')
  
def workers_list(request):
    user_type = request.user.user_type
    user_id = request.user.id
    if user_type == 'owner':
        with connection.cursor() as cursor:
                
                cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                account_data = [dict(zip(columns, row)) for row in rows]

        with connection.cursor() as cursor:
                
                cursor.execute("SELECT * FROM `app_account` WHERE owner_id_id = %s", [user_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                workers_data = [dict(zip(columns, row)) for row in rows]
    else:
        return HttpResponse('Brak dostępu do tej opcji!')
    return render(request, 'workers_list.html',{'workers':workers_data,'account_data':account_data})

def delete_worker(request, id):
    user_type = request.user.user_type
    user_id = request.user.id
    if user_type == 'owner':
        with connection.cursor() as cursor:
                
                cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                account_data = [dict(zip(columns, row)) for row in rows]
        with connection.cursor() as cursor:
                cursor.execute("DELETE FROM `app_account` WHERE id =  %s", [id])
        return render(request, 'workers_list.html',{'account_data':account_data})
    

    else:
        return HttpResponse('Brak dostępu do tej opcji!')
    
def my_account(request):
    user_type = request.user.user_type
    user_id = request.user.id
    if user_type == 'owner' or user_type == 'employee':
        with connection.cursor() as cursor:
                
                cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                account_data = [dict(zip(columns, row)) for row in rows]
        return render(request,'my_account.html',{'account_data':account_data,'user_type':user_type})
    else:
        return HttpResponse('Brak dostępu!')
    
def delete_account(request):
    user_type = request.user.user_type
    if user_type == 'owner':
        user_id = request.user.id
        with connection.cursor() as cursor:
                cursor.execute("DELETE FROM `app_account` WHERE id =  %s", [user_id])
        return HttpResponse('Usunięto konto.')
    else:
        return HttpResponse('Brak dostępu!')
    
def edit_account(request):
    user_type = request.user.user_type
    user_id = request.user.id
    if user_type == 'owner':
        with connection.cursor() as cursor:
                
                cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                account_data = [dict(zip(columns, row)) for row in rows]

        if request.method == 'POST':
            email = request.POST.get('email')
            country = request.POST.get('country')
            NIP = request.POST.get('NIP')
            company_name = request.POST.get('company_name')
            address = request.POST.get('address')
            city = request.POST.get('city')
            postcode = request.POST.get('postcode')
            phone_number = request.POST.get('phone_number')
            name_contact = request.POST.get('name_contact')

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE app_account
                    SET email = %s, country = %s, NIP = %s, company_name = %s, address = %s, city = %s, postcode = %s, phone_number = %s, name_contact = %s
                    WHERE id = %s
                """, [email,country,NIP,company_name,address,city,postcode,phone_number,name_contact,user_id])
            return HttpResponse('Zaktualizowano dane.')

        return render(request, 'edit_account.html', {'account_data':account_data, 'user_type':user_type})
    if user_type == 'employee':
        with connection.cursor() as cursor:
                
                cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                account_data = [dict(zip(columns, row)) for row in rows]

        if request.method == 'POST':
            name = request.POST.get('name')
            last_name = request.POST.get('last_name')

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE app_account
                    SET name = %s, last_name = %s
                    WHERE id = %s
                """, [name,last_name,user_id])
            return HttpResponse('Zaktualizowano dane.')
        return render(request, 'edit_account_worker.html', {'account_data':account_data, 'user_type':user_type})
    else:    
        return HttpResponse('Brak dostępu!')
    
def orders_list(request):
    if request.user.is_authenticated:
        user_type = request.user.user_type
        user_id = request.user.id
        if user_type == 'owner':
            with connection.cursor() as cursor:
                    
                    cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                    rows = cursor.fetchall()
                    # Konwersja wyników z krotki na listę słowników
                    columns = [col[0] for col in cursor.description]
                    account_data = [dict(zip(columns, row)) for row in rows]
        #Pobieranie JSON 
        with open('app/sample_order_events.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        # with open('app/sample_order_events_allegro.json', 'w') as file:
        #     file.truncate(0)
        
    
        allegro_data = data.get('events', [])
        
        for event in data.get('events', []):
                total_amount = sum(
                    float(item['price']['amount']) * item['quantity'] 
                    for item in event['order']['lineItems']
                )
                total_amount = round(total_amount,2)
                event['total_amount'] = total_amount

                total_quantity = sum(
                    item['quantity']
                    for item in event['order']['lineItems']
                    )

                time_str = event['occurredAt']
                dt_object = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                formatted_time = dt_object.strftime('%d-%m-%Y %H:%M')
                
                event['occurredAt'] = formatted_time
                # status_order = event['order']['checkoutForms'][0]['fulfillment']['status']
                # if status_order == 'SENT' or 'PICKED_UP' or 'READY_FOR_PICKUP':
                #      status_order = 3
                # if status_order == 'NEW' or 'PROCESSING':
                #      status_order = 1
                # if status_order == 'READY_FOR_SHIPMENT':
                #      status_order = 2
                # if status_order == 'SUSPENDED.':
                #     status_order = 4


        #Sortowanie według daty od najstarszego zamówienie, aby odwrócić należy dodać na końcu ,reverse=True
        allegro_data = sorted(allegro_data, key=lambda x: datetime.strptime(x['occurredAt'], '%d-%m-%Y %H:%M'))

        #Paginacja strony
        paginator = Paginator(allegro_data,5)
        page = request.GET.get('page')
        try:
            allegro_data = paginator.page(page)
        except PageNotAnInteger:
            # Jeżeli 'page' nie jest liczbą całkowitą, pokaż pierwszą stronę
            allegro_data = paginator.page(1)
        except EmptyPage:
            # Jeżeli 'page' jest poza zakresem, pokaż ostatnią stronę
            allegro_data = paginator.page(paginator.num_pages)
        
        #Wyszukiwanie
        search_orders = request.GET.get('search_orders')
        if search_orders and allegro_data:
            allegro_data = [event for event in allegro_data if search_orders.lower() in event.get('order', {}).get('buyer', {}).get('email', '').lower()]
        
       # Filtrowanie po statusie
        status_filters = {
            'SENT': ['SENT', 'PICKED_UP', 'READY_FOR_PICKUP'],
            'NEW': ['NEW', 'PROCESSING'],
            'READY_FOR_SHIPMENT': ['READY_FOR_SHIPMENT'],
            'CANCELLED': ['SUSPENDED', 'CANCELLED']
            }
        status = request.GET.get('status')
        print(status)
        if status in status_filters:
            allowed_statuses = status_filters[status]
            allegro_data = [event for event in allegro_data if event['order']['checkoutForms'][0]['fulfillment']['status'] in allowed_statuses]

        context = {
            'account_data': account_data,
            'user_type': user_type,
            'allegro_data': allegro_data
        }

        return render(request,'orders/orders-list.html',context)
    else:
        return redirect('welcome')

def invoices(request):
    if request.user.is_authenticated:
        user_type = request.user.user_type
        user_id = request.user.id
        if user_type == 'owner':
            with connection.cursor() as cursor:
                    
                    cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                    rows = cursor.fetchall()
                    # Konwersja wyników z krotki na listę słowników
                    columns = [col[0] for col in cursor.description]
                    account_data = [dict(zip(columns, row)) for row in rows]
        context = {
            'account_data': account_data,
            'user_type': user_type
        }
        return render(request, 'orders/invoices.html',context)
    else:
       return redirect('welcome')
   
def statistics(request):
    if request.user.is_authenticated:
        user_type = request.user.user_type
        user_id = request.user.id
        if user_type == 'owner':
            with connection.cursor() as cursor:
                    
                    cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                    rows = cursor.fetchall()
                    # Konwersja wyników z krotki na listę słowników
                    columns = [col[0] for col in cursor.description]
                    account_data = [dict(zip(columns, row)) for row in rows]
        context = {
            'account_data': account_data,
            'user_type': user_type
        }
        return render(request, 'orders/statistics.html',context)
    else:
        return redirect('welcome')
    
def welcome(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'welcome.html')


#################################################################

def getAllCategory(request):
    getAllCategoryNames = Categories.objects.all()
    return HttpResponse(getAllCategoryNames)


def getOneCategory(request, id):
    getCategoryName = Categories.objects.get(pk=id)
    return HttpResponse(getCategoryName.name)


def getAllProducts(request):
    allProducts = Products.objects.all()
    data = {'produkty': allProducts}
    return render(request, 'products/allProductsView.html', data)


def getOneProduct(request, id):
    getProduct = Products.objects.get(pk=id)
    data = {'getProduct': getProduct}
    return render(request, 'products/specificProduct.html', data)


def addNewProduct(request): #id
    allCategories = Categories.objects.all()
    data = {'kategorie': allCategories}
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        category = request.POST.get('category')
        user_id = request.user.id

        newProduct = Products(name=name, description=description, quantity=quantity, price=price,
                              accounts_account_id_id=user_id, category_id=category)
        newProduct.save()

    return render(request, 'products/addNewProduct.html', data)





def editProduct(request, id):
    allCategories = Categories.objects.all()
<<<<<<< HEAD:basepoint/app/views.py
    product = get_object_or_404(Products, pk=id)


    context = {
        'produkt': product,
        'kategorie': allCategories
    }

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.quantity = request.POST.get('quantity')
        product.price = request.POST.get('price')
        product.category = request.POST.get('Categories.name')
        category_id = request.POST.get('category')
        product.category_id = category_id
        user_id = request.user.id

        product.save()

    return render(request, 'products/editProduct.html', context)
=======
    produkt = get_object_or_404(Products, pk=id)
    if request.method == 'POST':
        produkt.name = request.POST.get('name')
        produkt.description = request.POST.get('description')
        produkt.quantity = request.POST.get('quantity')
        produkt.price = request.POST.get('price')
        produkt.save()

    return render(request, 'products/editProduct.html', {'product': produkt})
>>>>>>> 841b598584583d6ce110321bf357b754fd59f1e1:basepoint/basepoint/app/views.py








def deleteProduct(request):
    product = get_object_or_404(Products, pk=id)
    if request.method == 'POST':
        product.delete()
        return redirect(getAllProducts)

    return render(request, 'deleteDefinitely.html')













