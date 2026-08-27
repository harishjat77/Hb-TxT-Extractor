#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) ACE

import os


class Config(object):
    # get a token from @BotFather
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714119859:AAHNEqUMoyhpY3bquVQVDBR9XXS4yQ1Reuo")
    API_ID = int(os.environ.get("API_ID", "35201189"))
    API_HASH = os.environ.get("API_HASH", "d7b7c2cb7f08e16c9b10638dad8b9795")
    AUTH_USERS = os.environ.get("AUTH_USERS", "6410653364")
