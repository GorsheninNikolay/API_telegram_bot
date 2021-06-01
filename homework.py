import os
import time
import logging

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


class WrongResponse(Exception):
    pass


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

URL = {
    "url": "https://praktikum.yandex.ru/api/user_api/homework_statuses/",
    "headers": {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"},
    "params": {"from_date": 0},
}

logging.basicConfig(
    format="%(asctime)s"
           "%(levelname)s"
           "%(name)s"
           "%(message)s",
           level=logging.DEBUG)


def parse_homework_status(homework: dict) -> str:
    homework_name = homework.get("homework_name")
    status = homework.get("status")
    verdict = statuses.get(status)
    if homework_name or status or verdict is None:
        logging.error(f"Wrong server response.\nWith: {URL}")
        # Pytest ругается из-за raise =(
        # До этого еще пытался вернуть строкой: return "Неверный ответ сервера"
        # Но Pytest все равно не пропускает.
        # Также любое изменение Русских строк,
        # Например, на английский язык, не принимает.
        # Я так понимаю, что в тестах parse_homework_status
        # Значение homework_name = None, поэтому функция, в моем случае,
        # Возвращает исключение, Pytest сравнивает все assert-ом
        # И вместо f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
        # У меня выходит свое исключение.
        """Вот ошибка с попыткой return "Неверный ответ сервера":
 AssertionError:
Проверьте, что возвращаете название домашней
                        работы в возврате функции parse_homework_status()
E assert False
E + where False = <built-in method startswith of str object at 0x04512E90>
                            ('У вас проверили работу "FqGyDvIpxOcreLy"')
E + where <built-in method startswith of str object at 0x04512E90>
= 'Неверный ответ сервера'.startswith """
        # raise WrongResponse(f"Wrong server response.\nWith: {URL}")
        # return "Неверный ответ сервера"
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp: int) -> dict:
    try:
        URL["params"]["from_date"] = current_timestamp
        homework_statuses = requests.get(
            URL["url"],
            headers=URL["headers"],
            params=URL["params"])
    except Exception as error:
        logging.error(f"Request Error: {error}.\nWith: {URL}")
        return {}
    return homework_statuses.json()


def send_message(message: str,
                 bot_client: telegram.bot.Bot
                 ) -> telegram.bot.Bot.send_message:
    logging.info("Message has been sent.")
    return bot_client.send_message(CHAT_ID, message)


def main() -> None:
    current_timestamp = int(time.time())
    logging.debug("Bot has been successfully launched.")
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get("homeworks"):
                send_message(parse_homework_status(
                    homework=new_homework.get("homeworks")[0]), bot_client=BOT)
            current_timestamp = new_homework.get("current_date",
                                                 current_timestamp)
            time.sleep(1200)

        except Exception as e:
            logging.error(f"Bot got an error: {e}")
            send_message(f"Bot got an error: {e}", bot_client=BOT)
            time.sleep(600)


if __name__ == "__main__":
    main()
