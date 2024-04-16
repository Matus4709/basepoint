from django.db import models

# Create your models here.

class Kategories(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.PositiveIntegerField()
    kategory = models.ForeignKey(Kategories, null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
