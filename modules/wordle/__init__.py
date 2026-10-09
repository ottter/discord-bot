"""Wordle: plays each day's game from the colors on other players' boards.

Loaded as a single extension, so the solver, image reading and storage can
live beside the cogs. Try the solver without Discord with
`python -m modules.wordle`.
"""
from modules.wordle.commands import WordleCommands
from modules.wordle.games import BOARDS_NEEDED, GAME_TZ, Games
from modules.wordle.listener import WordleWatch
from modules.wordle.storage import WordleDB


async def setup(bot):
    """Adds the cogs (module) to startup. See main/load_extensions"""
    # Both cogs share the database and board tables, built once.
    games = Games(WordleDB(bot.config.get('WORDLE_DB')),
                  tz=bot.config.get('WORDLE_TZ') or GAME_TZ,
                  needed=int(bot.config.get('WORDLE_BOARDS') or BOARDS_NEEDED))
    await bot.add_cog(WordleWatch(bot, games))
    await bot.add_cog(WordleCommands(bot, games))
