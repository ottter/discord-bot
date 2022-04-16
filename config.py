import os
import time
import datetime
from pymongo import MongoClient


# Discord token should be added to your path
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

# Token used by Heroku, in my case.
PRIMARY_ACCOUNT_PREFIX = '.'

# Dev account used for... deving. Ensures no conflict with live bot. Use a different prefix than live
DEV_ACCOUNT_NAME = 'testdogtestdog'
DEV_ACCOUNT_PREFIX = ','

# Mongo token should be added to your path
MONGO_TOKEN = MongoClient(f"{os.environ['MONGO_PASSWORD']}")
db = MONGO_TOKEN.get_database('discord')

# Gets a cool timestamp to use in logs or whatever
time = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")

# (Unsecure) way to filter additions to image db. I'll improve this later
accepted_hosts = ['discord', 'imgur', 'youtube', 'gyazo']
accepted_media_types = ['png', 'jpg', 'jpeg']
