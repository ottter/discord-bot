"""Check that every extension loads. No token needed — setup_hook() is all local.

load_extensions logs a bad cog and moves on, so check what registered rather than
waiting for an exception.
"""
import asyncio
import sys
from pathlib import Path

import discord

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import (  # pylint: disable=wrong-import-position
    EXTENSION_DIRS, EXTENSION_EXCLUSIONS, DiscordBot)


def expected_extensions() -> set:
    """The modules load_extensions should have found."""
    modules = Path(__file__).resolve().parent.parent / 'modules'
    return {
        f.stem
        for name in EXTENSION_DIRS
        if (modules / name).is_dir()
        for f in (modules / name).glob('*.py')
        if f.stem not in EXTENSION_EXCLUSIONS
    }


async def main() -> None:
    """Load everything, then report what made it."""
    print('discord.py', discord.__version__)
    bot = DiscordBot(command_prefix=',', intents=discord.Intents.default(),
                     help_command=None)
    async with bot:
        await bot.setup_hook()
        loaded = {name.rsplit('.', 1)[-1] for name in bot.extensions}
        commands = sorted(cmd.name for cmd in bot.tree.get_commands())

    expected = expected_extensions()
    print(f'Extensions ({len(loaded)}/{len(expected)}):', ', '.join(sorted(loaded)) or 'none')
    print(f'Slash commands ({len(commands)}):', ', '.join(commands) or 'none')

    missing = expected - loaded
    if missing:
        sys.exit(f'Failed to load: {", ".join(sorted(missing))}')
    if not loaded:
        sys.exit('No extensions found — check EXTENSION_DIRS.')


if __name__ == '__main__':
    asyncio.run(main())
