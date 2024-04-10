from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.contrib.auth.hashers import make_password

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Adres e-mail musi być podany')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_worker(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('user_type', 'employee')  # Domyślny typ użytkownika dla pracownika

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

    def get_owners(self):
        return self.get_queryset().filter(user_type='owner')

    def get_employees(self):
        return self.get_queryset().filter(user_type='employee')
    

class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=50, null=True)
    NIP = models.CharField(max_length=20, null=True)
    company_name = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    name_contact = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=50, null=True)
    postcode = models.CharField(max_length=6, null=True)
    user_type = models.CharField(max_length=10, default='owner')
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='account_set')  # Dodaj related_name
    user_permissions = models.ManyToManyField(Permission, related_name='account_set')  # Dodaj related_name

    #Worker
    name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    owner_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class Actions(models.Model):
    action_taken = models.CharField(max_length=100)
    action_time = models.DateTimeField(auto_now_add=True)
    action_result = models.CharField(max_length=100)
    # workers_worker_id = models.ForeignKey(Worker, on_delete=models.CASCADE)
    
class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    category = models.CharField(max_length=100)
    graphic_url = models.CharField(max_length=1000)
    accounts_account_id = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Statues(models.Model):
    description_status = models.CharField(max_length=100)
    def __str__(self):
        return self.description_status

class Documents(models.Model):
    date_of_sale = models.DateTimeField(auto_now_add=True)
    document_number = models.CharField(max_length=50)
    document_type = models.CharField(max_length=50)

    def __str__(self):
        return self.document_number

class Orders(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    amount_products = models.IntegerField()
    status = models.ForeignKey(Statues, on_delete=models.CASCADE, related_name='orders_by_status')
    summary_price = models.DecimalField(max_digits=10, decimal_places=2)
    documents_document_id = models.ForeignKey(Documents, on_delete=models.CASCADE)
    statues_status_id = models.ForeignKey(Statues, on_delete=models.CASCADE, related_name='orders_by_statues')
    
    def __str__(self):
        return str(self.documents_document_id)

class Status_history(models.Model):
    date_of_change = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(Statues, on_delete=models.CASCADE)
    who_changed = models.ForeignKey(Account, on_delete=models.CASCADE)

class Product_has_orders(models.Model):
    products_product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    orders_order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)

class Custumers_addresses(models.Model):
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

class Customers(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

class Customers_has_customers_addresses(models.Model):
    customers_customer_id = models.ForeignKey(Customers, on_delete=models.CASCADE)
    customers_addresses_address_id = models.ForeignKey(Custumers_addresses, on_delete=models.CASCADE)

class Contacts(models.Model):
    report_title = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    report_description = models.TextField(max_length=300)
    attachment = models.CharField(max_length=255)
    accounts_account_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    customers_customer_id = models.ForeignKey(Customers, on_delete=models.CASCADE)

class integrations(models.Model):
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=255)
    accounts_account_id = models.ForeignKey(Account, on_delete=models.CASCADE)
