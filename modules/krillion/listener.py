"""Watches for pasted Krillion shares and records them."""
import datetime
import logging
import os
import sqlite3

import discord
from discord.ext import commands

from modules.krillion.parser import GAME_TZ, ParseError, parse_share, today_day_number

log = logging.getLogger('discord.bot')

ACCEPTED = '🦐'
REJECTED = '💀'

# One stored score per user per minute. Per-user, so a rush of people all
# posting at once is fine — only one person repeating themselves is throttled.
SUBMIT_RATE = 1
SUBMIT_PER = 60.0


class KrillionSubmit(commands.Cog):
    """Accepts share text posted in chat, no command needed."""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        # Scores only count in this channel. Unset means anywhere.
        channel = (bot.config.get('KRILLION_SUBMIT_CHANNEL')
                   or os.environ.get('DISCORD_BOT_KRILLION_SUBMIT_CHANNEL'))
        try:
            self.submit_channel = int(channel) if channel else None
        except ValueError:
            log.error('Krillion: KRILLION_SUBMIT_CHANNEL is not a channel id: %r', channel)
            self.submit_channel = None

        setting = (bot.config.get('KRILLION_COOLDOWN')
                   or os.environ.get('DISCORD_BOT_KRILLION_COOLDOWN'))
        try:
            seconds = float(setting) if setting else SUBMIT_PER
        except (TypeError, ValueError):
            log.error('Krillion: KRILLION_COOLDOWN is not a number: %r', setting)
            seconds = SUBMIT_PER
        self.cooldown = commands.CooldownMapping.from_cooldown(
            SUBMIT_RATE, seconds, commands.BucketType.user)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):  # pylint: disable=too-many-return-statements
        """Fires for every message, so drop out early on anything irrelevant.

        Written as a checklist rather than nested ifs, so the order of the
        rules stays obvious.
        """
        if message.author.bot or not message.guild:
            return
        if not message.content.lstrip().startswith('Krillion'):
            return

        try:
            result = parse_share(message.content)
        except ParseError as err:
            log.info('Krillion: rejected %s in %s #%s: %s', message.author,
                     message.guild.name, message.channel.name, err)
            await self._reject(message, str(err))
            return

        if result is None:
            return

        # Shares are read anywhere, but only count in the submit channel.
        if self.submit_channel and message.channel.id != self.submit_channel:
            log.info('Krillion: rejected %s in %s #%s: outside the submit channel',
                     message.author, message.guild.name, message.channel.name)
            await self._reject(message, f'scores only count in <#{self.submit_channel}>')
            return

        today = today_day_number()
        if result['day'] != today:
            reason = (f"that's day #{result['day']}, and today is #{today}"
                      " — only today's dive counts")
            log.info('Krillion: rejected %s in %s: day %s, today is %s',
                     message.author, message.guild.name, result['day'], today)
            await self._reject(message, reason)
            return

        # Last, so a rejected paste doesn't burn the cooldown. Throttled
        # messages go silently — reacting just gives a spammer something to watch.
        retry_after = self.cooldown.update_rate_limit(message)
        if retry_after:
            log.info('Krillion: throttled %s in %s, %.0fs left',
                     message.author, message.guild.name, retry_after)
            return

        try:
            previous = self.db.save_score(
                message.guild.id, message.author.id, result,
                datetime.datetime.now(GAME_TZ).isoformat())
        except sqlite3.Error as err:
            log.error('Krillion: could not save the score from %s in %s: %s',
                      message.author, message.guild.name, err)
            await self._reject(message, 'the scoreboard is unavailable right now')
            return

        board = self.db.leaderboard(message.guild.id, today)
        rank = next((i for i, row in enumerate(board, 1)
                     if row['user_id'] == message.author.id), '?')
        # A replacement reacts like any other accept; the change belongs in
        # the log, not in chat.
        if previous is None:
            log.info('Krillion #%s: accepted %s in %s: %s, %s of %s today',
                     today, message.author, message.guild.name, result['score'],
                     rank, len(board))
        else:
            log.info('Krillion #%s: replaced %s in %s: %s -> %s, %s of %s today',
                     today, message.author, message.guild.name, previous,
                     result['score'], rank, len(board))
        await self._react(message, ACCEPTED)

    async def _react(self, message, emoji):
        """Reactions are cosmetic, so a missing permission shouldn't raise."""
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException as err:
            log.warning('Krillion: could not react to message %s in %s: %s',
                        message.id, message.guild.name, err)

    async def _reject(self, message, reason):
        """Mark the message and say why, quietly enough not to derail chat."""
        await self._react(message, REJECTED)
        try:
            await message.reply(f'Not counted — {reason}.', mention_author=False,
                                delete_after=30)
        except discord.HTTPException as err:
            log.warning('Krillion: could not reply to message %s in %s: %s',
                        message.id, message.guild.name, err)
