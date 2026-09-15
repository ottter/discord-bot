"""Verify every extension loads and registers. Needs no token or network.

setup_hook() does all the local work — importing cogs and building the command
tree — while bot.start() is the only part that authenticates, so CI can run this
without credentials. main.load_extensions logs failures rather than raising, so
this asserts on the result instead of relying on an exception.
"""
import asyncio
import sys
from pathlib import Path

import discord

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import (  # pylint: disable=wrong-import-position
    EXTENSION_DIRS, EXTENSION_EXCLUSIONS, DiscordBot)


def expected_extensions() -> set:
    """Every module main.load_extensions should have picked up."""
    modules = Path(__file__).resolve().parent.parent / 'modules'
    return {
        f.stem
        for name in EXTENSION_DIRS
        if (modules / name).is_dir()
        for f in (modules / name).glob('*.py')
        if f.stem not in EXTENSION_EXCLUSIONS
    }


async def main() -> None:
    """Load everything, then report what did and did not register."""
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
