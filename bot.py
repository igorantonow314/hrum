import json
import logging
import os

from typing import Union

from aiogram import Bot, Dispatcher, executor
from aiogram.types import (
    InputTextMessageContent,
    InlineQueryResultArticle,
    InlineQuery,
    Message,
    InputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pytube import YouTube

import scan

DEFAULT_CONF = "bot.conf"


def load_conf(conf=DEFAULT_CONF):
    if not os.path.exists(conf):
        save_conf({"version": 0.1}, conf)
    with open(conf, "r") as f:
        return json.load(f)


def save_conf(data, conf=DEFAULT_CONF):
    with open(conf, "w") as f:
        json.dump(data, f)


BOT_TOKEN = load_conf().get("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def start_msg(message: Message):
    await message.reply(
        "Привет! Я буду присылать тебе свежие хрумы. Ты также можешь попросить меня найти нужный выпуск, для этого просто напиши его название.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Последний выпуск", callback_data="last")],
                [
                    InlineKeyboardButton(
                        "Проверить обновления!", callback_data="force_update"
                    )
                ],
            ]
        ),
    )


@dp.callback_query_handler(lambda x: x.data == "force_update")
@dp.message_handler(commands=["force_update"])
async def update(x: Union[Message, CallbackQuery]):
    logger.info("scanning for new updates...")
    if hasattr(x, "message"):
        # it is callback
        message = x.message
        await x.answer()
    else:
        message = x
    await message.answer_chat_action("typing")
    for t, v in scan.get_updates():
        await send_hrum(v, message=message)
        await message.answer_chat_action("typing")
    await message.reply("Я посмотрел все обновления.", disable_notification=True)
    logger.info("updates processed!")


@dp.callback_query_handler(lambda x: x.data == "last")
@dp.message_handler(commands=["last"])
async def send_last(message_or_callback: Union[Message, CallbackQuery]):
    if hasattr(message_or_callback, "message"):
        # it is callback
        message = message_or_callback.message
        await message_or_callback.answer()
    else:
        message = message_or_callback
    await message.answer_chat_action("typing")
    v = scan.get_last_hrum()
    await send_hrum(v, message)


async def send_hrum(v: YouTube, message: Message):
    await message.answer_chat_action("upload_document")
    await message.answer_audio(
        audio=InputFile(scan.get_hrum_audio_filename(v)), caption=scan.get_title(v)
    )


@dp.message_handler()
async def find(message: Message):
    await message.answer_chat_action("typing")
    hrums = scan.find_hrums(message.text)
    ik = []
    for _, v in zip(range(10), hrums):
        ik.append(
            [
                InlineKeyboardButton(
                    scan.get_title(v), callback_data=f"get {v.watch_url}"
                )
            ]
        )
    ikm = InlineKeyboardMarkup(inline_keyboard=ik)
    await message.reply("Результаты поиска:", reply_markup=ikm)


@dp.callback_query_handler(lambda x: x.data.startswith("get"))
async def get_hrum(callback: CallbackQuery):
    url = callback.data.split()[1]
    await send_hrum(message=callback.message, v=YouTube(url))
    await callback.answer()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
