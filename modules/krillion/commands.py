"""Krillion leaderboards, stats, and the daily results post."""
import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

from modules.krillion.parser import GAME_TZ, date_for_day, today_day_number

log = logging.getLogger('discord.bot')

MEDALS = ('🥇', '🥈', '🥉')
BOARD_LIMIT = 25
GAME_URL = 'https://krillion.io'


def format_board(rows, guild, day, title=None) -> discord.Embed:
    """Render one day's scores. Ties keep their order: earliest submission first."""
    podium, rest = [], []
    for position, row in enumerate(rows[:BOARD_LIMIT]):
        # Someone who left the server is no longer a member, so fall back to a
        # mention, which Discord resolves to their name on its own.
        member = guild.get_member(row['user_id'])
        name = (discord.utils.escape_markdown(member.display_name[:32])
                if member else f"<@{row['user_id']}>")
        # One line each, so the tiles never sit directly under a medal and read
        # as a rank of their own. The top three keep bold names and a gap.
        if position < len(MEDALS):
            podium.append(f"{MEDALS[position]}  **{name}** — `{row['score']}`  {row['emoji']}")
        else:
            rest.append(f"`{position + 1}.` {name} — `{row['score']}`  {row['emoji']}")

    body = '\n\n'.join(podium)
    if rest:
        body += '\n\n' + '\n'.join(rest)

    embed = discord.Embed(
        title=title or f'Krillion #{day}',
        # Makes the title a link to the game. Discord renders no preview card
        # for it, so the board stays the only thing in the message.
        url=GAME_URL,
        description=body or 'Nobody dived today.',
        colour=discord.Colour.dark_teal())
    embed.set_footer(text=f'{date_for_day(day)} · {len(rows)} diver(s)')
    return embed


class KrillionBoard(commands.Cog):
    """Slash commands plus the loop that posts yesterday's results."""

    group = app_commands.Group(name='krillion', description='Krillion daily dive scores',
                               guild_only=True)

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.post_results.start()

    async def cog_unload(self):
        self.post_results.cancel()

    # -- commands ----------------------------------------------------------

    @group.command(name='today', description="Today's standings")
    async def today(self, interaction: discord.Interaction):
        """Current leaderboard, before the day is over."""
        day = today_day_number()
        rows = self.db.leaderboard(interaction.guild.id, day)
        await interaction.response.send_message(
            embed=format_board(rows, interaction.guild, day,
                               title=f'Krillion #{day} · so far'))

    @group.command(name='results', description='Render a day of results on demand')
    @app_commands.describe(day='Puzzle number. Defaults to today.')
    async def results(self, interaction: discord.Interaction, day: int = None):
        """The same embed the scheduled post uses — handy for checking format."""
        day = day or today_day_number()
        rows = self.db.leaderboard(interaction.guild.id, day)
        await interaction.response.send_message(
            embed=format_board(rows, interaction.guild, day))

    @group.command(name='stats', description='Someone\'s Krillion record')
    @app_commands.describe(member='Whose stats to show. Defaults to you.')
    async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
        """Games played, average, best, and the current daily streak."""
        member = member or interaction.user
        row = self.db.user_stats(interaction.guild.id, member.id)

        if not row['played']:
            # Embed titles ignore markdown, but a plain message doesn't.
            await interaction.response.send_message(
                f'{discord.utils.escape_markdown(member.display_name)} has not '
                'submitted a dive yet.', ephemeral=True)
            return

        embed = discord.Embed(title=f'{member.display_name} · Krillion',
                              colour=discord.Colour.dark_teal())
        embed.add_field(name='Dives', value=row['played'])
        embed.add_field(name='Average', value=f"{row['average']:.0f}")
        embed.add_field(name='Best', value=row['best'])
        embed.add_field(name='Streak', value=self._streak(interaction.guild.id, member.id))
        await interaction.response.send_message(embed=embed)

    @group.command(name='channel', description='Where the daily results post')
    @app_commands.describe(channel='Leave empty to turn the daily post off.')
    @app_commands.default_permissions(manage_guild=True)
    async def channel(self, interaction: discord.Interaction,
                      channel: discord.TextChannel = None):
        """Per-guild setting, so each server picks its own results channel."""
        self.db.set_results_channel(interaction.guild.id, channel.id if channel else None)
        where = channel.mention if channel else 'nowhere — daily results are off'
        log.info('Guild %s set Krillion results channel to %s',
                 interaction.guild.id, channel.id if channel else None)
        await interaction.response.send_message(f'Daily results will post to {where}.',
                                                ephemeral=True)

    # -- daily post --------------------------------------------------------

    @tasks.loop(time=datetime.time(hour=0, minute=5, tzinfo=GAME_TZ))
    async def post_results(self):
        """Post the day that just ended, a few minutes after it closes.

        The margin covers clock drift — firing before midnight would post the
        wrong day.
        """
        finished = today_day_number() - 1
        for guild_id, channel_id in self.db.guilds_awaiting(finished):
            guild = self.bot.get_guild(guild_id)
            channel = guild.get_channel(channel_id) if guild else None
            if channel is None:
                log.warning('Krillion results channel %s is gone', channel_id)
                continue

            rows = self.db.leaderboard(guild_id, finished)
            if not rows:
                self.db.mark_posted(guild_id, finished)
                continue

            try:
                await channel.send(embed=format_board(rows, guild, finished))
                self.db.mark_posted(guild_id, finished)
                log.info('Posted Krillion #%s results to %s', finished, channel_id)
            except discord.HTTPException as err:
                log.error('Could not post Krillion results to %s: %s', channel_id, err)

    @post_results.before_loop
    async def before_post(self):
        """Wait for the cache, or get_guild returns nothing."""
        await self.bot.wait_until_ready()

    def _streak(self, guild_id, user_id) -> int:
        """Consecutive days played, counting back from today or yesterday."""
        days = self.db.user_days(guild_id, user_id)
        if not days:
            return 0

        today = today_day_number()
        if days[0] not in (today, today - 1):
            return 0

        streak, expected = 0, days[0]
        for day in days:
            if day != expected:
                break
            streak += 1
            expected -= 1
        return streak
