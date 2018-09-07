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
pass_dict = dict()


class UserCredentials:
    def __init__(self, email):
        self.email = email
        self.password = None


class PasswordCredentials:
    def __init__(self, n_url):
        self.url = n_url
        self.title = None
        self.login = None
        self.password = None
        self.comment = None


def log(message, answer):
    from datetime import datetime
    print(datetime.now())
    print(f'Message from {message.from_user.first_name} {message.from_user.last_name}. \ '
          f'id={str(message.from_user.id)}, message: {message.text}')


@bot.message_handler(commands=['help'])
def handle_help_command(message):
    if not cookies:
        user_markup = telebot.types.ReplyKeyboardMarkup()
        user_markup.row('/login', '/help')
        bot.send_message(message.from_user.id, 'Please, choose what you\'d like to do', reply_markup=user_markup)
    if cookies:
        user_markup = telebot.types.ReplyKeyboardMarkup()
        user_markup.row('/get_me', '/get_my_pass')
        user_markup.row('/search', '/logout')
        user_markup.row('/add_pass', '/change_pass_info')
        bot.send_message(message.from_user.id, 'Please, choose what you\'d like to do', reply_markup=user_markup)


@bot.message_handler(commands=['login'])
def handle_login_command(message):
    try:
        msg = bot.reply_to(message, """\
        Hi there, I am SSkey bot.
        Please, enter your email in order to login
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
        msg = bot.reply_to(message, 'Almost there. Please, enter your password')
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


@bot.message_handler(commands=['search'])
def handle_get_command(message):
    try:
        msg = bot.reply_to(message, """\
                Please, enter a description of your passport in order to find the password
                """)
        bot.register_next_step_handler(msg, search_pass)
    except Exception as err:
        bot.reply_to(message, err)


def search_pass(message):
    try:
        condition = message.text
        rv = requests.post(url + 'user/passwords/search', json=dict(condition=condition), cookies=cookies)
        passwords = rv.json()

        for pas in passwords.get("passwords"):
            bot.send_message(message.from_user.id, f'{pas}')
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['add_pass'])
def handle_login_command(message):
    try:
        msg = bot.reply_to(message, """\
        Hi there, I am SSkey bot.
        Please, enter an url of new password
        """)
        bot.register_next_step_handler(msg, get_url)
    except Exception as err:
        bot.reply_to(message, err)


def get_url(message):
    try:
        chat_id = message.chat.id
        n_url = message.text
        user_pass = PasswordCredentials(n_url)
        pass_dict[chat_id] = user_pass
        msg = bot.reply_to(message, 'Almost there. Please, enter a title of the service')
        bot.register_next_step_handler(msg, get_title)
    except Exception as err:
        bot.reply_to(message, err)


def get_title(message):
    try:
        chat_id = message.chat.id
        title = message.text
        if not title:
            msg = bot.reply_to(message, 'Cannot be empty.')
            bot.register_next_step_handler(msg, get_title)
            return
        user_pass = pass_dict[chat_id]
        user_pass.title = title
        msg = bot.reply_to(message, 'A few more steps. Please, enter your login of the service')
        bot.register_next_step_handler(msg, get_login)
    except Exception as e:
        bot.reply_to(message, e)


def get_login(message):
    try:
        chat_id = message.chat.id
        login = message.text
        user_pass = pass_dict[chat_id]
        user_pass.login = login
        msg = bot.reply_to(message, 'Almost there. Please, enter your password')
        bot.register_next_step_handler(msg, get_my_pass)
    except Exception as err:
        bot.reply_to(message, err)


def get_my_pass(message):
    try:
        chat_id = message.chat.id
        password = message.text
        if not password:
            msg = bot.reply_to(message, 'Cannot be empty. Please, enter your password')
            bot.register_next_step_handler(msg, get_pass)
            return
        user_pass = pass_dict[chat_id]
        user_pass.password = password
        msg = bot.reply_to(message, 'Last, but not least. Please, enter your description for your service')
        bot.register_next_step_handler(msg, get_description)
    except Exception as e:
        bot.reply_to(message, e)


def get_description(message):
    try:
        chat_id = message.chat.id
        comment = message.text
        if not comment:
            msg = bot.reply_to(message, 'Cannot be empty.')
            bot.register_next_step_handler(msg, get_description)
            return
        user_pass = pass_dict[chat_id]
        user_pass.comment = comment

        rv = requests.post(url + 'user/passwords', json=dict(
            url=user_pass.url,
            title=user_pass.title,
            login=user_pass.login,
            password=user_pass.password,
            comment=user_pass.comment
        ), cookies=cookies)
        bot.send_message(message.from_user.id, rv)
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    answer = 'Some answer'
    log(message, answer)


bot.polling(none_stop=True, interval=0)
