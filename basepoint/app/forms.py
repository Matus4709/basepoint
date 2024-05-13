from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account
from django.forms import ModelForm
from .models import Products

class UserRegisterForm(UserCreationForm):
    pass
    email = forms.EmailField()

    class Meta:
        model = Account 
        fields = ['email', 'password1', 'password2', 'NIP','country','company_name','phone_number','name_contact','postcode','city','address']

    def __init__(self, *args, **kwargs): #Dodanie klass do inputów
        super().__init__(*args, **kwargs)
        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    
# from django import forms
# from .models import Worker

# class WorkerForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput())

#     class Meta:
#         model = Worker
#         fields = ['email', 'password', 'name', 'last_name']



class ProductsForm(ModelForm):
    class Meta:
        model = Products
        fields = ['name','description','price','quantity','graphic', 'category'] # 'id', 'accounts_account_id'
        
# class UpdateForm(ModelForm):
#     class Meta:
#         model = Products
#         fields = ['graphic']