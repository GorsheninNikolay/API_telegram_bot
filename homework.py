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
BOT = telegram.Bot(token=TELEGRAM_TOKEN)

statuses = {
    "rejected": "К сожалению в работе нашлись ошибки.",
    "approved": "Ревьюеру всё понравилось, "
                "можно приступать к следующему уроку.",
    "reviewing": "Проект успешно отправлен и ожидает ревью."
}

logging.basicConfig(
    format="%(asctime)s"
           "%(levelname)5s"
           "%(name)5s"
           "%(message)5s",
           level=logging.DEBUG)


def parse_homework_status(homework: dict) -> str:
    homework_name = homework.get("homework_name")
    status = homework.get("status")
    if homework_name or status is None:
        logging.error("Wrong server response")
    verdict = statuses[status]
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp: int) -> dict:
    try:
        homework_statuses = requests.get(
            "https://praktikum.yandex.ru/api/user_api/homework_statuses/",
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
            params={'from_date': current_timestamp})
    except requests.RequestException:
        logging.error("Request Error.")
        return {}
    return homework_statuses.json()


def send_message(message: str,
                 bot_client: telegram.bot.Bot
                 ) -> telegram.bot.Bot.send_message:
    logging.info('Message has been sent.')
    return bot_client.send_message(CHAT_ID, message)


def main() -> None:
    current_timestamp = int(time.time())
    logging.debug('Bot has been successfully launched.')
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
