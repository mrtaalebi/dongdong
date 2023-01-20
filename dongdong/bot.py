import enum
from datetime import datetime, timedelta
import pytz
import os

import botogram
import peewee
import sqlite3

import config
from models import db, User, Item, Order, Debt, Payment, SimpleDebt


bot = botogram.create(config.api_key)
db.connect()
db.create_tables([User, Item, Order, Debt, Payment, SimpleDebt])


@bot.prepare_memory
def prepare_memory(shared):
    shared["state"] = {}
    shared["cache"] = {}


@bot.command("start")
def start_command(shared, chat, message, args):
    User.create(user_id=chat.id, name=chat.name, username=chat.username)
    with shared.lock("state"):
        state = shared["state"]
        state[chat.id] = enter_card_number
        shared["state"] = state
    chat.send(config.start_message)


@bot.command("help")
def help_command(shared, chat, message, args):
    chat.send(config.help_message)


@bot.command("menu")
def menu_command(shared, chat, message, args):
    menu = botogram.Buttons()
    for i, item in enumerate(Item.select()):
        menu[int(i / 2)].callback(item.name, 'order', str(item.id))
    chat.send(config.menu_message, attach=menu)


@bot.callback("order")
def order_callback(shared, query, data, chat, message):
    with shared.lock("cache"):
        cache = shared["cache"]
        cache[chat.id] = data
        shared["cache"] = cache
    item = Item.get(id=int(data))
    menu = botogram.Buttons()
    menu[0].callback(config.order_is_correct_message, 'order_is_correct', str(item.id))
    menu[0].callback(config.order_is_incorrect_message, 'order_is_incorrect', str(item.id))
    chat.send(config.order_message.format(item.name), attach=menu)


@bot.callback("order_is_correct")
def order_is_correct_callback(shared, query, data, chat, message):
    with shared.lock("cache"):
        cache = shared["cache"]
        cache.pop(chat.id)
        shared["cache"] = cache
    item = Item.get(id=int(data))
    user = User.get(user_id=chat.id)
    Order.create(user=user, item=item)
    chat.send(config.order_confirmed_message)


@bot.callback("order_is_incorrect")
def order_is_incorrect_callback(shared, query, data, chat, message):
    with shared.lock("cache"):
        cache = shared["cache"]
        cache.pop(chat.id)
        shared["cache"] = cache
    chat.send(config.order_canceled_message)


@bot.command("orders")
def orders(shared, chat, message, args):
    message = []
    menu = botogram.Buttons()
    user = User.get(user_id=chat.id)
    start = config.time_now()
    if start.hour < 3:
        start -= timedelta(days=1)
    start = datetime.combine(start.date(), start.min.time()) + timedelta(hours=3)
    end = start + timedelta(days=1)
    for i, order in enumerate(Order.select().where(
        Order.user == user and Order.ordered_at > start and Order.ordered_at < end)
        ):
        message.append(f'{i} - {order.item.name} - {order.ordered_at.time()}')
        menu[int(i / 3)].callback(config.order_remove_message.format(i), 'remove_order', str(order.id))
    chat.send('\n'.join(message), attach=menu)


@bot.callback("remove_order")
def remove_order_callback(shared, query, data, chat, message):
    Order.delete().where(id=int(data))
    chat.send(config.order_remove_confirmation)


@bot.command("pay")
def pay(shared, chat, message, args):
    start = config.time_now()
    if start.hour < 3:
        start -= timedelta(days=1)
    start = datetime.combine(start.date(), start.min.time()) + timedelta(hours=3)
    end = start + timedelta(days=1)
    creditor = User.get(user_id=chat.id)
    payment = Payment(creditor=creditor)
    debts, total = [], 0
    for order in Order.select().where(Order.ordered_at > start and Order.ordered_at < end and Order.debt is None):
        debts.append({'debitor': order.user, 'order': order, 'payment': payment})
        total += order.item.price
    Debt.insert_many(debts).execute()
    chat.send(config.pay_message.format(total))


