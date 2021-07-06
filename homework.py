import os
import time
import requests
import logging

from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
load_dotenv()

from telegram import Bot


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log', 
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('my_logger.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status == 'reviewing':
        verdict = 'Проект находится на ревью.'
    elif homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    homework_statuses_url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    return requests.get(homework_statuses_url, headers=headers, params=payload).json()


def send_message(message):
    if message is not None:
        return bot.send_message(CHAT_ID, message)
    pass


def main():
    timestamp = int(time.time())

    while True:
        try:
            homeworks_statuses = get_homeworks(timestamp)
            if len(homeworks_statuses['homeworks']) > 0:
                message = parse_homework_status(homeworks_statuses['homeworks'][0])
            else:
                message = 'нет домашек'
            send_message(message)
            time.sleep(20 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            logging.error(e, exc_info=True)
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
