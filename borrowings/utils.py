import requests
from dotenv import load_dotenv
import os
import logging

from telegram import Bot

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logger = logging.getLogger(__name__)


def send_telegram_message(message):
    # bot = Bot(token=TELEGRAM_TOKEN)
    # bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }

    logger.info(f"Sending message to Telegram: {message}")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"Response: {response.status_code}, {response.json()}")
    except requests.RequestException as e:
        logger.error(f"Error sending Telegram message: {e}")
        return None

    return response
