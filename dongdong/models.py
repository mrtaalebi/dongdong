import os

from peewee import *

import config


if config.conn.startswith("postgres"):
    db = PostgresqlDatabase(config.conn, autorollback=True)
else:
    db = SqliteDatabase(config.conn, autorollback=True)


class User(Model):
    user_id = CharField()
    name = CharField()
    username = CharField(null=True)
    card_number = CharField(null=True)

    class Meta:
        database = db


class Item(Model):
    name = CharField(unique=True)
    price = FloatField()

    class Meta:
        database = db


class Order(Model):
    user = ForeignKeyField(User, backref='orders')
    item = ForeignKeyField(Item)
    ordered_at = DateTimeField(default=config.time_now)

    class Meta:
        database = db


class Payment(Model):
    creditor = ForeignKeyField(User, backref='payments')
    payed_at = DateTimeField(default=config.time_now)

    class Meta:
        database = db


class Debt(Model):
    debitor = ForeignKeyField(User, backref='debts')
    order = ForeignKeyField(Order, backref='debt', unique=True)
    payment = ForeignKeyField(Payment, backref='debt', null=True)
    is_settled = BooleanField(default=False)

    class Meta:
        database = db


class SimpleDebt(Model):
    debitor = ForeignKeyField(User, backref='simple_debts')
    creditor = ForeignKeyField(User, backref='simple_credits')
    amount = FloatField()

    class Meta:
        database = db

