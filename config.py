import os
import time
import datetime
from pymongo import MongoClient


# Discord token should be added to your path. Keep this extra secure.
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

# Token used by Heroku, in my case. STRING
PRIMARY_ACCOUNT_PREFIX = '.'

# Dev account used for... deving. Ensures no conflict with live bot. Use a different prefix than live. STRING(S)
DEV_ACCOUNT_NAME = 'testdogtestdog'
DEV_ACCOUNT_PREFIX = ','

# Channel ID to send messages to bot's DMs to. INTEGER
PRIVATE_CHANNEL = 966507830641315860

# Scan all servers for wordlers?
WORDLE_GLOBAL_BAN = False
# Integer list of all servers/guilds & channels to moderate. LIST(INT)
WORDLE_BAN_LIST = [786399511651287041,963213566733873192,918187449845424158]

# Mongo token should be added to your path
MONGO_TOKEN = MongoClient(f"{os.environ['MONGO_PASSWORD']}")
db = MONGO_TOKEN.get_database('discord')

# Gets a cool timestamp to use in logs or whatever
time = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")

# (Unsecure) way to filter additions to image db. I'll improve this later. LIST(STR)
accepted_hosts = ['discord', 'imgur', 'youtube', 'gyazo']
accepted_media_types = ['png', 'jpg', 'jpeg']
