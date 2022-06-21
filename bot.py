from syslog import LOG_INFO, LOG_PERROR
from telegram.ext import *
from time import time, strftime, localtime

import telegram
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

log_path = ""
keyword_path = ""
telegram_bot_token = ""

def log_error(func, msg):
    logfile = "{}/{}.log".format(log_path, "errors")
    linelog = "\n{}:\t\t[{}] - {}".format(
        strftime("%Y-%m-%d %H:%M:%S", localtime()), func, msg)
    open(logfile, "a+").write(linelog)


def log_info(func, msg):
    logfile = "{}/{}.log".format(log_path, "info")
    linelog = "\n{}:\t\t[{}] - {}".format(
        strftime("%Y-%m-%d %H:%M:%S", localtime()), func, msg)
    open(logfile, "a+").write(linelog)

# Bot function reply

def list(update, context):
    try:
        file = open(keyword_path, "r")
        content = file.read()
        file.close()
        context.bot.send_message(chat_id=update.effective_chat.id, text=content)
    except Exception as ex:
        context.bot.send_message(chat_id=update.effective_chat.id, text=ex)


def add(update, context):
    try:   
        data = update.message.text.split("\n")
        if len(data) < 2:
            data = data[0].split()
            data[1] += "\n"
        data.pop(0)
        file = open(keyword_path, "a")
        file.write('\n'.join(data))
        file.close()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Đã thêm, chạy /list lại để kiểm tra")
    except Exception as ex:
        context.bot.send_message(chat_id=update.effective_chat.id, text=ex)


def remove(update, context):
    try:   
        data = update.message.text.split("\n")
        if len(data) < 2:
            data = data[0].split()
        data.pop(0)
        lst = []
        file = open(keyword_path, "r")
        for line in file:
            for word in data:
                if word in line:
                    line = line.replace(word,'').strip() 
            lst.append(line)
        file.close()
        file = open(keyword_path, "w")
        for line in lst:
            file.write(line)
        file.close()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Đã xoá, chạy /list lại để kiểm tra")
    except Exception as ex:
        context.bot.send_message(chat_id=update.effective_chat.id, text=ex)


def bot_handler():
    try:
        updater = Updater(
            token=telegram_bot_token, use_context=True)
        dispatcher = updater.dispatcher

        # Init bot with API token
        bot = telegram.Bot(token=telegram_bot_token)
        bot_info = bot.get_me()
        log_info("bot_handler", "botname: {} (id={}) aka {} was deployed successful!".format(
            bot_info["username"], bot_info["id"], bot_info["first_name"]))
    except Exception as ex:
        log_info("bot_handler", "Load API failed! - {}".format(ex))

    # Command handler
    start_handler = CommandHandler('list', list)
    dispatcher.add_handler(start_handler)
    updater.start_polling()

    haniz_handler = CommandHandler('add', add)
    dispatcher.add_handler(haniz_handler)
    updater.start_polling()

    sendfile_handler = CommandHandler('remove', remove)
    dispatcher.add_handler(sendfile_handler)
    updater.start_polling()

if __name__ == '__main__':
    bot_handler()