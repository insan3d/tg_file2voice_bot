#!/usr/bin/env python3

#  This program is free software. It comes without any warranty, to
#  the extent permitted by applicable law. You can redistribute it
#  and/or modify it under the terms of the Do What The Fuck You Want
#  To Public License, Version 2, as published by Sam Hocevar. See
#  http://www.wtfpl.net/ for more details.

"""
Converts files to voice message as Telegram bot.

API token may be specified as BOT_TOKEN environment variable.
"""

import asyncio
import logging

from argparse import ArgumentParser, HelpFormatter
from contextlib import suppress
from os import getenv
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

import ffmpeg

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, Filter
from aiogram.types import ContentType, Message
from aiogram.types.input_file import FSInputFile

__prog__ = "tg_file2voice_bot"
__version__ = "0.1.0"
__author__ = "Alexadner Pozlevich"
__email__ = "apozlevich@gmail.com"

router = Router()


class TypeFilter(Filter):
    """Filters message by it's type."""

    def __init__(
        self,
        allowed_types: Iterable[ContentType] = (
            ContentType.VOICE,
            ContentType.VIDEO,
            ContentType.VIDEO_NOTE,
            ContentType.AUDIO,
        ),
    ):
        self.allowed_types = allowed_types

    async def __call__(self, message: Message):
        if message.content_type in self.allowed_types:
            return message


@router.message(Command("start", "help"))
async def help_handler(message: Message):
    """Process /start and /help commands."""

    await message.reply(text="Отправь мне файл и я отвечу голосовым")


@router.message(TypeFilter())
async def process_message(message: Message):
    """Process media content."""

    if message.voice:
        file_id = message.voice.file_id

    elif message.video:
        file_id = message.video.file_id

    elif message.video_note:
        file_id = message.video_note.file_id

    elif message.audio:
        file_id = message.audio.file_id

    # No support for aiofiles :'(
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        in_file, out_file = str(tmp_path / "input"), str(tmp_path / "output.ogg")

        await message.bot.download(file=file_id, destination=in_file)

        (
            ffmpeg.input(in_file)
            .output(out_file, acodec="libopus", loglevel="quiet")
            .run()
        )

        await message.reply_audio(audio=FSInputFile(path=out_file))


async def init(token: str):
    """Bot bootstrap routine."""

    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router=router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        args_parser = ArgumentParser(
            prog=__prog__,
            description=__doc__,
            epilog=f"Written by {__author__} <{__email__}>.",
            formatter_class=lambda prog: HelpFormatter(
                prog=prog,
                max_help_position=35,
            ),
        )

        args_parser.add_argument(
            "--version",
            action="version",
            version=__version__,
        )

        logging_args = args_parser.add_mutually_exclusive_group()

        logging_args.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="enable debug verbosity",
        )

        logging_args.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="be less verbose",
        )

        token_arg = args_parser.add_mutually_exclusive_group()
        token_arg.add_argument(
            "-t",
            "--token",
            metavar="API_TOKEN",
            help="specify Telegram API token",
        )
        token_arg.add_argument(
            "-f",
            "--token-file",
            metavar="PATH",
            help="specify Telegram API token file path",
        )

        args = args_parser.parse_args()

        if args.verbose:
            logging.basicConfig(level=logging.DEBUG)

        elif args.quiet:
            logging.basicConfig(level=logging.WARNING)

        else:
            logging.basicConfig(level=logging.INFO)

        if args.token_file:
            with open(file=args.token_file, mode="r", encoding="utf-8") as token_r:
                bot_token = token_r.read().strip()

        elif args.token:
            bot_token = args.token

        else:
            bot_token = getenv("BOT_TOKEN")

        assert bot_token
        asyncio.run(init(token=bot_token))
