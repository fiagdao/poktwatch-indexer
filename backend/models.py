from peewee import *
import os
#db = PostgresqlDatabase(user="ufo4f7au3ibjir",host="ec2-35-174-58-77.compute-1.amazonaws.com",database="dfj22uqqfkqbam",password="pb77af04be9db1ee75fca22da05007c7b4ce35d282059837afd8735c49b0a42c3",port="5432")
# db = PostgresqlDatabase(user="u8ubp48c0q5bhm", database="dfj22uqqfkqbam", host="ec2-35-170-124-67.compute-1.amazonaws.com", password="pdfa73ca4ff5e08f37c37d656332e303aa4e5f150734fb8b2c0b3fa344590f4e8", port="5432")
db = PostgresqlDatabase(user=os.environ.get('POSTGRES_USER'), database=os.environ.get('POSTGRES_NAME'), host="db", password=os.environ.get("POSTGRES_PASSWORD"), port="5432")
class Account(Model):
    address = CharField(max_length=40, null=True)
    public_key = CharField(max_length=64, null=True)
    balance = FloatField(null=True)
    staked_balance = IntegerField(null=True)
    txs = TextField(null=True)

    class Meta:
        database=db
        db_table = 'accounts'


class Blocks(Model):
    height = IntegerField(null=True)
    producer = CharField(max_length=40, null=True)
    relays = IntegerField(null=True)
    txs = IntegerField(null=True)

    class Meta:
        database=db
        db_table = 'blocks'

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
    hash = CharField(max_length=64, null=True)
    receiver = CharField(max_length=40, null=True)
    sender = CharField(max_length=40, null=True)
    value = BigIntegerField(null=True)
    type = CharField(max_length=24, null=True)
    fee = BigIntegerField(null=True)
    height = IntegerField(null=True)
    index = IntegerField(null=True)
    code = IntegerField(null=True)
    memo = TextField(null=True)
    chain = CharField(max_length=4, null=True)
    timestamp = DateTimeField()

    class Meta:
        database=db
        db_table = 'transactions'


db.create_tables([Transaction, State,Pulse,Blocks, Account])

if Pulse.select().count() == 0:
	Pulse.create(height=0, producer=0, relays=0, txs=0)

if State.select().count() == 0:
	State.create(height=0)
