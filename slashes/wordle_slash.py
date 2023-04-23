"""Meme SLASH commands go here"""
from discord.ext.commands import Cog
from discord_slash import cog_ext, SlashContext

from modules.wordle import play_wordle
from config import TIME, MODULE_SUBDIR


class SlashWordle(Cog):
    """All slash commands.
    Bot MUST be invited with 'applications.commands' permission for use"""

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="wordle",
        description="Have bot attempt the daily Wordle")
    async def _play_wordle(self, context:SlashContext):
        """More directly Wordle themed content"""

        wrdl = play_wordle(custom_list='data/wordlists/sorted-valid-wordle-words.txt',
                       print_output=False, starting_word='stole')
        
        # For some reason the number is a few days behind, even though the word is correct
        # wrdl_day = int(wrdl['wordle_num']) + 3      # Current Wordle day
        wrdl_output = f"Wordle {int(wrdl['wordle_num'])+3} {wrdl['guess_count']}/6*\n{wrdl['emoji_block']}"
        await context.send(wrdl_output)
        
        self.bot.reload_extension(f'{MODULE_SUBDIR}.wordle')
        print(f"{TIME}: Wordle {int(wrdl['wordle_num'])+3} path: {wrdl['guess_path']}")
        print(f'{TIME}: Reloaded Wordle module (wordle command)')

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(SlashWordle(bot))
