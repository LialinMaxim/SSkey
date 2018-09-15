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
user_dict = dict()
pass_dict = dict()
user_data = dict()


class UserCredentials:
    def __init__(self, email):
        self.email = email
        self.password = None
        self.token = None


class UserProfile:
    def __init__(self):
        self.cur_email = None
        self.username = None
        self.first_name = None
        self.last_name = None
        self.phone = None

    def print_user_profile(self):
        formatted_string = 'Email — ' + self.cur_email + '\n' + \
                           'Username — ' + self.username + '\n' + \
                           'First Name — ' + self.first_name + '\n' + \
                           'Last Name — ' + self.last_name + '\n' + \
                           'Phone — ' + self.phone
        return formatted_string


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
    msg = \
        """
        🔥 Commands
Comfortable and secure way of storing your passwords.
Just remember your main password and SSkey remembers the rest.
/login — Logging in https://sskey.herokuapp.com/
/profile — Get yours data from https://sskey.herokuapp.com/
/get_passwords — Get list of user's passwords
/logout — Logging out from https://sskey.herokuapp.com/
/search — Search for passwords by its description
/edit_pass_info — Update user's password data
/edit_profile — Update user's personal data
/delete_password — Delete specific password
"""
    bot.send_message(message.from_user.id, msg)


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
        user.token = rv.cookies
        rv = rv.json()
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['profile'])
def handle_profile_command(message):
    if user_dict.get(message.chat.id):
        try:
            rv = requests.get(url + 'user/', cookies=user_dict.get(message.chat.id).token)
            rv = rv.json().get('user')

            chat_id = message.chat.id

            profile_data = UserProfile()
            user_data[chat_id] = profile_data
            profile_data.cur_email = rv.get('email')
            profile_data.username = rv.get('username')
            profile_data.first_name = rv.get('first_name')
            profile_data.last_name = rv.get('last_name')
            profile_data.phone = rv.get('phone')

            bot.send_message(message.from_user.id, user_data.get(chat_id).print_user_profile())
            user_markup = telebot.types.ReplyKeyboardMarkup()
            user_markup.row('/logout', '/edit_profile')
            user_markup.row('/delete_profile', '\N{House Building}')
            bot.send_message(message.from_user.id, 'You\'re available to', reply_markup=user_markup)
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


def gen_edit_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 5
    markup.add(InlineKeyboardButton('Email', callback_data=f'change_email'),
               InlineKeyboardButton('Username', callback_data=f'change_username'),
               InlineKeyboardButton('First Name', callback_data=f'change_f_name'),
               InlineKeyboardButton('Last Name', callback_data=f'change_l_name'),
               InlineKeyboardButton('Phone', callback_data=f'change_phone'))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message
    if call.data == 'change_f_name':
        bot.answer_callback_query(call.id, 'Enter a new first name')
        bot.register_next_step_handler(chat_id, upd_f_name)
    elif call.data == 'change_l_name':
        bot.answer_callback_query(call.id, 'Enter a new last name')
        bot.register_next_step_handler(chat_id, upd_l_name)
    elif call.data == 'change_email':
        bot.answer_callback_query(call.id, 'Enter a new email address')
        bot.register_next_step_handler(chat_id, upd_email)
    elif call.data == 'change_phone':
        bot.answer_callback_query(call.id, 'Enter a new phone')
        bot.register_next_step_handler(chat_id, upd_phone)
    elif call.data == 'change_username':
        bot.answer_callback_query(call.id, 'Enter a new username')
        bot.register_next_step_handler(chat_id, upd_username)
    elif call.data == 'change_url':
        bot.answer_callback_query(call.id, 'Enter a new url')
        bot.register_next_step_handler(chat_id, upd_url)
    elif call.data == 'change_title':
        bot.answer_callback_query(call.id, 'Enter a new title')
        bot.register_next_step_handler(chat_id, upd_title)
    elif call.data == 'change_login':
        bot.answer_callback_query(call.id, 'Enter a new login')
        bot.register_next_step_handler(chat_id, upd_login)
    elif call.data == 'change_pass':
        bot.answer_callback_query(call.id, 'Enter a new password')
        bot.register_next_step_handler(chat_id, upd_pass)
    elif call.data == 'change_comment':
        bot.answer_callback_query(call.id, 'Enter a new description')
        bot.register_next_step_handler(chat_id, upd_description)


