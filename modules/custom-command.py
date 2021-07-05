from discord.ext import commands
from discord import Game
from admin import banned_users, bot_admins
import discord
import config
import json


class Aliases(commands.Cog):
    """Basic bot admin-level controls"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(alias='add_alias')
    async def add_alias(self, context, user: discord.User, *alias):
        user = str(context.message.author.id)
        if
        if str(context.message.author.id) in bot_admins or user.id == context.message.author.id:
            if len(alias) > 1:
                await context.send('The alias must be a single word.')
                return

            config.db['aliases'].update_one({'_id': user.id}, {'$addToSet': {'aliases': ' '.join(alias)}}, upsert=True)

            await context.send('Successfully added alias.')


def setup(bot):
    bot.add_cog(Aliases(bot))
