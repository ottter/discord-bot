"""Member related Discord functions"""
from discord.ext import commands
from config import ON_MEMBER_SERVERLIST
from config import timestamp as TIME


class MemberEventsListen(commands.Cog):
    """Class holding member events (member join, leave, kick, etc)"""
    def __init__(self, bot):
        self.bot = bot

    # NOTE: I think there is a new way to do this in 2.0

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     """Actions upon new member joining server"""
    #     for server in ON_MEMBER_SERVERLIST:
    #         if member.guild.id in server:
    #             welcome_channel = self.bot.get_channel(ON_MEMBER_SERVERLIST[member.guild.id])
    #             print(f"{TIME()}: {member.mention} has joined the server {server}")
    #             await welcome_channel.send(f'Welcome {member.mention}, I think?')

    # @commands.Cog.listener()
    # async def on_member_remove(self, member):
    #     """Actions upon channel member being removed"""
    #     for server in ON_MEMBER_SERVERLIST:
    #         if member.guild.id in server:
    #             welcome_channel = self.bot.get_channel(ON_MEMBER_SERVERLIST[member.guild.id])
    #             print(f"{TIME()}: {member.mention} has left the server {server}")
    #             await welcome_channel.send(f'Cya {member.mention} you dummy')

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(MemberEventsListen(bot))