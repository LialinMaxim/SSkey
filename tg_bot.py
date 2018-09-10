import os
import telebot
import re
import requests

from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, 'src/app/.env'))

token = os.environ.get('TOKEN')
bot = telebot.TeleBot(token)
url = 'http://127.0.0.1:5000/'
# url = 'http://sskey.herokuapp.com/'

print(bot.get_me())
cookies = dict()
user_dict = dict()
pass_dict = dict()


class UserCredentials:
    def __init__(self, email):
        self.email = email
        self.password = None


class PasswordCredentials:
    def __init__(self, id):
        self.id = id
        self.url = None
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
        user_markup.row('/profile', '/search')
        user_markup.row('/get_passwords', '/logout')
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
        # cookies.append(rv.cookies)
        cookies['cookie'] = rv.cookies
        rv = rv.json()
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['profile'])
def handle_profile_command(message):
    if cookies:
        try:
            rv = requests.get(url + 'user/', cookies=cookies.get('cookie'))
            bot.send_message(message.from_user.id, rv)
            user_markup = telebot.types.ReplyKeyboardMarkup()
            user_markup.row('/logout', '/edit_profile')
            user_markup.row('/delete_profile', '/help')
            bot.send_message(message.from_user.id, 'You\'re available to', reply_markup=user_markup)
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


def gen_edit_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton('First Name', callback_data=f'change_f_name'),
               InlineKeyboardButton('Last Name', callback_data=f'change_l_name'),
               InlineKeyboardButton('Email', callback_data=f'change_email'),
               InlineKeyboardButton('Phone', callback_data=f'change_phone'))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'change_f_name':
        bot.answer_callback_query(call.id, "Answer is Yes")
    elif call.data == 'change_l_name':
        bot.answer_callback_query(call.id, "Answer is No")
    elif call.data == 'change_email':
        pass
    elif call.data == 'change_phone':
        pass


@bot.message_handler(commands=['edit_profile'])
def handle_edit_profile_command(message):
    if cookies:
        try:
            bot.send_message(message.chat.id, 'Choose what you wanna change', reply_markup=gen_edit_markup())
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


@bot.message_handler(commands=['delete_profile'])
def handle_delete_profile_command(message):
    try:
        rv = requests.delete(url + 'user/', cookies=cookies.get('cookie'))
        bot.send_message(message.from_user.id, rv)
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['get_passwords'])
def handle_get_passwords_command(message):
    if cookies:
        try:
            rv = requests.get(url + 'user/passwords', cookies=cookies.get('cookie'))
            passwords = rv.json()
            counter = 0
            results = ''

            for pas in passwords.get('passwords'):
                counter += 1
                results = results + '/' + str(pas.get('pass_id')) + ' - ' + pas.get('title') + ': ' + pas.get(
                    'login') + '\n'
            header = f'Results of {counter} \n'
            results = header + results
            bot.send_message(message.from_user.id, results)
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


@bot.message_handler(commands=['logout'])
def handle_logout_command(message):
    try:
        rv = requests.get(url + 'logout', cookies=cookies.get('cookie'))
        rv = rv.json()
        cookies.clear()
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['search'])
def handle_search_command(message):
    if cookies:
        try:
            msg = bot.reply_to(message, 'Please, enter a description of your passport in order to find the password')
            bot.register_next_step_handler(msg, search_pass)
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


def search_pass(message):
    try:
        condition = message.text
        rv = requests.post(url + 'user/passwords/search', json=dict(condition=condition), cookies=cookies.get('cookie'))
        passwords = rv.json()

        for pas in passwords.get('passwords'):
            bot.send_message(message.from_user.id, f'{pas}')
    except Exception as err:
        bot.reply_to(message, err)


def gen_edit_pass_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 5
    markup.add(InlineKeyboardButton('URL', callback_data=f'change_url'),
               InlineKeyboardButton('Title', callback_data=f'change_title'),
               InlineKeyboardButton('Login', callback_data=f'change_login'),
               InlineKeyboardButton('Password', callback_data=f'change_pass'),
               InlineKeyboardButton('Comment', callback_data=f'change_comment'))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'change_url':
        bot.answer_callback_query(call.id, "Answer is Yes")
    elif call.data == 'change_title':
        bot.answer_callback_query(call.id, "Answer is No")
    elif call.data == 'change_login':
        pass
    elif call.data == 'change_pass':
        pass
    elif call.data == 'change_comment':
        pass


@bot.message_handler(commands=['edit_pass_info'])
def handle_edit_pass_command(message):
    if cookies:
        try:
            user_markup = telebot.types.ReplyKeyboardMarkup()
            user_markup.row('/change_url', '/change_title')
            user_markup.row('/change_login', '/change_pass')
            user_markup.row('/change_comment', '/help')
            bot.send_message(message.from_user.id, 'Choose, what to change', reply_markup=gen_edit_pass_markup())
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


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
    except Exception as err:
        bot.reply_to(message, err)


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
    except Exception as err:
        bot.reply_to(message, err)


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
        ), cookies=cookies.get('cookie'))
        bot.send_message(message.from_user.id, rv)
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(func=lambda message: re.match(r'/\d+', message.text))
def handle_get_particular_pass_command(message):
    if cookies:
        try:
            # removed / after passwords because message.text will be smth like /digit
            rv = requests.get(url + 'user/passwords' + message.text, cookies=cookies.get('cookie'))
            bot.send_message(message.from_user.id, rv)
            chat_id = message.chat.id
            pass_id = message.text
            user_pass = PasswordCredentials(pass_id)
            pass_dict[chat_id] = user_pass
            user_markup = telebot.types.ReplyKeyboardMarkup()
            user_markup.row('/edit_pass_info', '/delete_password')
            user_markup.row('/help')
            bot.send_message(message.from_user.id, 'Also, you are able to', reply_markup=user_markup)
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


@bot.message_handler(commands=['delete_password'])
def handle_delete_password_command(message):
    if cookies:
        try:
            chat_id = message.chat.id
            # removed / after passwords because message.text will be smth like /digit
            rv = requests.delete(url + 'user/passwords' + pass_dict.get(chat_id).id, cookies=cookies.get('cookie'))
            rv = rv.json()
            bot.send_message(message.from_user.id, rv.get('message'))
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    answer = 'Some answer'
    log(message, answer)


bot.polling(none_stop=True, interval=0)
