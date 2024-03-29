"""Module that collects and shows memorable quotes from special people"""
import random
import urllib
from discord.ext import commands

from config import ACCEPTED_HOSTS, ACCEPTED_MEDIA_TYPES, db
from config import timestamp as TIME


BANNED_USERS = [
    '635226170698235925',   # jebbers
    '941144178136600647',   # mort
]

BOT_ADMINS = [
    '918084315290673152',   # me
    '205144077144948737',   # liam
]


def valid_host(host):
    """Compares input URL against list from config.py"""
    if host in ACCEPTED_HOSTS:
        return True
    return False


def valid_media_type(media_type):
    """Compares input URL's media type against list from config.py"""
    return media_type in ACCEPTED_MEDIA_TYPES


def add_image(context, person):
    """ Tests the URL and adds to specific collection csv"""
    args = context.message.content.split(" ")

    parsed_url = urllib.parse.urlparse(args[1])
    host = parsed_url.hostname.split('.')[0]
    media_type = args[1].split('.')[-1]

    if not valid_host(host) and not valid_media_type(media_type):  # Tests for imgur image URL
        return context.send('Invalid URL, try again.')

    collection = db['people']
    # Prevent duplicate inputs
    collection.update_one({'image_url': args[1]}, {'$set': {'person': person}}, upsert=True)
    return context.send(f'Added to the `{person}` collection')


def random_image(context, person):
    """ Returns a random Imgur URL from the selected file"""
    collection = db['people']
    images = collection.find({'person': person})
    row = []
    for image in images:
        row.append(image['image_url'])
    rand_img = random.choice(list(row))
    return context.channel.send(rand_img)


class People(commands.Cog):
    """Channel-specific Quotes and memes"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def people(self, context):
        """Stat count on People database"""
        collection = db['people']
        person_count = []
        count_dict = {}
        for person in collection.find({}, {'_id': 0, 'person': 1}):
            person_count.append(person['person'])
        for person in list(set(person_count)):
            count_dict[person] = person_count.count(person)
        person_print = [f'`{k.capitalize()}: {v}`\t' for k, v in sorted(count_dict.items())]

        await context.send('Current Image Totals:\n')
        await context.send(''.join(person_print))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def lights(self, context):
        """Shows you the best of Lights473"""

        await random_image(context, 'lights')

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def add_lights(self, context):
        """Add to the Lights collection"""
        if str(context.author.id) in BANNED_USERS:
            await context.send(f'I can\'t do that, {context.author.mention}')
            return print(f'{TIME}: {context.author} failed to add image Banned.')

        await add_image(context, 'lights')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['jeb'])
    async def jebrim(self, context):
        """Shows you the best of Jebrim"""

        await random_image(context, 'jebrim')

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def add_jebrim(self, context):
        """Add to the Jebrim collection"""
        if str(context.author.id) in BANNED_USERS:
            await context.send(f'I can\'t do that, {context.author.mention}')
            return print(f'{TIME}: {context.author} failed to add image. Reason: Banned')

        await add_image(context, 'jebrim')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def lathow(self, context):
        """Shows you the best of Lathow"""

        await random_image(context, 'lathow')

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def add_lathow(self, context):
        """Add to the Lathow collection"""

        await add_image(context, 'lathow')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def pgt(self, context):
        """Shows you the best of Pgt"""

        await random_image(context, 'pgt')

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def add_pgt(self, context):
        """Add to the Pgt collection"""

        await add_image(context, 'pgt')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def philo(self, context):
        """Shows you the best of PhiloChat"""

        await random_image(context, 'philo')

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def add_philo(self, context):
        """Add to the PhiloChat collection"""
        if str(context.message.author.id) in BOT_ADMINS:
            await add_image(context, 'philo')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def corona(self, context):
        """Shows you the best Corona quotes"""

        await random_image(context, 'corona')


async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(People(bot))