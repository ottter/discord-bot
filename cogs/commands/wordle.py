"""Solve the daily Wordle"""
from discord.ext import commands

from config import MODULE_SUBDIR, FILES_SUBDIR
from config import timestamp as TIME
from scripts.wordle import play_wordle

wordlist = "sorted-valid-wordle-words.txt"

def path_output(wrdl):
    return f"Here's how I got **Wordle {int(wrdl['wordle_num'])+3}**:\n||{wrdl['guess_path']}||"

def play_output(wrdl):
    return f"Wordle {int(wrdl['wordle_num'])+3} {wrdl['guess_count']}/6*\n{wrdl['emoji_block']}"

class WordleCmd(commands.Cog):
    """Wordle themed content"""

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def wordle(self, context):
        """More directly Wordle themed content"""
        try: 
            message = context.message.content.split(" ", 1)[1].lower()
        except: 
            message = "play"

        if message in ["play", "path"] or message is False:

            wrdl = play_wordle(custom_list=f"{FILES_SUBDIR}/wordlists/{wordlist}",
                        print_output=False, starting_word='stole')
        
            if message == "path":
                return await context.send(path_output(wrdl))
            
            else:
                return await context.send(play_output(wrdl))
        
        else:
            await context.send("Accepted `wordle` subcommands: `path`, `play`")
        
        await self.bot.reload_extension(f"{MODULE_SUBDIR}.commands.wordle")
        print(f"{TIME()}: Reloaded Wordle module (via WordleCmd)")
        print(f"{TIME()}: Wordle {int(wrdl['wordle_num'])+3} path: {wrdl['guess_path']}")

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(WordleCmd(bot))