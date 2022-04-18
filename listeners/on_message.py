from discord.ext import commands
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
        
        if context.channel.id == 786399511651287041:
            for key, value in rdleverse_dict.items():
                if re.search(value.lower(), message):
                    print(f'Put a {key}r in their place')
                    await context.channel.send(f"Get lost, {key}r")

        if message.startswith('!co2'):
            await context.channel.send('Also CO2 is good for plants, meaning more CO2 means more life-sustaining oxygen '
                                       'and thus increase in agriculture as plants grow faster, more food, etc.')

        await self.bot.process_commands(context)

def setup(bot):
    bot.add_cog(OnMessage(bot))