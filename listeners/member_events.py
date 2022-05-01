"""Member related Discord functions"""
from discord.ext import commands
from config import ON_MEMBER_SERVERLIST


class MemberEvents(commands.Cog):
    """Class holding member events (member join, leave, kick, etc)"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Actions upon new member joining server"""
        if member.guild.id in ON_MEMBER_SERVERLIST.keys():
            welcome_channel = self.bot.get_channel(ON_MEMBER_SERVERLIST[member.guild.id])
            await welcome_channel.send(f'Welcome {member.mention}, I think?')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Actions upon channel member being removed"""
        if member.guild.id in ON_MEMBER_SERVERLIST.keys():
            welcome_channel = self.bot.get_channel(ON_MEMBER_SERVERLIST[member.guild.id])
            await welcome_channel.send(f'Cya {member.mention} you dummy')

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(MemberEvents(bot))
