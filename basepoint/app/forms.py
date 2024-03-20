from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Account 
        fields = ['email', 'password1', 'password2', 'NIP','country','company_name','phone_number','name_contact','surname_contact']

    def __init__(self, *args, **kwargs): #Dodanie klass do inputów
        super().__init__(*args, **kwargs)
        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    
