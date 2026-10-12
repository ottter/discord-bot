"""/wordle slash commands: play, stats, simulate and channel."""
import logging

import discord
from discord import app_commands
from discord.ext import commands

from modules.wordle.games import (blind_note, board, guesses_taken, headline, official_note,
                                  spoilers, tally)
from modules.wordle.solver import OPENER, load_words

log = logging.getLogger('discord.bot')


class WordleCommands(commands.Cog):
    """Slash commands for the Wordle solver."""

    group = app_commands.Group(name='wordle', description='Wordle solver', guild_only=True)

    def __init__(self, bot, games):
        self.bot = bot
        self.games = games

    async def result(self, guild_id, game=None):
        """(game, turns, answer, boards used, blind play, locked result), or a
        string if it can't. The blind play is None when there were no boards,
        and the locked result is (turns, boards) or None.

        Always plays with every guild's boards so far, none needed. Until
        today's game is locked in, that's saved as provisional. An earlier
        game is only replayed, never saved."""
        today = self.games.today(guild_id)
        game = today if game is None else game
        if not 0 <= game <= self.games.newest(guild_id):
            return f"Wordle {game} can't be played: it's not out yet, or doesn't exist."
        answer = await self.games.answer(game, keep=game == today)
        if not answer:
            return f"Can't look up Wordle {game} right now. Try again in a bit."
        saved = self.games.db.solve(guild_id, game)
        locked = (saved[0], saved[1]) if saved and saved[2] else None
        boards = self.games.db.pooled(game)
        replay = game != today
        turns = await self.games.play(game, answer, boards, replay)
        blind = await self.games.blind(game, answer, replay) if boards else None
        if not replay and not locked:
            self.games.db.save_play(guild_id, game, turns, len(boards))
        return game, turns, answer, len(boards), blind, locked

    @group.command(name='play', description="Today's Wordle result, with the guesses in spoilers")
    @app_commands.describe(game='An earlier game number to replay. Defaults to today.')
    async def play(self, interaction: discord.Interaction, game: int = None):
        """The result with each guess, the words it was picked over and the
        answer in spoilers, and what it would have scored with no boards.
        Once more boards have come in than the locked result used, that
        result is given too, as the official one."""
        await interaction.response.defer(thinking=True)
        found = await self.result(interaction.guild.id, game=game)
        if isinstance(found, str):
            # The reply started out public, so swap it for one only they see.
            await interaction.delete_original_response()
            await interaction.followup.send(found, ephemeral=True)
            return
        game, turns, answer, boards, blind, locked = found
        notes = []
        if blind:
            notes.append(blind_note(blind))
        if locked and boards > locked[1]:
            notes.append(official_note(*locked))
        lines = [headline(game, turns), spoilers(turns, answer, boards)]
        if notes:
            lines.append(' '.join(notes))
        await interaction.followup.send('\n'.join(lines))
        log.info('Wordle: /wordle play by %s in %s: %s from %s board(s)', interaction.user,
                 interaction.guild.name, headline(game, turns), boards)

    @group.command(name='stats', description="This server's official scores against blind play")
    async def stats(self, interaction: discord.Interaction):
        """The average locked-in score here, and the average of the same games
        played blind from the opener, which shows what the boards are worth."""
        await interaction.response.defer(thinking=True)
        guild = interaction.guild
        official, blind = [], []
        for game, turns in self.games.db.locked_solves(guild.id):
            answer = self.games.db.answer(game)
            if not answer:
                continue
            official.append(guesses_taken(turns))
            blind.append(guesses_taken(await self.games.blind(game, answer)))
        if not official:
            await interaction.followup.send('No locked-in Wordle results here yet.')
            return
        await interaction.followup.send(
            f'**Wordle stats** · {discord.utils.escape_markdown(guild.name)}\n'
            f'Games played: {len(official)}\n'
            f'Official average: {average(official):.2f}\n'
            f'Blind {OPENER.upper()} average: {average(blind):.2f}')
        log.info('Wordle: /wordle stats by %s in %s: %s games, %.2f against %.2f blind',
                 interaction.user, guild.name, len(official), average(official), average(blind))

    @group.command(name='simulate', description='Watch the solver play a word, with no boards')
    @app_commands.describe(word='Any five-letter word Wordle accepts')
    async def simulate(self, interaction: discord.Interaction, word: str):
        """You picked the word, so the guesses are shown plainly."""
        word = word.strip().lower()
        if word not in load_words():
            await interaction.response.send_message(f"`{word}` isn't a word Wordle accepts.",
                                                    ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        turns = await self.games.simulate(word)
        await interaction.followup.send(f'{word.upper()} {tally(turns)}*\n{board(turns)}')
        # The word is left out, in case someone simulates today's answer.
        log.info('Wordle: /wordle simulate by %s in %s: %s*', interaction.user,
                 interaction.guild.name, tally(turns))

    @group.command(name='channel', description='Where locked-in results post')
    @app_commands.describe(channel="Leave empty to post next to the Wordle app's message.")
    @app_commands.default_permissions(manage_guild=True)
    async def channel(self, interaction: discord.Interaction,
                      channel: discord.TextChannel = None):
        """Per-guild, like Krillion's results channel."""
        self.games.db.set_channel(interaction.guild.id, channel.id if channel else None)
        where = channel.mention if channel else "the Wordle app's channel"
        log.info('Guild %s set Wordle channel to %s',
                 interaction.guild.id, channel.id if channel else None)
        await interaction.response.send_message(f'Wordle results will post in {where}.',
                                                ephemeral=True)



def average(scores) -> float:
    """The mean of some scores."""
    return sum(scores) / len(scores)
