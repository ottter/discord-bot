"""Module that processes all received messages"""
import re
import emoji
import discord
from discord.ext import commands
from config import WORDLE_GLOBAL_BAN, WORDLE_BAN_LIST, PRIVATE_CHANNEL


rdleverse_dict = {
    "Wordle": "(Wordle \\d{1,} \\d/\\d)",                             # Wordle 298 3/6
    "Letterle": "(Letterle \\d{1,}/26)",                              # Letterle 7/26
    "Heardle": "(#Heardle #)\\d{1,}",                                 # #Heardle #47
    "Dordle": "(Daily Dordle #\\d{4} )((0-9|X)&(0-9|X)/7)",           # Daily Dordle #0078 X&X/7
    "Tridle": "(TRIDLE - \\d{1,}/3 words, (\\d{1,}/8 tries|failed))", # TRIDLE- 3/3 words, 7/8 tries
    "Quordle": "(Daily Quordle \\d{2,})",                             # Daily Quordle 78
    "Duotrigordle": "(Daily Duotrigordle #\\d{2,})",                  # Daily Duotrigordle #42
    "Lewdle": "(Lewdle 🍆💦 \\d{2,})( (\\d{1}|X)(/6))",              # Lewdle 🍆💦 83 5/6
    }

class OnMessage(commands.Cog):
    """Class handling all viewable messages"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, context):
        """Actions upon seeing any message in viewable channel"""
        message = str(context.content.lower())

        if context.author == self.bot.user:
            return

        # Relays received DM to specified channel (based on ID)
        if context.channel.type is discord.ChannelType.private:
            priv = self.bot.get_channel(PRIVATE_CHANNEL)
            if len(context.attachments) > 0:    # Length check required to avoid IndexError
                await priv.send(f'{context.author} sent me this:\n{context.attachments[0].url}')
            else:
                await priv.send(f'{context.author} sent me this:\n{context.content}')

        # Moderates a wordler if either of the options are True by telling them to leave
        if (WORDLE_GLOBAL_BAN) or (context.channel.id in WORDLE_BAN_LIST) or (context.guild.id in WORDLE_BAN_LIST):
            square_count = len(re.findall("(_square:)", emoji.demojize(message)))
            for key, value in rdleverse_dict.items():
                if re.search(value.lower(), message):
                    print(f'Put a {key}r in their place ({context.author})')
                    return await context.channel.send(f"Get lost, {key}r")
            if square_count > 9:
                return await context.channel.send("Not even close to avoiding my wrath")

        # await self.bot.process_commands(context)

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(OnMessage(bot))
