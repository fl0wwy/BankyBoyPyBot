import account_generator
import datetime
import os
import telebot
from telebot import types

API = os.environ['API']
bot = telebot.TeleBot(API)

accounts = []
markup = types.ForceReply(selective=False)

@bot.message_handler(commands=['start'])
def start(message):
    for i in accounts:
        if i.id == message.chat.id:
            bot.send_message(message.chat.id,'You already have an account in this bot!')
            return ''
    bot.send_message(message.chat.id,'Hello, This is the banking bot service. please start by entering your current balance:',reply_markup=markup)
    account = account_generator.Account(id=message.chat.id,balance=0,salary=0)
    account.date = datetime.date.today().strftime('%d/%m/%Y')
    accounts.append(account)

def check(users,m):
    for i in users:
        if i.id == m.chat.id:
            return i 

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message,'The following commands are available for this bot:\n/start - resets the bot completely in the case it was already initiated.\n/help - Commands guide\n/salary - Changes your monthly salary\n/deposit - Enters a new deposit with the parameters "price,sender,reason(optional)" in this order seperated by commas.\n/expense - Enters a new expense with the parameters "price,location,products(optional)" in this order seperated by commas.\n/balance - Shows current account balance\n/summary - Shows a dictionary of all recent deposits and expenses /month - adds your monthly income to your balance and activates the summary command. deletes all history of transactions. (USE ONLY WHEN YOUR MONTHLY INCOME ARRIVES)')    

@bot.message_handler(func=lambda m: m.reply_to_message != None)
def reply_checker(message):
    if message.reply_to_message.text == 'Hello, This is the banking bot service. please start by entering your current balance:':
        balance_change(message)
        
    elif message.reply_to_message.text == 'Please state a deposit amount and a sender and optionally a reason seperated by a comma.':
        deposit(message)
        
    elif message.reply_to_message.text ==  'Please state an expense amount and where it was spent and optionally the products seperated by a comma.':
        expense(message)
        
    elif message.reply_to_message.text == 'Please enter your salary!':
        salary_change(message)      
                                    

@bot.message_handler(commands=['balance'])
def balance(message):
    bot.reply_to(message,f'Your balance is {check(accounts,message).balance}')

@bot.message_handler(commands=['deposit'])
def deposit_prompt(message):
    bot.send_message(message.chat.id,'Please state a deposit amount and a sender and optionally a reason seperated by a comma.',reply_markup=markup)

def balance_change(message):
    if message.text.isdecimal():
        check(accounts,message).balance = float(message.text)
        bot.reply_to(message,f'Got it! your balance is now set to {check(accounts,message).balance}.\nTo input your salary for your monthly documentation use the /salary command. or refer to the /help command for further information.')
    else:
        bot.reply_to(message,'Please make sure the input is a decimal value! reply to the prompt to try again.')    

def deposit(message):
    split = message.text.split(',')
    if len(split) == 1:
        bot.reply_to(message,'Please make sure you seperate the information using a comma.')
    else:
        try:
            if len(split) == 3:
                check(accounts,message).deposition(amount=split[0],sender=split[1],reason=split[2])
            else:
                check(accounts,message).deposition(amount=split[0],sender=split[1])     
        except TypeError:
            bot.reply_to(message,'Please make sure you have the right specifications!')
        else:
            bot.reply_to(message,f'Deposit successful! {check(accounts,message).deposits[split[1]]}\nBalance: {check(accounts,message).balance}')        

@bot.message_handler(commands=['expense'])
def expense_promot(message):
    bot.send_message(message.chat.id,'Please state an expense amount and where it was spent and optionally the products seperated by a comma.',reply_markup=markup)

def expense(message):
    split = message.text.split(',')
    if len(split) == 1:
        bot.reply_to(message,'Please make sure you seperate the information using a comma.')
    else:
        try:
            check(accounts,message).expense(amount=split[0],place=split[1],products=[split[2::]])
        except TypeError:
            bot.reply_to(message,'Please make sure the amount is specified first!')
        else:
            bot.reply_to(message,f'Expense documented. {check(accounts,message).expenses[split[1]]}\nBalance: {check(accounts,message).balance}')

@bot.message_handler(commands=['salary'])
def salary_prompt(message):
    bot.send_message(message.chat.id,'Please enter your salary!',reply_markup=markup)

def salary_change(message):
    if message.text.isdecimal():
        check(accounts,message).salary = float(message.text)
        bot.reply_to(message,f'Got it! Your monthly salary is now set to {check(accounts,message).salary}')
    else:
        bot.reply_to(message,'Please make sure your salary input consists of only decimal values!')

def briefing(message,acc):
    bot.send_message(message.chat.id,f'EXPENSES: {acc.expenses}')
    bot.send_message(message.chat.id,f'DEPOSITS: {acc.deposits}')

@bot.message_handler(commands=['summary'])
def summary(message):
    last_date = check(accounts,message).date
    bot.send_message(message.chat.id,f'Your recent expenses and deposits from -{last_date}- to -{datetime.date.today().strftime("%d/%m/%Y")}-:')
    briefing(message,check(accounts,message))
    check(accounts,message).date = datetime.date.today().strftime("%d/%m/%Y")

@bot.message_handler(commands=['month'])
def income(message):
    bot.reply_to(message,f'This is your monthly summary of -{datetime.date.today().strftime("%B")}-')
    check(accounts,message).deposition(check(accounts,message).salary,'MONTHLY INCOME')
    bot.send_message(message.chat.id,f'YOUR BALANCE AFTER MONTHLY INCOME OF {check(accounts,message).salary}: {check(accounts,message).balance}')
    briefing(message,check(accounts,message))
    check(accounts,message).deposits = {}
    check(accounts,message).expenses = {}


bot.polling()              










                        
            

