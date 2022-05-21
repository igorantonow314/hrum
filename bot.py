import json
import logging
import os

from aiogram import Bot, Dispatcher, executor
from aiogram.types import InputTextMessageContent, InlineQueryResultArticle, InlineQuery, Message

import scan

DEFAULT_CONF = "bot.conf"


def load_conf(conf=DEFAULT_CONF):
    if not os.path.exists(conf):
        save_conf({'version': 0.1}, conf)
    with open(conf, 'r') as f:
        return json.load(f)


def save_conf(data, conf=DEFAULT_CONF):
    with open(conf, 'w') as f:
        json.dump(data, f)


BOT_TOKEN = load_conf().get('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def start_msg(message: Message):
    await message.reply("Привет! Я буду присылать тебе свежие хрумы. Ты также можешь попросить меня найти нужный выпуск, для этого просто напиши его название.")


@dp.message_handler(commands=["force_update"])
async def update(message: Message):
    logger.info('scanning for new updates...')
    for t, v in scan.get_updates():
        await message.answer_chat_action("upload_photo")
        await message.reply_photo(v.thumbnail_url, caption='Новый выпуск! ' + t)
        await message.answer_chat_action("typing")
    await message.answer('Я посмотрел все обновления')
    logger.info('updates processed!')



@dp.message_handler(commands=["last"])
async def send_last(message: Message):
    await message.answer_chat_action("typing")
    v = scan.get_last_hrum()
    await message.answer_chat_action("upload_document")
    await message.reply_photo(v.thumbnail_url, caption='Новый выпуск! ' + v.title)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)