def upd_f_name(message):
    try:
        chat_id = message.chat.id
        first_name = message.text
        user_data.get(chat_id).first_name = first_name

        rv = update_user_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def upd_l_name(message):
    try:
        chat_id = message.chat.id
        last_name = message.text
        user_data.get(chat_id).last_name = last_name

        rv = update_user_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def upd_phone(message):
    try:
        chat_id = message.chat.id
        phone = message.text
        user_data.get(chat_id).phone = phone

        rv = update_user_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def upd_email(message):
    try:
        chat_id = message.chat.id
        email = message.text
        user_data.get(chat_id).cur_email = email

        rv = update_user_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def upd_username(message):
    try:
        chat_id = message.chat.id
        username = message.text
        user_data.get(chat_id).username = username

        rv = update_user_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def update_user_data(chat_id):
    rv = requests.put(url + 'user/', json=dict(
        email=user_data.get(chat_id).cur_email,
        username=user_data.get(chat_id).username,
        first_name=user_data.get(chat_id).first_name,
        last_name=user_data.get(chat_id).last_name,
        phone=user_data.get(chat_id).phone
    ), cookies=user_dict.get(chat_id).token).json()
    
    return rv


def upd_url(message):
    try:
        chat_id = message.chat.id
        url = message.text
        pass_dict.get(chat_id).url = url

        rv = update_password_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def upd_title(message):
    try:
        chat_id = message.chat.id
        title = message.text
        pass_dict.get(chat_id).title = title

        rv = update_password_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def upd_login(message):
    try:
        chat_id = message.chat.id
        login = message.text
        pass_dict.get(chat_id).login = login

        rv = update_password_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def upd_pass(message):
    try:
        chat_id = message.chat.id
        password = message.text
        pass_dict.get(chat_id).password = password

        rv = update_password_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def upd_description(message):
    try:
        chat_id = message.chat.id
        comment = message.text
        pass_dict.get(chat_id).comment = comment

        rv = update_password_data(chat_id)
        bot.send_message(message.from_user.id, rv.get('message'))
    except Exception as err:
        bot.reply_to(message, err)


def update_password_data(chat_id):
    rv = requests.post(url + 'user/passwords', json=dict(
        url=pass_dict.get(chat_id).url,
        title=pass_dict.get(chat_id).title,
        login=pass_dict.get(chat_id).login,
        password=pass_dict.get(chat_id).password,
        comment=pass_dict.get(chat_id).comment
    ), cookies=user_dict.get(chat_id).token).json()
    
    return rv


@bot.message_handler(commands=['edit_profile'])
def handle_edit_profile_command(message):
    if user_dict.get(message.chat.id):
        if user_data.get(message.chat.id):
            try:
                bot.send_message(message.chat.id, 'Choose what you wanna change', reply_markup=gen_edit_markup())
            except Exception as err:
                bot.reply_to(message, err)
        else:
            bot.send_message(message.from_user.id, 'Please, firstly visit /profile')
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


@bot.message_handler(commands=['delete_profile'])
def handle_delete_profile_command(message):
    try:
        rv = requests.delete(url + 'user/', cookies=user_dict.get(message.chat.id).token)
        bot.send_message(message.from_user.id, rv)
    except Exception as err:
        bot.reply_to(message, err)


@bot.message_handler(commands=['get_passwords'])
def handle_get_passwords_command(message):
    if user_dict.get(message.chat.id):
        try:
            rv = requests.get(url + 'user/passwords', cookies=user_dict.get(message.chat.id).token)
            passwords = rv.json()
            counter = 0
            results = ''

            for pas in passwords.get('passwords'):
                counter += 1
                results = results + '/' + str(pas.get('pass_id')) + ' – ' + pas.get('title') + ': ' + pas.get(
                    'login') + '\n'
            # TODO MAX
            # six = get_six_passwords(results)
            # bot.send_message(message.from_user.id, six)
            header = f'Results of {counter} \n'
            results = header + results
            bot.send_message(message.from_user.id, results)
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


