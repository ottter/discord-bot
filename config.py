import os
import time
import datetime
from pymongo import MongoClient

time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

DISCORD_TOKEN = 'NjU3MTE3MTQ5NjEyOTk4NjU3.XfsiCQ.fiD5uwIseat1kGbuxnaBEXio46Q'

discord_game_played = 'Runescape'

accepted_hosts = ['discord', 'imgur', 'youtube', 'gyazo']
accepted_media_types = ['png', 'jpg', 'jpeg']