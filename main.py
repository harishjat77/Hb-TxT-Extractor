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
import json
import logging
import sys

import aiohttp
import tgcrypto
from config import Config
from pyrogram import Client, idle
from pyrogram.errors import FloodWait
from pyromod import listen
from logging.handlers import RotatingFileHandler


LOGGER = logging.getLogger(__name__)


# Plugins import shared values with ``from main import ...``. When this file is
# started as a script, Python normally registers it only as ``__main__`` and
# importing ``main`` would execute the whole module a second time, creating a
# second Pyrogram Client. Point both module names at the same running module so
# every plugin uses the one Client that is actually started below.
sys.modules.setdefault("main", sys.modules[__name__])


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


START_MESSAGE = (
    "Hi, I am All in One Extractor Bot.\n\n"
    "/pw - Physics Wallah\n"
    "/e1 - E1 Coaching App\n"
    "/vidya - Vidya Bihar App\n"
    "/ocean - Ocean Gurukul App\n"
    "/winners - The Winners Institute\n"
    "/rgvikramjeet - Rgvikramjeet App\n"
    "/txt - Ankit With Rojgar, The Mission Institute, The Last Exam App\n"
    "/cp - Classplus App\n"
    "/cw - Careerwill App\n"
    "/khan - Khan GS App\n"
    "/exampur - Exampur App\n"
    "/samyak - Samayak IAS\n"
    "/chandra - Chandra App\n"
    "/mgconcept - Mgconcept App\n"
    "/down - Download URL lists\n"
    "/forward - Forward from one channel to another\n\n"
    "Bot Owner: YASH"
)


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


async def bot_api_start_fallback():
    """Answer /start through Bot API when MTProto updates are not delivered."""
    api_url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}"
    offset = None
    timeout = aiohttp.ClientTimeout(total=40)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            params = {
                "timeout": 25,
                "allowed_updates": json.dumps(["message"]),
            }
            if offset is not None:
                params["offset"] = offset

            try:
                async with session.get(
                    f"{api_url}/getUpdates",
                    params=params,
                ) as response:
                    payload = await response.json(content_type=None)

                if not payload.get("ok"):
                    LOGGER.warning(
                        "Bot API update polling failed: %s",
                        payload.get("description", "unknown error"),
                    )
                    await asyncio.sleep(3)
                    continue

                start_messages = {}
                for update in payload.get("result", []):
                    update_id = update.get("update_id")
                    if isinstance(update_id, int):
                        offset = max(offset or 0, update_id + 1)

                    message = update.get("message") or {}
                    text = (message.get("text") or "").strip()
                    if not text:
                        continue
                    command = text.split(maxsplit=1)[0].split("@", 1)[0].lower()
                    chat_id = (message.get("chat") or {}).get("id")
                    if command == "/start" and isinstance(chat_id, int):
                        start_messages[chat_id] = message.get("message_id")

                for chat_id, message_id in start_messages.items():
                    reply_parameters = (
                        {"message_id": message_id}
                        if isinstance(message_id, int)
                        else None
                    )
                    request_body = {
                        "chat_id": chat_id,
                        "text": START_MESSAGE,
                    }
                    if reply_parameters:
                        request_body["reply_parameters"] = reply_parameters

                    async with session.post(
                        f"{api_url}/sendMessage",
                        json=request_body,
                    ) as response:
                        result = await response.json(content_type=None)

                    if result.get("ok"):
                        LOGGER.info("Handled /start command via Bot API fallback")
                    else:
                        LOGGER.warning(
                            "Bot API /start response failed: %s",
                            result.get("description", "unknown error"),
                        )
            except asyncio.CancelledError:
                raise
            except (
                aiohttp.ClientError,
                asyncio.TimeoutError,
                json.JSONDecodeError,
            ) as error:
                LOGGER.warning(
                    "Bot API fallback connection failed: %s",
                    type(error).__name__,
                )
                await asyncio.sleep(3)


async def main():
    await start_bot()

    bot_info = await bot.get_me()

    LOGGER.info(
        f"<--- @{bot_info.username} Started (c) STARKBOT --->"
    )

    fallback_task = asyncio.create_task(
        bot_api_start_fallback(),
        name="bot-api-start-fallback",
    )
    try:
        await idle()
    finally:
        fallback_task.cancel()
        await asyncio.gather(fallback_task, return_exceptions=True)
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())

    LOGGER.info("<--- Bot Stopped --->")
