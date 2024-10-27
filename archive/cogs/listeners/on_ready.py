import discord
from discord.ext import commands
from config import DEV_ACCOUNT_NAME, DEV_ACCOUNT_PREFIX
from config import DEFAULT_ACTIVITY, PRIMARY_ACCOUNT_PREFIX
from config import timestamp as TIME


class OnReadyListen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Runs if login attempt is successful"""
        if self.bot.user.name == DEV_ACCOUNT_NAME:
            self.command_prefix = DEV_ACCOUNT_PREFIX

        try:
            await self.bot.change_presence(status=discord.Status.dnd, 
                                           activity=discord.Game(DEFAULT_ACTIVITY))

            synced = await self.bot.tree.sync()

            print(f"{'='*34}")
            print(f"Logged in as: {self.bot.user.name}")
            print(f"Client ID   : {self.bot.user.id}")
            print(f"Local time  : {TIME()}")
            print(f"Synced /CMD : {len(synced)}")
            print(f"Cmd Prefix  : {PRIMARY_ACCOUNT_PREFIX}")
            print(f"{'='*34}\n")

        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(OnReadyListen(bot))