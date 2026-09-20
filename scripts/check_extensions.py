"""Check that every extension loads.

load_extensions logs a bad cog and moves on, so check what registered rather than
waiting for an exception.
"""
import asyncio
import sys
from pathlib import Path

import discord

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import DiscordBot, find_extensions  # pylint: disable=wrong-import-position


async def main() -> None:
    """Load everything, then report what made it."""
    print('discord.py', discord.__version__)
    expected = set(find_extensions())

    bot = DiscordBot(command_prefix=',', intents=discord.Intents.default(),
                     help_command=None)
    async with bot:
        await bot.setup_hook()
        loaded = set(bot.extensions)
        cogs = sorted(bot.cogs)
        commands = sorted(cmd.name for cmd in bot.tree.get_commands())

    print(f'Extensions ({len(loaded)}/{len(expected)}):',
          ', '.join(sorted(loaded)) or 'none')
    print(f'Cogs ({len(cogs)}):', ', '.join(cogs) or 'none')
    print(f'Slash commands ({len(commands)}):', ', '.join(commands) or 'none')

    missing = expected - loaded
    if missing:
        sys.exit(f'Failed to load: {", ".join(sorted(missing))}')
    if not loaded:
        sys.exit('No extensions found — check the modules/ directory.')


if __name__ == '__main__':
    asyncio.run(main())
