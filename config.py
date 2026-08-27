import os


class Config(object):
    BOT_TOKEN = os.environ["BOT_TOKEN"].strip()
    API_ID = int(os.environ["API_ID"].strip())
    API_HASH = os.environ["API_HASH"].strip()
    AUTH_USERS = os.environ.get("AUTH_USERS", "").strip()
