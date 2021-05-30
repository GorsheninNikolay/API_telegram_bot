import os
import time
import logging

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


class WrongStatus(Exception):
    pass


try:
    PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    BOT = telegram.Bot(token=TELEGRAM_TOKEN)
except Exception as token_error:
    logging.critical(f"Token has not been found!!!\nError: {token_error}")


logging.basicConfig(
    format='%(asctime)s,'
           '%(levelname)s,'
           '%(name)s,'
           '%(message)s',
           level=logging.DEBUG)


def parse_homework_status(homework: dict) -> str:
    try:
        homework_name = homework["homework_name"]
        status = homework["status"]
        if status not in ["rejected", "approved", "reviewing"]:
            raise WrongStatus("Wrong status of homework!")
    except Exception as error:
        logging.error(f"Wrong server respone: {error}")
        send_message(f"Wrong server respone: {error}", bot_client=BOT)
        time.sleep(600)
        parse_homework_status(homework)
    if status == "rejected":
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == "approved":
        verdict = 'Ревьюеру всё понравилось, '
        verdict += 'можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp: int) -> dict:
    try:
        homework_statuses = requests.get(
            "https://praktikum.yandex.ru/api/user_api/homework_statuses/",
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
            params={'from_date': current_timestamp})
    except requests.RequestException:
        send_message("Request Error.", bot_client=BOT)
        logging.error("Request Error.")
        time.sleep(600)
        get_homework_statuses(current_timestamp)
    return homework_statuses.json()


def send_message(message: str,
                 bot_client: telegram.bot.Bot
                 ) -> telegram.bot.Bot.send_message:
    logging.info('Message has been sent')
    return bot_client.send_message(CHAT_ID, message)


def main() -> None:
    current_timestamp = int(time.time())
    logging.debug('Бот успешно запущен.')
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    homework=new_homework.get('homeworks')[0]), bot_client=BOT)
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(1200)

        except Exception as e:
            logging.error(f'Bot got an error: {e}')
            send_message(f'Bot got an error: {e}', bot_client=BOT)
            time.sleep(600)


if __name__ == '__main__':
    main()
