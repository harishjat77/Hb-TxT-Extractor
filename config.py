#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) ACE

import os


class Config(object):
    # get a token from @BotFather
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714119859:AAHNEqUMoyhpY3bquVQVDBR9XXS4yQ1Reuo")
    API_ID = int(os.environ.get("API_ID", "31595997"))
    API_HASH = os.environ.get("API_HASH", "4e94f5b04d2c2fb0b275f50f01347257")
    AUTH_USERS = os.environ.get("AUTH_USERS", "6410653364")
