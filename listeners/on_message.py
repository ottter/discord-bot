from discord.ext import commands
import config
import discord
import re


rdleverse_dict = { 
    "Wordle": "(Wordle )\d{1,}( )-?(([0]|[3-9]|\d{2,})|X)(\/(6|\d{3,}))", # Wordle 298 3/6
    "Letterle": "(Letterle \d{1,}/26)",                                   # Letterle 7/26
    "Heardle": "(#Heardle #)\d{1,}",                                      # #Heardle #47
    "Dordle": "(Daily Dordle #\d{4} )((0-9|X)&(0-9|X)/7)",                # Daily Dordle #0078 X&X/7
    "Tridle": "(TRIDLE - \d{1,}/3 words, (\d{1,}/8 tries|failed))",       # TRIDLE - 3/3 words, 7/8 tries
    "Quordle": "(Daily Quordle \d{2,})",                                  # Daily Quordle 78
    "Duotrigordle": "(Daily Duotrigordle #\d{2,})",                       # Daily Duotrigordle #42
    "Lewdle": "(Lewdle 🍆💦 \d{2,})( (\d{1}|X)(/6))",                    # Lewdle 🍆💦 83 5/6
    }

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, context):
        message = str(context.content.lower())
        if context.author == self.bot.user:
            return

        # If someone sends the bot a dm, that message will be relayed to a selected channel (based on ID)
        if context.channel.type is discord.ChannelType.private:
            private_channel = self.bot.get_channel(config.PRIVATE_CHANNEL)
            if len(context.attachments) > 0:    # Length check required to avoid IndexError
                await private_channel.send(f'{context.author} sent me this:\n{context.attachments[0].url}')
            else:
                await private_channel.send(f'{context.author} sent me this:\n{context.content}')
        
        # Moderates a wordler if either of the options are True by telling them to leave
        if (config.WORDLE_GLOBAL_BAN) or (context.channel.id or context.guild.id in config.WORDLE_BAN_LIST):
            for key, value in rdleverse_dict.items():
                if re.search(value.lower(), message):
                    print(f'Put a {key}r in their place')
                    await context.channel.send(f"Get lost, {key}r")

        # Removed until I figure out why having this made commands run twice. Solution was add on_message event to main
        # await self.bot.process_commands(context)

def setup(bot):
    bot.add_cog(OnMessage(bot))