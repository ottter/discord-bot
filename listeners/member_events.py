"""Member related Discord functions"""
from discord.ext import commands

class MemberEvents(commands.Cog):
    """Class holding member events (member join, leave, kick, etc)"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Actions upon channel member being removed"""
        primary_server_base_id = None
        primary_welcome_channel = None
        if primary_server_base_id and member.guild.id == primary_server_base_id:
            channel = self.bot.get_channel(primary_welcome_channel)
            await channel.send(f'Cya {member} you dummy')

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(MemberEvents(bot))
