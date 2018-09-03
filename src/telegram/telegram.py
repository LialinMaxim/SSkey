import telebot
token = "624028048:AAF-s19gxNL6sN_IhLCdLVpvmyP2mmxbWoc"
bot = telebot.TeleBot(token)

# bot.send_message(397833851, 'hi test')

# upd = bot.get_updates()
# print(upd)

# last_upd = upd[-1]
# message_from_user = last_upd.message
# print(message_from_user)


@bot.message_handler(commands=['art'])
def handle_text(message):
    print('go commands')


@bot.message_handler(content_types=['text'])
def hedle_command(message):
    print('text income:', message.text)
    if 'a' in message.text:
        num = message.text.count('a')
        bot.send_message(message.chat.id, f"a: {num}")

bot.polling(none_stop=True, interval=0)