import os
import time
import datetime
from pymongo import MongoClient

# Gets a cool timestamp to use in logs or whatever
time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

# Discord token should be added to your path
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

discord_game_played = 'Runescape'

# Mongo token should be added to your path
MONGO_TOKEN = MongoClient(f"{os.environ['MONGO_PASSWORD']}")
db = MONGO_TOKEN.get_database('discord')

# (Unsecure) way to filter additions to image db. I'll improve this later
accepted_hosts = ['discord', 'imgur', 'youtube', 'gyazo']
accepted_media_types = ['png', 'jpg', 'jpeg']
