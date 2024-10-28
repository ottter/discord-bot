import yaml
import discord
from main import timestamp
from discord.ext import commands


with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

PRIMARY_ACCOUNT_PREFIX = config["PRIMARY_ACCOUNT_PREFIX"]

class OnReadyListen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Confirm successful login when the bot is ready."""

        print(f"\n{'='*34}")
        print(f"Username   : {self.bot.user.name}")
        print(f"Client ID  : {self.bot.user.id}")
        print(f"Local time : {timestamp()}")
        print(f"Cmd Prefix : {PRIMARY_ACCOUNT_PREFIX}")
        print(f"{'='*34}\n")


async def setup(bot):
    await bot.add_cog(OnReadyListen(bot))