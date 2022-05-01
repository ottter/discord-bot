"""Configuration settings"""
import os
import time
import datetime
from pymongo import MongoClient


# Discord token should be added to your path. Keep this extra secure.
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

# Token used by Heroku, in my case. STRING
PRIMARY_ACCOUNT_PREFIX = '.'

# Local dev account used for testing. Use a different prefix than live. STRINGS
DEV_ACCOUNT_NAME = 'testdogtestdog'
DEV_ACCOUNT_PREFIX = ','

# Users who are to be given "admin" access to the bot. LIST(STRING)
BOT_ADMINS = [
    '918084315290673152',   # me
    ]

# List for active on_member events (leave, join server). {SERVER_ID: WECLOME_CHANNEL_ID}
ON_MEMBER_SERVERLIST = {
    963213566733873192: 970377569956425779,
    918187449845424158: 918187449845424161,
    436267595365351434: 436267595365351436,
}

# Decides what the bot should show as currently being played
DISCORD_GAME_PLAYED='Vim Tutorial'

# Channel ID to send messages to bot's DMs to. INTEGER
PRIVATE_CHANNEL = 966507830641315860

# Scan all servers for wordlers?
WORDLE_GLOBAL_BAN = False
# Integer list of all servers/guilds & channels to moderate. LIST(INT)
WORDLE_BAN_LIST = [
    786399511651287041,
    963213566733873192,
    918187449845424158,
    ]

# Mongo token should be added to your path
MONGO_TOKEN = MongoClient(f"{os.environ['MONGO_PASSWORD']}")
db = MONGO_TOKEN.get_database('discord')

# Gets a cool timestamp to use in logs or whatever
time = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")

# (Unsecure) way to filter additions to image db. I'll improve this later. LIST(STR)
ACCEPTED_HOSTS = ['discord', 'imgur', 'youtube', 'gyazo']
ACCEPTED_MEDIA_TYPES = ['png', 'jpg', 'jpeg']
