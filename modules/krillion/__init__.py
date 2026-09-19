"""Krillion daily dive scores: submission, leaderboards and the daily post.

Loaded as a single extension, so parser and storage can live beside the cogs
without the loader treating them as extensions of their own.
"""
from modules.krillion.commands import KrillionBoard
from modules.krillion.listener import KrillionSubmit


async def setup(bot):
    """Adds the cogs (module) to startup. See main/load_extensions"""
    await bot.add_cog(KrillionSubmit(bot))
    await bot.add_cog(KrillionBoard(bot))
