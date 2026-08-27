from pyrogram import filters
from pyrogram import Client as stark
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from main import LOGGER, prefixes, AUTH_USERS
from config import Config
import os
import sys


@stark.on_message(filters.command(["restart"]))
async def restart_handler(_, m):
    await m.reply_text("Restarted!", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@stark.on_message(filters.command(["log"]))
async def log_msg(bot: stark , m: Message):   
    await bot.send_document(m.chat.id, "log.txt")
