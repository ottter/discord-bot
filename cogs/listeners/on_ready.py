import discord
from discord.ext import commands
from config import DEV_ACCOUNT_NAME, DEV_ACCOUNT_PREFIX, TIME


class OnReadyListen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Runs if login attempt is successful"""
        if self.bot.user.name == DEV_ACCOUNT_NAME:
            self.command_prefix = DEV_ACCOUNT_PREFIX

        ready_output = f"""
        {'='*34}
        Logged in as: {self.bot.user.name}
        Client ID   : {self.bot.user.id}
        Local time  : {TIME}
        {'='*34}\n"""

        try:
            print(ready_output)
            # synced = await self.bot.tree.sync()
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(OnReadyListen(bot))