#
# def get_six_passwords(results):
#     all_passwords = results.split('\n')
#     list_six_pass = list()
#     six_pass = ''
#     i = 1
#
#     page = 1000
#     pass
#     #TODO pagination - for maxim
#     # incomt
#     elements = 6
#     start = page*elements
#     end = (page+1)*elements
#     length = len(all_passwords)
#
#     if page < length//elements:
#         data = all_passwords[start:end]
#     elif start*elements < length:
#         data = all_passwords[start:]
#
#     print(page, "---", '\n'.join(data))

# for pas in all_passwords:
#     six_pass = six_pass + pas + '\n'
#     i += 1
#     if i % 6 == 0:
#         list_six_pass.append(six_pass)
#         six_pass = ''
# print(list_six_pass)
# return list_six_pass


@bot.message_handler(commands=['logout'])
def handle_logout_command(message):
    if user_dict.get(message.chat.id):
        try:
            rv = requests.get(url + 'logout', cookies=user_dict.get(message.chat.id).token)
            rv = rv.json()
            user_dict.pop(message.chat.id)
            bot.send_message(message.from_user.id, rv.get('message'))
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


@bot.message_handler(commands=['search'])
def handle_search_command(message):
    if user_dict.get(message.chat.id):
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
        rv = requests.post(url + 'user/passwords/search', json=dict(condition=condition),
                           cookies=user_dict.get(message.chat.id).token)
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


@bot.message_handler(commands=['edit_pass_info'])
def handle_edit_pass_command(message):
    if user_dict.get(message.chat.id):
        try:
            user_markup = telebot.types.ReplyKeyboardMarkup()
            user_markup.row('/change_url', '/change_title')
            user_markup.row('/change_login', '/change_pass')
            user_markup.row('/change_comment', '\N{House Building}')
            bot.send_message(message.from_user.id, 'Choose, what to change', reply_markup=gen_edit_pass_markup())
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


@bot.message_handler(func=lambda message: re.match(r'/\d+', message.text))
def handle_get_particular_pass_command(message):
    if user_dict.get(message.chat.id):
        try:
            # removed / after passwords because message.text will be smth like /digit
            rv = requests.get(url + 'user/passwords' + message.text, cookies=user_dict.get(message.chat.id).token)
            rv = rv.json().get('password')
            bot.send_message(message.from_user.id, f'{rv}')
            chat_id = message.chat.id
            pass_id = message.text
            pass_dict = PasswordCredentials(pass_id)
            pass_dict[chat_id] = pass_dict
            user_markup = telebot.types.ReplyKeyboardMarkup()
            user_markup.row('/edit_pass_info', '/delete_password')
            user_markup.row('\N{House Building}')
            bot.send_message(message.from_user.id, 'Also, you are able to', reply_markup=user_markup)
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


@bot.message_handler(func=lambda message: re.match('\N{House Building}', message.text))
def handle_home(message):
    if not user_dict.get(message.chat.id):
        user_markup = telebot.types.ReplyKeyboardMarkup()
        user_markup.row('/login', '/help')
        bot.send_message(message.from_user.id, 'Please, choose what you\'d like to do', reply_markup=user_markup)
    if user_dict.get(message.chat.id):
        user_markup = telebot.types.ReplyKeyboardMarkup()
        user_markup.row('/profile', '/search')
        user_markup.row('/get_passwords', '/logout')
        bot.send_message(message.from_user.id, 'Please, choose what you\'d like to do', reply_markup=user_markup)


@bot.message_handler(commands=['delete_password'])
def handle_delete_password_command(message):
    if user_dict.get(message.chat.id):
        try:
            chat_id = message.chat.id
            # removed / after passwords because message.text will be smth like /digit
            rv = requests.delete(url + 'user/passwords' + pass_dict.get(chat_id).id,
                                 cookies=user_dict.get(message.chat.id).token)
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
