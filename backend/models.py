from peewee import *
import os

db = PostgresqlDatabase(user=os.environ.get('POSTGRES_USER'), database=os.environ.get('POSTGRES_NAME'), host="db", password=os.environ.get("POSTGRES_PASSWORD"), port="5432")

class Block(Model):
    height = IntegerField(null=True)
    proposer = CharField(max_length=40, null=True)
    relays = IntegerField(null=True)
    txs = IntegerField(null=True)
    timestamp = DateTimeField()

    class Meta:
        database=db
        db_table = 'block'

class Pulse(Model):
    relays = BigIntegerField(null=True)
    nodes = IntegerField(null=True)
    apps = IntegerField(null=True)
    # id = IntegerField(null=True)

    class Meta:
        database=db
        db_table = 'pulse'


class State(Model):
    height = IntegerField(null=True)

    class Meta:
        database=db
        db_table = 'state'


class Transaction(Model):
    height = IntegerField()
    hash = CharField(max_length=64)
    index = IntegerField()
    result_code = IntegerField()
    signer = CharField(max_length=40)
    recipient = CharField(max_length=40)
    msg_type = CharField(max_length=24)
    fee = BigIntegerField()
    memo = TextField()
    value = BigIntegerField()
    timestamp = DateTimeField()

    class Meta:
        database=db
        db_table = 'transaction'


db.create_tables([Transaction, State,Pulse,Block])

if Pulse.select().count() == 0:
	Pulse.create(height=0, producer=0, relays=0, txs=0)

if State.select().count() == 0:
	State.create(height=1)
