import os

import telebot
import datasource
import oai_proxy
import logging


BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Started')


if __name__ == '__main__':
    main()


@bot.message_handler(commands=['help'])
def send_help(message):
    t_user = message.from_user

    if datasource.user_not_exists(t_user.id):
        datasource.save_user(datasource.User(t_user.id,
                                             t_user.first_name,
                                             t_user.last_name,
                                             t_user.username,
                                             t_user.language_code))

        send_welcome(message)

    bot.send_message(chat_id=message.chat.id,
                     text="/help for getting this message \n"
                     "/start for new chat with context \n"
                     "/stop for stop chat and clean context \n"
                     "/key for set new OpenAI API key \n"
                     "____________________________________________ \n\n")

    send_api_key_set_hint(message)
    send_api_key_hint(message)


@bot.message_handler(commands=['start', 'run'])
def start(message):
    t_user = message.from_user

    if datasource.user_exists(t_user.id):
        user = datasource.get_user(message.from_user.id)

        if user.oai_token:
            bot.send_message(chat_id=message.chat.id, disable_web_page_preview=True,
                             text="It looks like everything is ready to start 🫡 Just start chatting with ChatGPT 🤖")
        else:
            bot.send_message(chat_id=message.chat.id, disable_web_page_preview=True,
                             text="It seems to OpenAI API key not set yet 😕")

            send_api_key_set_hint(message)
            send_api_key_hint(message)
    else:
        send_help(message)


@bot.message_handler(commands=['key'])
def set_oai_token(message):
    t_user = message.from_user

    if datasource.user_not_exists(t_user.id):
        datasource.save_user(datasource.User(t_user.id,
                                             t_user.first_name,
                                             t_user.last_name,
                                             t_user.username,
                                             t_user.language_code))

    token = message.text.split(" ")[1]

    user = datasource.get_user(message.from_user.id)
    user.set_oai_token(token)
    datasource.save_user(user)

    logging.info("Token %s has sat for user %s", token, user.t_id)

    bot.send_message(chat_id=message.chat.id, disable_web_page_preview=True,
                     text="It looks like everything is ready to start 🫡 Just start chatting with ChatGPT 🤖")


@bot.message_handler(commands=['clean'])
def clean_context(message):
    t_user = message.from_user

    if datasource.user_exists(t_user.id):
        user = datasource.get_user(message.from_user.id)
        user.clean_context()
        datasource.save_user(user)

        bot.send_message(chat_id=message.chat.id, disable_web_page_preview=True,
                         text="Contex with ChatGPT clean now. "
                              "You can start new conversation. Just send messages to start")
    else:
        send_help(message)


@bot.message_handler(func=lambda msg: True)
def chat_gpt_message_bus(message):
    t_user = message.from_user

    if datasource.user_not_exists(t_user.id):
        send_help(message)
    else:
        user = datasource.get_user(t_user.id)

        # if openai token is empty make request not possible
        if user.oai_token:
            user.new_message(message.text)

            replay = oai_proxy.chat_request(user.oai_token, user.model, user.get_context())

            user.new_message(replay)
            datasource.save_user(user)

            bot.send_message(chat_id=message.chat.id, disable_web_page_preview=True,
                             text=replay)
        else:
            send_welcome(message)


def send_welcome(message):
    t_user = message.from_user
    user = datasource.get_user(t_user.id)

    name = "Unknown"

    if user.first_name:
        name = user.first_name
    else:
        name = user.username

    bot.send_message(chat_id=message.chat.id, disable_web_page_preview=True,
                     text="Hi " + name + " jan ☺️ Nice to meet you! 🎉 \n"
                          "____________________________________________ \n\n")


def send_api_key_set_hint(message):
    bot.send_message(chat_id=message.chat.id, disable_web_page_preview=True,
                     text="That bot will help you collaborate with OpenAI ChatGPT easier via Telegram. \n"
                          "All you have to do that get your OpenAI API key and provide it here with command: \n"
                          "/key {key_content} \n \n"
                          "Here is example: \n"
                          "/key 4567898432:HHgtyasdasdiuIUIUBVghgjhghjsagdyuTY \n"
                          "____________________________________________ \n\n")


def send_api_key_hint(message):
    bot.send_message(chat_id=message.chat.id, disable_web_page_preview=True,
                     text="Steps for get OpenAI API key from OpenAI site: \n"
                          "1. Go to https://platform.openai.com/login \n"
                          "2. Click on your image int the right upper corner \n"
                          "3. Click on View API keys \n"
                          "4. Click on '+ Create new secret key' \n"
                          "____________________________________________ \n\n")

bot.infinity_polling()

