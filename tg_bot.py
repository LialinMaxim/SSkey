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
url = os.environ.get('URL')
# url = 'http://sskey.herokuapp.com/'

print(bot.get_me())
user_dict = dict()
pass_dict = dict()


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
    msg = ["Commands 🔥 🔥 🔥",
           "Comfortable and secure way of storing your passwords. ",
           "Just remember your main password and SSkey remembers the rest.",
           "",
           "/login — Log in sskey.herokuapp.com",
           "/profile — Get yours data from sskey.herokuapp.com",
           "/get_passwords — Get list of user's passwords",
           "/logout — Log out sskey.herokuapp.com",
           "/search — Search for passwords by its description",
           "/edit_pass_info — Update user's password data",
           "/edit_profile — Update user's personal data",
           "/delete_password — Delete specific password",
           ]
    msg = "\n".join(msg)
    bot.send_message(message.from_user.id, msg)


@bot.message_handler(commands=['login'])
def handle_login_command(message):
    try:
        msg = bot.reply_to(message, "Hi there, I am SSkey bot. \nPlease, enter your email in order to login.")
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

            user_data = UserProfile()
            user_data.cur_email = rv.get('email')
            user_data.username = rv.get('username')
            user_data.first_name = rv.get('first_name')
            user_data.last_name = rv.get('last_name')
            user_data.phone = rv.get('phone')

            bot.send_message(message.from_user.id, user_data.print_user_profile())
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


def view_part_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('←', callback_data=f'move_left'),
               InlineKeyboardButton('→', callback_data=f'move_right'))
    return markup


# @bot.callback_query_handler(func=lambda call: True)
# def callback_query2(call):
#

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    page = 0
    if call.data == 'change_f_name':
        bot.answer_callback_query(call.id, 'Enter a new name')
    elif call.data == 'change_l_name':
        bot.answer_callback_query(call.id, 'Enter a new last name')
    elif call.data == 'change_email':
        bot.answer_callback_query(call.id, 'Enter a new email address')
    elif call.data == 'change_phone':
        bot.answer_callback_query(call.id, 'Enter a new phone')
    elif call.data == 'change_username':
        bot.answer_callback_query(call.id, 'Enter a new username')

    # view_part_markup
    elif call.data == 'move_left':
        page -= 1
        print('-1-')
        # bot.edit_message_text(chat_id=call.message.chat.id,
        #                       message_id=call.message.message_id,
        #                       reply_markup=view_part_markup(),
        #                       text=f"Пыщь {page}")
        # bot.answer_callback_query(call.id, '<<<')

    elif call.data == 'move_right':
        page += 1
        print('-2-')
        # bot.answer_callback_query(call.id, '>>>')


@bot.message_handler(commands=['edit_profile'])
def handle_edit_profile_command(message):
    if user_dict.get(message.chat.id):
        try:
            bot.send_message(message.chat.id, 'Choose what you wanna change', reply_markup=gen_edit_markup())
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


@bot.message_handler(commands=['delete_profile'])
def handle_delete_profile_command(message):
    try:
        rv = requests.delete(url + 'user/', cookies=user_dict.get(message.chat.id).token)
        bot.send_message(message.from_user.id, rv)
    except Exception as err:
        bot.reply_to(message, err)


def view_part(pass_list, page=0, elements=6):
    """Splits the list into separate pages.
    As a page can be any integer"""
    length = len(pass_list)
    if length % elements:
        pages = length // elements + 1
    else:
        pages = length // elements
    page = abs(pages + page) % pages

    start = page * elements
    if start == length:
        start = 0
    end = start + elements

    if end > length:
        passwords = pass_list[start:]
    else:
        passwords = pass_list[start:end]

    view = ''
    for p in passwords:
        id = p.get('pass_id')
        title = p.get('title')
        login = p.get('login')
        view += f'/{id} - {title} : {login}\n'
    return view


@bot.message_handler(commands=['get_passwords'])
def handle_get_passwords_command(message):
    if user_dict.get(message.chat.id):
        rv = requests.get(url + 'user/passwords', cookies=user_dict.get(message.chat.id).token)
        user_passwords = rv.json()['passwords']

        try:
            bot.send_message(message.chat.id, view_part(user_passwords), reply_markup=view_part_markup())
        except Exception as err:
            bot.reply_to(message, err)
    else:
        bot.send_message(message.from_user.id, 'You have to be logged in.')


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
        ), cookies=user_dict.get(message.chat.id).token)
        bot.send_message(message.from_user.id, rv)
    except Exception as err:
        bot.reply_to(message, err)


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
            user_pass = PasswordCredentials(pass_id)
            pass_dict[chat_id] = user_pass
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
