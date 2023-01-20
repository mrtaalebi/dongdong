import enum
from datetime import datetime, timedelta
import pytz
import os

import botogram
import sqlite3

import config
from dongdong.models import db, User, Item, Order, Debt, Payment


bot = botogram.create(config.api_key)
db.connect()
db.create_tables([User, Item, Order, Debt, Payment])

state = {}
cache = {}


@bot.command("start")
def start_command(chat, message, args):
    User.create(user_id=chat.id, name=chat.name, username=chat.username)
    chat.send(config.start_message)


@bot.command("help")
def help_command(chat, message, args):
    chat.send(config.help_message)


@bot.command("menu")
def menu_command(chat, message, args):
    menu = botogram.Buttons()
    for i, item in enumerate(Item.select()):
        menu[int(i / 2)].callback(item.name, 'order', item.name)
    chat.send(config.menu_message, attach=menu())


@bot.callback("order")
def order_callback(query, data, chat, message):
    cache[chat.id] = data
    menu = botogram.Buttons()
    menu[0].callback(order_is_correct, 'order_is_correct', item.name)
    menu[0].callback(order_is_incorrect, 'order_is_incorrect', item.name)
    chat.send(config.order_message, attach=menu())


@bot.callback("order_is_correct")
def order_is_correct_callback(query, data, chat, message):
    item = Item.get(name=cache(chat.id))
    user = User.get(user_id=chat.id)
    Order.create(user=user, item=item)
    chat.send(config.order_confirmed_message)


@bot.callback("order_is_incorrect")
def order_is_incorrect_callback(query, data, chat, message):
    cache.drop(chat.id)
    chat.send(config.order_canceled_message)



@bot.command("settle")
def settle(chat, message, args):
    """
    uses min flow algorithm to minimize number of payments made
    """
    debts = [
        [
            sum([
                debt.order.item.price for debt in
                Debt.where(debitor == user and payment.creditor == creditor)])
                for creditor in User.select()
        ]
        for debitor in User.select()
    ]
    amount = {user: 0 for user in User.select()}
    for p, _ in amount:
        for i, __ in amount:
            amount[p][0] += debts[i][p] - debts[p][i]

    simple_debts = {}
    while True:
        sorted_keys = sorted(amount, key=lambda i: amount[i])
        max_credit, max_debit = amount[sorted_amount[-1]], amount[sorted_amount[0]]
        if amount[max_credit] == 0 and amount[max_debit] == 0:
            break
        deliver = min(-1 * amount[max_debit], amount[max_credit])
        amount[max_credit] -= deliver
        amount[max_debit] += deliver
        simple_debts.append({'debitor': max_debit, 'creditor': max_credit, 'amount': deliver})
    SimpleDebt.insert_many(**simple_debts).execute()

    user = User.get(user_id=chat.id)
    menu = botogram.Buttons()
    for i, sd in enumerate(SimpleDebt.where(debitor == user)):
        menu[i].callback(f'{sd.creditor.name}', 'deliver', sd.id)
    message = '\n'.join([f'{sd.debitor.name} pays {sd.creditor.name}, {sd.amount}' for sd in SimpleDebt.select()])
    chat.send(message, attach=menu())


@bot.callback("deliver")
def deliver_callback(query, data, chat, message):
    simple_debt = SimpleDebt.get(id=data)
    creditor = User.get(user_id == simple_debt.creditor.user_id)
    chat.send(f'{creditor.name} \n {simple_debt.amount}')
    if creditor.card_number:
        chat.send(creditor.card_number)
    simple_debt.delete()


@bot.command("item")
def item_command(chat, message, args):
    chat.send(config.enter_item_name_message)
    state[chat.id] = enter_item_name


@bot.message_matches(".*")
def input_matcher(chat, message, args):
    if chat.id in state:
        return state[chat.id](chat, message, args)
    else:
        return message_not_matched(chat, message, args)


def enter_item_name(chat, message, args):
    cache[chat.id] = message
    chat.send(config.enter_item_price_message)
    state[chat.id] = enter_item_price


def enter_item_price(chat, message, args):
    name = cache[chat.id]
    try:
        Item.create(name=name, price=float(message))
        chat.send(item_created_message)
    except peewee.IntegrityError as e:
        Item.where(name=name).update(price=float(message))
        chat.send(item_updated_message)
    state.pop(chat.id)


def message_not_matched(chat, message, args):
    chat.send(config.message_not_matched_message)

