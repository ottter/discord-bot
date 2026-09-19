"""Krillion daily dive scores: submission, leaderboards and the daily post.

Loaded as a single extension, so parser and storage can live beside the cogs
without the loader treating them as extensions of their own.
"""
from modules.krillion.commands import KrillionBoard
from modules.krillion.listener import KrillionSubmit
from modules.krillion.storage import KrillionDB


async def setup(bot):
    """Adds the cogs (module) to startup. See main/load_extensions"""
    # Both cogs share one database handle, so the file opens once.
    db = KrillionDB(bot.config.get('KRILLION_DB'))
    await bot.add_cog(KrillionSubmit(bot, db))
    await bot.add_cog(KrillionBoard(bot, db))
