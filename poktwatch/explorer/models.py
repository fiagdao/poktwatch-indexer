from django.db import models


class Accounts(models.Model):
    address = models.CharField(max_length=40, blank=True, null=True)
    public_key = models.CharField(max_length=64, blank=True, null=True)
    balance = models.FloatField(blank=True, null=True)
    staked_balance = models.IntegerField(blank=True, null=True)
    txs = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accounts'


class Blocks(models.Model):
    height = models.IntegerField(blank=True, null=True)
    producer = models.CharField(max_length=40, blank=True, null=True)
    relays = models.IntegerField(blank=True, null=True)
    txs = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blocks'


class Pulse(models.Model):
    relays = models.BigIntegerField(blank=True, null=True)
    nodes = models.IntegerField(blank=True, null=True)
    apps = models.IntegerField(blank=True, null=True)
    # id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pulse'


class State(models.Model):
    height = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'state'


class Transactions(models.Model):
    hash = models.CharField(max_length=64, blank=True, null=True)
    receiver = models.CharField(max_length=40, blank=True, null=True)
    sender = models.CharField(max_length=40, blank=True, null=True)
    value = models.BigIntegerField(blank=True, null=True)
    type = models.CharField(max_length=24, blank=True, null=True)
    fee = models.BigIntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    index = models.IntegerField(blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions'
