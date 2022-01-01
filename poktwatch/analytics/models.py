# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Ask(models.Model):
    id = models.AutoField(primary_key=True)
    volume = models.IntegerField(default=0)
    minimumFill = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    seller = models.ForeignKey(User,on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10,choices=(("PENDING", "Pending"), ("OPEN", "Open")), default='OPEN')

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    volume = models.IntegerField(default=0)
    minimumFill = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    buyer = models.ForeignKey(User,on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10,choices=(("PENDING", "Pending"), ("OPEN", "Open"),("SHEET","Sheet"),("N/A","N/A")), default='OPEN')

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateFilled = models.DateTimeField(blank=True,null=True)

    volume = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=3)

    buyer = models.ForeignKey(User,on_delete=models.CASCADE,related_name='buyer')
    seller = models.ForeignKey(User,on_delete=models.CASCADE,related_name='seller')

    origin = models.CharField(max_length=10,choices=(("BID", "Bid"), ("Ask", "Ask")))

    status = models.CharField(max_length=10,choices=(("PENDING", "Pending"), ("COMPLETED", "Completed")), default='OPEN')
