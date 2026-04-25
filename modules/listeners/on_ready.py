from discord.ext import commands
from utils import timestamp


class OnReadyListen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Confirm successful login when the bot is ready."""
        prefix = self.bot.command_prefix
        print(f"\n{'='*34}")
        print(f"Username   : {self.bot.user.name}")
        print(f"Client ID  : {self.bot.user.id}")
        print(f"Local time : {timestamp()}")
        print(f"Cmd Prefix : {prefix}")
        print(f"{'='*34}\n")

        await self.bot.tree.sync()


async def setup(bot):
    await bot.add_cog(OnReadyListen(bot))
