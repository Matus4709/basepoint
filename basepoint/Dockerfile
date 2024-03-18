# Użyj obrazu bazowego Pythona
FROM python:3.12.1

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj plik requirements.txt i zainstaluj zależności
COPY requirements.txt .
RUN pip install -r requirements.txt

# Skopiuj cały projekt do katalogu /app
COPY . .

# Uruchom serwer Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
