import discord
from discord.ext import commands
from config import TIME


class PingCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, context):
        """Test latency to server"""
        server_ping = round(self.bot.latency * 1000)
        print(f"{TIME}: {context.author} pinged the server: {server_ping}ms")
        await context.send(f"Ping: {server_ping}ms")

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(PingCmd(bot))