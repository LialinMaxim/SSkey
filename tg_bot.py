import telebot
import requests

token = "561689896:AAFOU46PTW4y-4FPNgbBurYRvEWcDY6ESgc"
bot = telebot.TeleBot(token)
url = 'http://127.0.0.1:5000/'
# url = 'http://sskey.herokuapp.com/'

print(bot.get_me())


def log(message, answer):
    from datetime import datetime
    print(datetime.now())
    print(f'Message from {message.from_user.first_name} {message.from_user.last_name}. \ '
          f'id={str(message.from_user.id)}, message: {message.text}')


@bot.message_handler(commands=['help'])
def handle_help_command(message):
    user_markup = telebot.types.ReplyKeyboardMarkup()
    user_markup.row('/home', '/smoke')
    user_markup.row('/register', '/login')
    user_markup.row('/get_me', '/get_my_pass')
    user_markup.row('/add_my_pass', '/logout')
    bot.send_message(message.from_user.id, 'Please, choose what you\'d like to do', reply_markup=user_markup)


@bot.message_handler(commands=['home'])
def handle_home_command(message):
    rv = requests.get(url + 'home')
    bot.send_message(message.from_user.id, rv)


@bot.message_handler(commands=['smoke'])
def handle_smoke_command(message):
    rv = requests.get(url + 'smoke')
    bot.send_message(message.from_user.id, rv)


@bot.message_handler(commands=['register'])
def handle_register_command(message):
    bot.send_message(message.from_user.id, 'Hello from register')


@bot.message_handler(commands=['login'])
def handle_login_command(message):
    rv = requests.post(url + 'login', json=dict(email='admin@gmail.com', password='admin'))
    bot.send_message(message.from_user.id, rv)


@bot.message_handler(commands=['get_me'])
def handle_get_command(message):
    rv = requests.get(url + 'user/')
    bot.send_message(message.from_user.id, rv)


@bot.message_handler(commands=['get_my_pass'])
def handle_get_command(message):
    rv = requests.get(url + '/user/passwords')
    bot.send_message(message.from_user.id, rv)


@bot.message_handler(commands=['logout'])
def handle_get_command(message):
    rv = requests.get(url + 'logout')
    bot.send_message(message.from_user.id, rv)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    answer = 'Some answer'
    log(message, answer)


bot.polling(none_stop=True, interval=0)
