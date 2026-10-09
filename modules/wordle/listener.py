"""Watches the Wordle app's posts and plays once a game has enough boards.

The app posts one message per game and edits it as people play, each time
with a new image of every board so far. So new messages and edits are both
read, and the newest image replaces the last.
"""
import asyncio
import io
import logging

import aiohttp
import discord
from discord.ext import commands

from modules.wordle import image
from modules.wordle.answers import current_game
from modules.wordle.games import grid, headline

log = logging.getLogger('discord.bot')

# The Wordle app's bot account.
APP_ID = 1211781489931452447


class WordleWatch(commands.Cog):
    """Reads the app's images and posts the locked result."""

    def __init__(self, bot, games):
        self.bot = bot
        self.games = games
        self.app_id = int(bot.config.get('WORDLE_APP_ID') or APP_ID)
        self.warned = False

    @commands.Cog.listener()
    async def on_ready(self):
        """Get the board tables going, so the first solve doesn't wait."""
        self.games.start_building()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """A new post from the app."""
        await self.read(message)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        """The app's post updated with another board. Edits may not be cached,
        so check the author from the raw data before fetching anything."""
        author = payload.data.get('author', {}).get('id')
        if author is None or int(author) != self.app_id:
            return
        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            return
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.HTTPException as err:
            log.warning('Could not fetch edited Wordle post %s: %s', payload.message_id, err)
            return
        await self.read(message)

    async def read(self, message):
        """Read the image, store the boards, and play once there are enough."""
        if message.author.id != self.app_id or not message.guild:
            return
        urls = image_urls(message)
        if not urls:
            if not self.warned:
                log.warning('Wordle post %s has no image I can find: %r',
                            message.id, message.components)
                self.warned = True
            return

        picture = await download(urls[0])
        if picture is None:
            return
        game, boards = await asyncio.to_thread(image.read, io.BytesIO(picture))
        if game is None:
            log.warning('Could not read the game number in Wordle post %s', message.id)
            return

        guild = message.guild.id
        async with self.games.locks[guild, game]:
            self.games.db.save_boards(guild, game, boards)
            answer = await self.games.answer(game)
            log.info('Wordle %s: %s board(s) in guild %s', game, len(boards), guild)
            if not answer or not self.ready_to_lock(guild, game, boards):
                return
            turns = await self.games.play(game, answer, boards)
            if not self.games.db.save_solve(guild, game, turns, len(boards)):
                return

        log.info('Wordle %s locked in guild %s: %s', game, guild, headline(game, turns))
        channel = message.guild.get_channel(self.games.db.channel(guild) or 0) or message.channel
        try:
            await channel.send(f'{headline(game, turns)}\n{grid(turns)}')
        except discord.HTTPException as err:
            log.error('Could not post the Wordle %s result: %s', game, err)

    def ready_to_lock(self, guild, game, boards) -> bool:
        """Enough boards, and nothing locked in yet. Once the day is over, the
        last /wordle play stands instead."""
        saved = self.games.db.solve(guild, game)
        if len(boards) < self.games.needed or (saved and saved[2]):
            return False
        return not saved or game >= current_game(self.games.tz)


def image_urls(message) -> list:
    """Every image in a message: attachments, embeds, and the newer layout
    where images sit in a gallery inside the message's components."""
    urls = [attachment.url for attachment in message.attachments
            if (attachment.content_type or '').startswith('image/')]
    urls += [embed.image.url for embed in message.embeds if embed.image and embed.image.url]
    parts = list(message.components)
    while parts:
        part = parts.pop(0)
        url = getattr(getattr(part, 'media', None), 'url', None)
        if url:
            urls.append(url)
        for name in ('children', 'items', 'components'):
            parts.extend(getattr(part, name, None) or [])
    return urls


async def download(url):
    """The image's bytes, or None."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        log.warning('Could not download Wordle image %s: %s', url, err)
        return None
