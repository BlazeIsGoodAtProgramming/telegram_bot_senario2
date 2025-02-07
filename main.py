import telebot
from datetime import datetime
import time
from pymongo import MongoClient
import matplotlib.pyplot as plt

Api_token = "7946742728:AAFfBNzT5vesJiH1mMYMbbJQ3KN5m45uDts"
bot = telebot.TeleBot(Api_token)

client = MongoClient('mongodb://localhost:27017')
db = client['bot']
collection = db['cal']

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id , 'use inline buttons')



@bot.message_handler(commands=['new_user'])
def new_user(message):
    user = collection.find_one({'id' : str(message.chat.id)})
    if user is None :
        bot.send_message(message.chat.id , 'insert your info like this:\nsiavash*0521234567*09181234567')
        bot.register_next_step_handler(message , set_user)     
    else:
         bot.send_message(message.chat.id , 'you have been registerd before \n use /get_chart and /get_new_data')   
    

def set_user(message):
    if '*' in message.text:
        text = message.text.split('*')
        collection.insert_one({
            'id' : str(message.chat.id),
            'name' : text[0],
            'national_code' : int(text[1]),
            'phone' : int(text[2]),
            'income' : [],
            'cost' : [],
            'time' : []
            }
        )
        bot.send_message(message.chat.id , 'you have been registerd \n use /get_chart and /get_new_data')  
    else:
         bot.send_message(message.chat.id , 'message format is incorrect use /new_user again')     


@bot.message_handler(commands=['get_new_data'])
def get_new_data(message):
    user = collection.find_one({'id' : str(message.chat.id)})
    if user is not None :
        bot.send_message(message.chat.id , 'enter your income and cost like this:\n+30000\n-200\nif you dont have any income or cost use /get_chart') 
        bot.register_next_step_handler(message , set_data)  
    else:
        bot.send_message(message.chat.id , 'you are not registerd\nuse /new_user to register') 
       

def set_data(message):
    if '\n' in message.text:
        user = collection.find_one({'id' : str(message.chat.id)})
        text_data = message.text.split('\n')
        income = int(text_data[0])  
        cost = int(text_data[1])
        time = datetime.now()
        collection.update_one(user,
            {"$push" : {"income" : income , "cost" : cost , "time" : time}}
        )
        bot.send_message(message.chat.id , 'your data has been inserted use /get_new_data to insert more data or use /get_chart to get a chart based on the data')

    else:
        bot.send_message(message.chat.id , 'message format is incorrect use /get_new_data again')         


@bot.message_handler(commands=['get_chart']) 
def get_chart(message):
    user = collection.find_one({'id' : str(message.chat.id)})
    if user is not None:
        income = user['income']           
        cost = user['cost']
        print(cost)           
        print(income)           
        time = user['time']
        bot.send_message(message.chat.id , f'your income is : {sum(income)}\nyour cost is : {sum(cost)}\nfinally your balance is : {sum(income)+sum(cost)}')
        
        plt.figure()
        plt.plot(time, income, marker='o', linestyle='-', color='b', label='income_chart')

        plt.xlabel('time')
        plt.ylabel('income')
        plt.title('income_chart')

        """
        plt.legend()
        plt.show() 
        """
        plt.savefig('.\chart_photos\income_chart.png')
        with open('.\chart_photos\income_chart.png', 'rb') as photo1:
            bot.send_photo(message.chat.id , photo1)

        '----------------------------------------------------------------------------'   

        plt.figure()
        plt.plot(time, cost, marker='o', linestyle='-', color='b', label='cost_chart')

        plt.xlabel('time')
        plt.ylabel('cost')
        plt.title('cost_chart')

        """
        plt.legend()
        plt.show() 
        """
        plt.savefig('.\chart_photos\cost_chart.png')
        with open('.\chart_photos\cost_chart.png', 'rb') as photo2:
            bot.send_photo(message.chat.id , photo2)

    else:
        bot.send_message(message.chat.id , 'you are not registerd\nuse /new_user to register')                  



















bot.infinity_polling()