@bot.command("settle")
def settle(shared, chat, message, args):
    """
    uses min flow algorithm to minimize number of payments made
    """
    debts = {user_1: {user_2: 0 for user_2 in User.select()} for user_1 in User.select()}
    for debt in Debt.select().where(Debt.payment != None):
        debts[debt.debitor][debt.payment.creditor] += debt.order.item.price
    amount = {user: 0 for user in User.select()}
    for p in amount:
        for i in amount:
            amount[p] += debts[i][p] - debts[p][i]

    simple_debts = []
    while True:
        sorted_keys = sorted(amount, key=lambda i: amount[i])
        try:
            max_credit, max_debit = sorted_keys[-1], sorted_keys[0]
        except Exception as e:
            break
        if amount[max_credit] == 0 and amount[max_debit] == 0:
            break
        deliver = min(-1 * amount[max_debit], amount[max_credit])
        amount[max_credit] -= deliver
        amount[max_debit] += deliver
        simple_debts.append({'debitor': max_debit, 'creditor': max_credit, 'amount': deliver})
    with db.atomic():
        SimpleDebt.delete()
    SimpleDebt.insert_many(simple_debts).execute()

    user = User.get(user_id=chat.id)
    menu = botogram.Buttons()
    for i, sd in enumerate(SimpleDebt.select().where(SimpleDebt.debitor == user)):
        menu[i].callback(f'{sd.creditor.name}', 'deliver', str(sd.id))
    message = config.settle_message + '\n'.join([f'{sd.debitor.name} pays {sd.creditor.name}, {sd.amount}' for sd in SimpleDebt.select()])
    chat.send(message, attach=menu)


@bot.callback("deliver")
def deliver_callback(shared, query, data, chat, message):
    simple_debt = SimpleDebt.get(id=int(data))
    creditor = User.get(user_id == simple_debt.creditor.user_id)
    if creditor.card_number:
        chat.send(creditor.card_number)
    simple_debt.delete()
    chat.send(f'{creditor.name} \n {simple_debt.amount}')


@bot.command("put_item")
def item_command(shared, chat, message, args):
    with shared.lock("state"):
        state = shared["state"]
        state[chat.id] = enter_item_name
        shared["state"] = state
    chat.send(config.enter_item_name_message)


@bot.command("delete_item")
def delete_item_command(shared, chat, message, args):
    message = []
    menu = botogram.Buttons()
    for i, item in enumerate(Item.select()):
        message.append(f'{i} - {item.name} - {item.price}')
        menu[int(i % 3)].callback(delete_item_message.format(i), 'delete_item_callback', str(item.id))
    chat.send('\n'.join(message), attach=menu)
    

@bot.callback("delete_item_callback")
def delete_item_callback(shared, query, data, chat, message):
    Item.delete(id=int(data))
    chat.send(config.delete_item_confirm_message)


@bot.message_matches(r".*")
def input_matcher(shared, chat, message):
    if chat.id in shared["state"]:
        return shared["state"][chat.id](shared, chat, message)
    else:
        return message_not_matched(chat, message)


def enter_item_name(shared, chat, message):
    with shared.lock("cache"):
        cache = shared["cache"]
        cache[chat.id] = message.text
        shared["cache"] = cache
    with shared.lock("state"):
        state = shared["state"]
        state[chat.id] = enter_item_price
        shared["state"] = state
    chat.send(config.enter_item_price_message)


def enter_item_price(shared, chat, message):
    name = shared["cache"][chat.id]
    with shared.lock("state"):
        state = shared["state"]
        shared["state"].pop(chat.id)
        shared["state"] = state
    try:
        Item.create(name=name, price=float(message.text))
        chat.send(config.item_created_message)
    except peewee.IntegrityError as e:
        Item.select().where(name=name).update(price=float(message.text))
        chat.send(item_updated_message)


def enter_card_number(shared, chat, message):
    with shared.lock("state"):
        state = shared["state"]
        shared["state"].pop(chat.id)
        shared["state"] = state
    user = User.get(user_id=chat.id)
    user.card_number = message.text
    user.save()
    chat.send(config.welcome_message)


def message_not_matched(chat, message):
    chat.send(config.message_not_matched_message)
