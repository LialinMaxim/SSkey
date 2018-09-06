import os
import telebot
import requests

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, 'src/app/.env'))

token = os.environ.get('TOKEN')
bot = telebot.TeleBot(token)
url = 'http://127.0.0.1:5000/'
# url = 'http://sskey.herokuapp.com/'

print(bot.get_me())
cookies = ''
user_dict = dict()


class UserCredentials:
    def __init__(self, email):
        self.email = email
        self.password = None


def log(message, answer):
    from datetime import datetime
    print(datetime.now())
    print(f'Message from {message.from_user.first_name} {message.from_user.last_name}. \ '
          f'id={str(message.from_user.id)}, message: {message.text}')


@bot.message_handler(commands=['help'])
def handle_help_command(message):
    if not cookies:
        user_markup = telebot.types.ReplyKeyboardMarkup()
        user_markup.row('/home', '/smoke')
        user_markup.row('/login', '/help')
        bot.send_message(message.from_user.id, 'Please, choose what you\'d like to do', reply_markup=user_markup)
    if cookies:
        user_markup = telebot.types.ReplyKeyboardMarkup()
        user_markup.row('/get_me', '/get_my_pass')
        user_markup.row('/add_my_pass', '/logout')
        bot.send_message(message.from_user.id, 'Please, choose what you\'d like to do', reply_markup=user_markup)


@bot.message_handler(commands=['home'])
def handle_home_command(message):
    try:
        rv = requests.get(url + 'home')
        bot.send_message(message.from_user.id, rv)
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['smoke'])
def handle_smoke_command(message):
    try:
        rv = requests.get(url + 'smoke', cookies=cookies)
        bot.send_message(message.from_user.id, rv)
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['login'])
def handle_login_command(message):
    try:
        msg = bot.reply_to(message, """\
        Hi there, I am SSkey bot.
        Please, enter your email?
        """)
        bot.register_next_step_handler(msg, get_email)
    except Exception as err:
        bot.reply_to(message, err)


def get_email(message):
    try:
        chat_id = message.chat.id
        email = message.text
        user = UserCredentials(email)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, 'Enter your password?')
        bot.register_next_step_handler(msg, get_pass)
    except Exception as err:
        bot.reply_to(message, err)


def get_pass(message):
    try:
        chat_id = message.chat.id
        password = message.text
        if not password:
            msg = bot.reply_to(message, 'Cannot be empty. Please, enter your password')
            bot.register_next_step_handler(msg, get_pass)
            return
        user = user_dict[chat_id]
        user.password = password
        rv = requests.post(url + 'login', json=dict(email=user.email, password=user.password))
        global cookies
        cookies = rv.cookies
        bot.send_message(message.from_user.id, rv)
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(commands=['get_me'])
def handle_get_command(message):
    try:
        rv = requests.get(url + 'user/', cookies=cookies)
        bot.send_message(message.from_user.id, rv)
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['get_my_pass'])
def handle_get_command(message):
    try:
        rv = requests.get(url + 'user/passwords', cookies=cookies)
        passwords = rv.json()

        for pas in passwords.get("passwords"):
            bot.send_message(message.from_user.id, f'{pas}')
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['logout'])
def handle_get_command(message):
    try:
        rv = requests.get(url + 'logout', cookies=cookies)
        bot.send_message(message.from_user.id, rv)
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    answer = 'Some answer'
    log(message, answer)


bot.polling(none_stop=True, interval=0)
