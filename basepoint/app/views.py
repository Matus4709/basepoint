from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
import secrets
import smtplib, ssl
import os
from dotenv import load_dotenv


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
            import os
            from dotenv import load_dotenv
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            load_dotenv(os.path.join(BASE_DIR, '.env'))
            port = os.getenv('PORT')
            smtp_server = os.getenv('SMTP_SERVER')
            sender_email = os.getenv('EMAIL_HOST_USER')
            smtp_password = os.getenv('EMAIL_HOST_PASSWORD')

            message = """Subject: Potwierdzenie rejestracji - BASEPOINT

            Witaj {email}, kliknij w ponizszy link, aby aktywowac konto:\n\n http://127.0.0.1:8000/activate/{token}/
            """.format(email=email, token=token)

            ssl_con = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=ssl_con) as server:
                server.login(sender_email, smtp_password)
                server.sendmail(sender_email, email, message)
            
            return HttpResponse("Sprawdź swój e-mail, aby aktywować konto.")
    else:
        return redirect('dashboard')

    return render(request, 'create_worker.html')

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
        port = os.getenv('PORT')
        smtp_server = os.getenv('SMTP_SERVER')
        sender_email = os.getenv('EMAIL_HOST_USER')
        smtp_password = os.getenv('EMAIL_HOST_PASSWORD')

        message = """Subject: Potwierdzenie rejestracji - BASEPOINT

        Witaj {email}, kliknij w ponizszy link, aby aktywowac konto:\n\n http://127.0.0.1:8000/activate/{token}/
        """.format(email=email, token=token)

        ssl_con = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=ssl_con) as server:
            server.login(sender_email, smtp_password)
            server.sendmail(sender_email, email, message)
        
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
    return redirect('login')  # Przykładowa nazwa strony logowania

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
            with connection.cursor() as cursor:
                
                cursor.execute("SELECT country, NIP, company_name, phone_number, name_contact, city, address, postcode FROM app_account WHERE %s = id;", [owner_id])
                rows = cursor.fetchall()
                # Konwersja wyników z krotki na listę słowników
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in rows]
            

            return render(request, 'dashboard.html', {'user_type': user_type,'data':data})
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
        #Wysyłanie maila
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(BASE_DIR, '.env'))
        port = os.getenv('PORT')
        smtp_server = os.getenv('SMTP_SERVER')
        # sender_email = os.getenv('EMAIL_HOST_USER')
        sender_email = 'pichniarczykmarek@gmail.com'
        smtp_password = os.getenv('EMAIL_HOST_PASSWORD')

        message = """Subject: Resetowanie hasla - BASEPOINT

            Witaj {email}, kliknij w ponizszy link, aby zresetowac swoje haslo:\n\n http://127.0.0.1:8000/reset-password-confirm/{token}/
            """.format(email=email, token=token)
        print (sender_email)


        ssl_con = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=ssl_con) as server:
                server.login(sender_email, smtp_password)
                server.sendmail(sender_email, email, message)
    
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
  