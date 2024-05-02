from django.shortcuts import render, redirect
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
        if user_type == 'employee':
              with connection.cursor() as cursor:
                 cursor.execute("SELECT owner_id_id FROM app_account WHERE id = %s", [user_id])
                 rows = cursor.fetchall()
                 columns = [col[0] for col in cursor.description]
                 owner_id = [dict(zip(columns, row)) for row in rows]
        else:
            owner_id = user_id
        with connection.cursor() as cursor:            
                    cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                    rows = cursor.fetchall()
                    # Konwersja wyników z krotki na listę słowników
                    columns = [col[0] for col in cursor.description]
                    account_data = [dict(zip(columns, row)) for row in rows]
        #Pobieranie JSON 
        with open('app/sample_order_events.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        total_amount = 0
        amount_products = 0
            # Pętla po wszystkich zdarzeniach
        for event in data['events']:
                event_id = event['id']
                event_type = event['type']
                event_occurred_at = event['occurredAt']
                order_details = event['order']
                # Formularze płatności
                checkout_forms = order_details['checkoutForms']
                for form in checkout_forms:
                    delivery = form['delivery']['method']['name']
                    buyer_details = order_details['buyer']
                    buyer_id = buyer_details['id']
                    form_id = form['id']
                    message_to_seller = form['messageToSeller']
                    
                    buyer_details_in_form = form['buyer']
                    buyer_id_in_form = buyer_details_in_form['id']
                    buyer_email_in_form = buyer_details_in_form['email']
                    buyer_login_in_form = buyer_details_in_form['login']
                    buyer_first_name = buyer_details_in_form['firstName']
                    buyer_last_name = buyer_details_in_form['lastName']
                    buyer_company_name = buyer_details_in_form['companyName']
                    buyer_is_guest_in_form = buyer_details_in_form['guest']
                    buyer_personal_identity = buyer_details_in_form['personalIdentity']
                    buyer_phone_number = buyer_details_in_form['phoneNumber']
                    buyer_language_in_form = buyer_details_in_form['preferences']['language']
                    buyer_street = buyer_details_in_form['address']['street']
                    buyer_city = buyer_details_in_form['address']['city']
                    buyer_post_code = buyer_details_in_form['address']['postCode']
                    buyer_country_code = buyer_details_in_form['address']['countryCode']

                    # #Dodawnie do app_customers
                    # with connection.cursor() as cursor:
                    #     cursor.execute("""
                    #         SELECT id FROM app_customers WHERE id = %s
                    #         """, [buyer_id])
                    #     result = cursor.fetchone()
                    #     if result:
                    #         print('Customer already exists')
                    #     else:
                    #         cursor.execute("""
                    #             INSERT INTO app_customers (id, first_name, last_name, email, phone)
                    #             VALUES (%s, %s, %s, %s, %s);
                    #             """,[buyer_id, buyer_first_name, buyer_last_name, buyer_email_in_form, buyer_phone_number])
                            
                    # # Dodawnie do app_custumer_addreses
                    # with connection.cursor() as cursor:
                    #     cursor.execute("""
                    #         SELECT id FROM app_custumers_addresses WHERE custumer_id_id = %s
                    #         """, [buyer_id])
                    #     result = cursor.fetchone()
                    #     if result:
                    #         print('Customer already exists')
                    #     else:
                    #         with connection.cursor() as cursor:
                    #             cursor.execute("""
                    #                 INSERT INTO app_custumers_addresses (country, city, address, postal_code, custumer_id_id)
                    #                 VALUES (%s, %s, %s, %s, %s);
                    #                 """, [buyer_country_code, buyer_city, buyer_street, buyer_post_code, buyer_id])
                
                # Szczegóły zamówienia
                order_details = event['order']
                seller_id = order_details['seller']['id']
                checkout_forms = order_details['checkoutForms']
                for form in checkout_forms:
                    messageToSeller = form['messageToSeller']
                    buyer_details = order_details['buyer']
                    buyer_id = buyer_details['id']
                    buyer_email = buyer_details['email']
                    buyer_login = buyer_details['login']
                    buyer_is_guest = buyer_details['guest']
                    buyer_language = buyer_details['preferences']['language']
                    payment_details = form['payment']
                    payment_id = payment_details['id']
                    payment_type = payment_details['type']
                    payment_provider = payment_details['provider']
                    payment_finished_at = payment_details['finishedAt']
                    paid_amount = payment_details['paidAmount']['amount']
                    paid_currency = payment_details['paidAmount']['currency']
                    
                    status = form['fulfillment']['status']    
                    total_amount =  total_amount + float(paid_amount)
                    total_amount = round(total_amount,2)
                    event_occurred_at = datetime.strptime(event_occurred_at, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
                    
                # # Dodawanie app_orders
                # with connection.cursor() as cursor:
                #         cursor.execute("""
                #             SELECT id FROM app_orders WHERE id = %s
                #             """, [event_id])
                #         result = cursor.fetchone()
                #         if result:
                #             print('Order already exists')
                #         else:
                #             cursor.execute("""
                #                 INSERT INTO app_orders (id, order_date, amount_products, summary_price, statues_status_id, seller_id, customer_id, messageToSeller)
                #                 VALUES (%s,%s,%s,%s,%s,%s,%s);
                #                 """,[event_id,event_occurred_at,amount_products,total_amount,status,owner_id,buyer_id,messageToSeller])
                            
                # Pozycje zamówienia
                line_items = order_details['lineItems']
                for line_item in line_items:
                    line_item_id = line_item['id']
                    offer_id = line_item['offer']['id']
                    offer_name = line_item['offer']['name']
                    offer_external_id = line_item['offer']['external']['id']
                    quantity = line_item['quantity']
                    original_price_amount = line_item['originalPrice']['amount']
                    original_price_currency = line_item['originalPrice']['currency']
                    price_amount = line_item['price']['amount']
                    price_currency = line_item['price']['currency']
                    bought_at = line_item['boughtAt']

                    id_item = line_item['id']
                    item_name = line_item['offer']['name']
                    item_price = line_item['originalPrice']['amount']
                    items_price = line_item['price']['amount']
                    item_quantity = line_item['quantity']
                    item_description = line_item['offer']['description']
                    item_graphic_url = line_item['offer']['graphic_url']
                    item_category = line_item['offer']['category']

                    amount_products = amount_products + quantity
                    
                    # # Dodawanie app_products
                    # with connection.cursor() as cursor:
                    #     cursor.execute("""
                    #         SELECT id FROM app_products WHERE id = %s
                    #         """, [id_item])
                    #     result = cursor.fetchone()
                    #     if result:
                    #         print('Product already exists')
                    #     else:
                    #         cursor.execute("""
                    #             INSERT INTO app_products (id,name, description, price, quantity, category, graphic_url, accounts_account_id_id)
                    #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    #             """, [id_item,item_name,item_description,item_price,item_quantity,item_category,item_graphic_url,owner_id])
                
                
                    # # Dodawnie do app_product_has_orders
                    # with connection.cursor() as cursor:
                    #      cursor.execute("""
                    #                     INSERT INTO app_product_has_orders (orders_order_id_id, products_product_id_id,quantity)
                    #                     VALUES (%s, %s, %s);
                    #                     """, [event_id,id_item,quantity])
                    
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT app_orders.id as order_id, app_customers.first_name as customer_name, app_customers.email as customer_email,
                GROUP_CONCAT(CONCAT(app_products.name, ' (', app_product_has_orders.quantity, ')') SEPARATOR ', ') as products,
                SUM(app_products.price * app_product_has_orders.quantity) as total_price,
                app_orders.statues_status_id as status,
                app_orders.delivery as delivery,
                app_orders.order_date as order_date
                FROM app_orders 
                JOIN app_customers ON app_orders.customer_id = app_customers.id
                JOIN app_custumers_addresses ON app_custumers_addresses.custumer_id_id = app_customers.id
                JOIN app_product_has_orders ON app_orders.id = app_product_has_orders.orders_order_id_id
                JOIN app_products ON app_product_has_orders.products_product_id_id = app_products.id
                WHERE app_orders.seller_id = %s
                GROUP BY app_orders.id
                ORDER BY app_orders.order_date DESC;
            """, [owner_id])

            allegro_data = cursor.fetchall()
                                                                        
    #Wyszukiwanie
    search_orders = request.GET.get('search_orders')
    search_orders = str(search_orders) if search_orders else '%'  # Jeśli nie ma wartości, ustaw na dowolny ciąg

    if search_orders and allegro_data:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT app_orders.id as order_id, app_customers.first_name as customer_name, app_customers.email as customer_email,
                GROUP_CONCAT(CONCAT(app_products.name, ' (', app_product_has_orders.quantity, ')') SEPARATOR ', ') as products,
                SUM(app_products.price * app_product_has_orders.quantity) as total_price,
                app_orders.statues_status_id as status,
                app_orders.delivery as delivery,
                app_orders.order_date as order_date
                FROM app_orders 
                JOIN app_customers ON app_orders.customer_id = app_customers.id
                JOIN app_custumers_addresses ON app_custumers_addresses.custumer_id_id = app_customers.id
                JOIN app_product_has_orders ON app_orders.id = app_product_has_orders.orders_order_id_id
                JOIN app_products ON app_product_has_orders.products_product_id_id = app_products.id
                WHERE app_orders.seller_id = %s AND app_customers.email LIKE %s
                GROUP BY app_orders.id
                ORDER BY app_orders.order_date DESC;
            """, [owner_id, f"%{search_orders}%"])
            allegro_data = cursor.fetchall()
        
        # Filtrowanie po statusie
        status_filters = {
            'SENT': ['SENT', 'PICKED_UP', 'READY_FOR_PICKUP'],
            'NEW': ['NEW', 'PROCESSING'],
            'READY_FOR_SHIPMENT': ['READY_FOR_SHIPMENT'],
            'CANCELLED': ['SUSPENDED', 'CANCELLED']
            }
        status = request.GET.get('status')
        print(status)
        if status == 'SENT' or 'PICKED_UP' or 'READY_FOR_PICKUP':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT app_orders.id as order_id, app_customers.first_name as customer_name, app_customers.email as customer_email,
                    GROUP_CONCAT(CONCAT(app_products.name, ' (', app_product_has_orders.quantity, ')') SEPARATOR ', ') as products,
                    SUM(app_products.price * app_product_has_orders.quantity) as total_price,
                    app_orders.statues_status_id as status,
                    app_orders.delivery as delivery,
                    app_orders.order_date as order_date
                    FROM app_orders 
                    JOIN app_customers ON app_orders.customer_id = app_customers.id
                    JOIN app_custumers_addresses ON app_custumers_addresses.custumer_id_id = app_customers.id
                    JOIN app_product_has_orders ON app_orders.id = app_product_has_orders.orders_order_id_id
                    JOIN app_products ON app_product_has_orders.products_product_id_id = app_products.id
                    WHERE app_orders.seller_id = %s AND app_orders.statues_status_id LIKE %s
                    GROUP BY app_orders.id
                    ORDER BY app_orders.order_date DESC;
                """, [owner_id, status])
                allegro_data = cursor.fetchall()
        if status == 'NEW' or 'PROCESSING':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT app_orders.id as order_id, app_customers.first_name as customer_name, app_customers.email as customer_email,
                    GROUP_CONCAT(CONCAT(app_products.name, ' (', app_product_has_orders.quantity, ')') SEPARATOR ', ') as products,
                    SUM(app_products.price * app_product_has_orders.quantity) as total_price,
                    app_orders.statues_status_id as status,
                    app_orders.delivery as delivery,
                    app_orders.order_date as order_date
                    FROM app_orders 
                    JOIN app_customers ON app_orders.customer_id = app_customers.id
                    JOIN app_custumers_addresses ON app_custumers_addresses.custumer_id_id = app_customers.id
                    JOIN app_product_has_orders ON app_orders.id = app_product_has_orders.orders_order_id_id
                    JOIN app_products ON app_product_has_orders.products_product_id_id = app_products.id
                    WHERE app_orders.seller_id = %s AND app_orders.statues_status_id LIKE %s
                    GROUP BY app_orders.id
                    ORDER BY app_orders.order_date DESC;
                """, [owner_id, status])
                allegro_data = cursor.fetchall()
        if status == 'READY_FOR_SHIPMENT':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT app_orders.id as order_id, app_customers.first_name as customer_name, app_customers.email as customer_email,
                    GROUP_CONCAT(CONCAT(app_products.name, ' (', app_product_has_orders.quantity, ')') SEPARATOR ', ') as products,
                    SUM(app_products.price * app_product_has_orders.quantity) as total_price,
                    app_orders.statues_status_id as status,
                    app_orders.delivery as delivery,
                    app_orders.order_date as order_date
                    FROM app_orders 
                    JOIN app_customers ON app_orders.customer_id = app_customers.id
                    JOIN app_custumers_addresses ON app_custumers_addresses.custumer_id_id = app_customers.id
                    JOIN app_product_has_orders ON app_orders.id = app_product_has_orders.orders_order_id_id
                    JOIN app_products ON app_product_has_orders.products_product_id_id = app_products.id
                    WHERE app_orders.seller_id = %s AND app_orders.statues_status_id LIKE %s
                    GROUP BY app_orders.id
                    ORDER BY app_orders.order_date DESC;
                """, [owner_id, status])
                allegro_data = cursor.fetchall()
        if status == 'SUSPENDED' or 'CANCELLED':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT app_orders.id as order_id, app_customers.first_name as customer_name, app_customers.email as customer_email,
                    GROUP_CONCAT(CONCAT(app_products.name, ' (', app_product_has_orders.quantity, ')') SEPARATOR ', ') as products,
                    SUM(app_products.price * app_product_has_orders.quantity) as total_price,
                    app_orders.statues_status_id as status,
                    app_orders.delivery as delivery,
                    app_orders.order_date as order_date
                    FROM app_orders 
                    JOIN app_customers ON app_orders.customer_id = app_customers.id
                    JOIN app_custumers_addresses ON app_custumers_addresses.custumer_id_id = app_customers.id
                    JOIN app_product_has_orders ON app_orders.id = app_product_has_orders.orders_order_id_id
                    JOIN app_products ON app_product_has_orders.products_product_id_id = app_products.id
                    WHERE app_orders.seller_id = %s AND app_orders.statues_status_id LIKE %s
                    GROUP BY app_orders.id
                    ORDER BY app_orders.order_date DESC;
                """, [owner_id, status])
                allegro_data = cursor.fetchall()
        if status is None:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT app_orders.id as order_id, app_customers.first_name as customer_name, app_customers.email as customer_email,
                    GROUP_CONCAT(CONCAT(app_products.name, ' (', app_product_has_orders.quantity, ')') SEPARATOR ', ') as products,
                    SUM(app_products.price * app_product_has_orders.quantity) as total_price,
                    app_orders.statues_status_id as status,
                    app_orders.delivery as delivery,
                    app_orders.order_date as order_date
                    FROM app_orders 
                    JOIN app_customers ON app_orders.customer_id = app_customers.id
                    JOIN app_custumers_addresses ON app_custumers_addresses.custumer_id_id = app_customers.id
                    JOIN app_product_has_orders ON app_orders.id = app_product_has_orders.orders_order_id_id
                    JOIN app_products ON app_product_has_orders.products_product_id_id = app_products.id
                    WHERE app_orders.seller_id = %s
                    GROUP BY app_orders.id
                    ORDER BY app_orders.order_date DESC;
                """, [owner_id])

                allegro_data = cursor.fetchall()
             
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
        context = {
            'account_data': account_data,
            'user_type': user_type,
            'allegro_data': allegro_data
            # 'allegro_data': result
        }

        return render(request,'orders/orders-list.html',context)
    else:
        return redirect('welcome')

def details_orders(request,pk):
    if request.user.is_authenticated:
        user_type = request.user.user_type
        user_id = request.user.id
        if user_type == 'employee':
              with connection.cursor() as cursor:
                 cursor.execute("SELECT owner_id_id FROM app_account WHERE id = %s", [user_id])
                 rows = cursor.fetchall()
                 columns = [col[0] for col in cursor.description]
                 owner_id = [dict(zip(columns, row)) for row in rows]
        else:
            owner_id = user_id


        with connection.cursor() as cursor:
                    
                    cursor.execute("SELECT * FROM app_account WHERE id = %s", [user_id])
                    rows = cursor.fetchall()
                    # Konwersja wyników z krotki na listę słowników
                    columns = [col[0] for col in cursor.description]
                    account_data = [dict(zip(columns, row)) for row in rows]
        
        pk=pk
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT app_orders.id as order_id, app_customers.first_name as customer_name, app_customers.email as customer_email,
                GROUP_CONCAT(CONCAT(app_products.name, ' (', app_product_has_orders.quantity, ')') SEPARATOR ', ') as products,
                SUM(app_products.price * app_product_has_orders.quantity) as total_price,
                app_orders.statues_status_id as status,
                app_orders.delivery as delivery,
                app_orders.order_date as order_date,
                app_custumers_addresses.*,
                app_customers.*,
                app_products.*,
                app_orders.messageToSeller
                FROM app_orders 
                JOIN app_customers ON app_orders.customer_id = app_customers.id
                JOIN app_custumers_addresses ON app_custumers_addresses.custumer_id_id = app_customers.id
                JOIN app_product_has_orders ON app_orders.id = app_product_has_orders.orders_order_id_id
                JOIN app_products ON app_product_has_orders.products_product_id_id = app_products.id
                WHERE app_orders.seller_id = %s AND app_orders.id = %s;
            """, [owner_id, pk])

            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            allegro_data = [dict(zip(columns, row)) for row in rows]
            print(allegro_data)

        context = {
            'account_data': account_data,
            'user_type': user_type,
            'allegro_data':allegro_data
            
        }
        return render(request, 'orders/details_orders.html',context)
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
