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
            log.error('KRILLION_SUBMIT_CHANNEL is not a channel id: %r', channel)
            self.submit_channel = None

        setting = (bot.config.get('KRILLION_COOLDOWN')
                   or os.environ.get('DISCORD_BOT_KRILLION_COOLDOWN'))
        try:
            seconds = float(setting) if setting else SUBMIT_PER
        except (TypeError, ValueError):
            log.error('KRILLION_COOLDOWN is not a number: %r', setting)
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
            log.info('Rejected %s: %s', message.author, err)
            await self._reject(message, str(err))
            return

        if result is None:
            return

        # Shares are read anywhere, but only count in the submit channel.
        if self.submit_channel and message.channel.id != self.submit_channel:
            log.debug('Krillion share from %s outside the submit channel',
                      message.author)
            await self._reject(message, f'scores only count in <#{self.submit_channel}>')
            return

        today = today_day_number()
        if result['day'] != today:
            reason = (f"that's day #{result['day']}, and today is #{today}"
                      " — only today's dive counts")
            log.info('Rejected %s: stale day %s', message.author, result['day'])
            await self._reject(message, reason)
            return

        # Last, so a rejected paste doesn't burn the cooldown. Throttled
        # messages go silently — reacting just gives a spammer something to watch.
        retry_after = self.cooldown.update_rate_limit(message)
        if retry_after:
            log.info('Throttled %s, %.0fs left', message.author, retry_after)
            return

        try:
            previous = self.db.save_score(
                message.guild.id, message.author.id, result,
                datetime.datetime.now(GAME_TZ).isoformat())
        except sqlite3.Error as err:
            log.error('Could not save score for %s: %s', message.author, err)
            await self._reject(message, 'the scoreboard is unavailable right now')
            return

        # A replacement reacts like any other accept; the change belongs in
        # the log, not in chat.
        if previous is None:
            log.info('Accepted %s: %s on day %s', message.author, result['score'], today)
        else:
            log.info('Replaced %s on day %s: %s -> %s',
                     message.author, today, previous, result['score'])
        await self._react(message, ACCEPTED)

    async def _react(self, message, emoji):
        """Reactions are cosmetic, so a missing permission shouldn't raise."""
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException as err:
            log.warning('Could not react to %s: %s', message.id, err)

    async def _reject(self, message, reason):
        """Mark the message and say why, quietly enough not to derail chat."""
        await self._react(message, REJECTED)
        try:
            await message.reply(f'Not counted — {reason}.', mention_author=False,
                                delete_after=30)
        except discord.HTTPException as err:
            log.warning('Could not reply to %s: %s', message.id, err)
