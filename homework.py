import os
import time
import logging

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(
    format='%(asctime)-10s,'
           '%(levelname)-10s,'
           '%(name)-10s,'
           '%(message)s')


def parse_homework_status(homework):
    # Getting homework name
    homework_name = homework["homework_name"]
    if homework["status"] == "rejected":
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, '
        verdict += 'можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    # Getting homework status
    homework_statuses = requests.get(
        "https://praktikum.yandex.ru/api/user_api/homework_statuses/",
        headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
        params={'from_date': current_timestamp})
    return homework_statuses.json()


def send_message(message, bot_client):
    """ In argument we are getting data of the last homework and bot_client"""
    logging.info('Message has been sent')
    return bot_client.send_message(CHAT_ID, message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)  # Bot initialization
    current_timestamp = int(time.time())  # first value for timestamp
    logging.debug('Бот успешно запущен.')
    while True:
        try:
            send_message("Идет проверка...", bot_client=bot)
            # Getting homework with the given time - current_timestamp
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    homework=new_homework.get('homeworks')[0]), bot_client=bot)
            # update timestamp
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(1200)  # sleep 20 minutes for the next request

        except Exception as e:
            logging.error(f'Bot got an error: {e}')
            send_message(f'Bot got an error: {e}', bot_client=bot)
            time.sleep(600)


if __name__ == '__main__':
    main()
