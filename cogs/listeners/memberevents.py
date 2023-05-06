"""Member related Discord functions"""
from discord.ext import commands
from config import ON_MEMBER_SERVERLIST
from config import timestamp as TIME


class MemberEventsListen(commands.Cog):
    """Class holding member events (member join, leave, kick, etc)"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(member):
        """Actions upon new member joining server"""

        welcome_channel = member.guild.system_channel
        print(f"{TIME()}: {member.mention} has joined the server {member.guild.id}")
        await welcome_channel.send(f'Welcome {member.mention}, I think?')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Actions upon channel member being removed"""
        welcome_channel = member.guild.system_channel
        print(f"{TIME()}: {member.mention} has left the server {member.guild.id}")
        await welcome_channel.send(f'Cya {member.mention} you dummy')

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(MemberEventsListen(bot))