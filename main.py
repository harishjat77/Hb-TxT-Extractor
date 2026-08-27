#  MIT License
#
#  Copyright (c) 2019-present Dan <https://github.com/delivrance>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.


import asyncio
import logging

import tgcrypto
from config import Config
from pyrogram import Client, idle
from pyrogram.errors import FloodWait
from pyromod import listen
from logging.handlers import RotatingFileHandler


LOGGER = logging.getLogger(__name__)


logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "log.txt",
            maxBytes=5000000,
            backupCount=10
        ),
        logging.StreamHandler(),
    ],
)


# Auth Users
AUTH_USERS = [
    int(chat.strip())
    for chat in Config.AUTH_USERS.split(",")
    if chat.strip()
]


# Prefixes
prefixes = ["/", "~", "?", "!"]


# Plugins
plugins = dict(root="plugins")


# Temporary debug
print("API_ID:", Config.API_ID)
print("API_HASH length:", len(Config.API_HASH))
print("BOT_TOKEN present:", bool(Config.BOT_TOKEN))


bot = Client(
    name="StarkBot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    sleep_threshold=20,
    plugins=plugins,
    workers=50
)


async def start_bot():
    while True:
        try:
            await bot.start()
            return
        except FloodWait as error:
            wait_seconds = int(error.value) + 1
            LOGGER.warning(
                "Telegram rate limit during startup; retrying in %s seconds",
                wait_seconds,
            )
            if bot.is_connected:
                await bot.disconnect()
            await asyncio.sleep(wait_seconds)


async def main():
    await start_bot()

    bot_info = await bot.get_me()

    LOGGER.info(
        f"<--- @{bot_info.username} Started (c) STARKBOT --->"
    )

    await idle()

    await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())

    LOGGER.info("<--- Bot Stopped --->")
