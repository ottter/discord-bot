"""/wordle slash commands: play, today, simulate and channel."""
import logging

import discord
from discord import app_commands
from discord.ext import commands

from modules.wordle.games import board, grid, headline, spoilers
from modules.wordle.solver import load_words, solved

log = logging.getLogger('discord.bot')


class WordleCommands(commands.Cog):
    """Slash commands for the Wordle solver."""

    group = app_commands.Group(name='wordle', description='Wordle solver', guild_only=True)

    def __init__(self, bot, games):
        self.bot = bot
        self.games = games

    async def result(self, guild_id, save):
        """(game, turns, answer) for today's game. Unless it's locked in, it's
        played now with whatever boards there are, none needed, and saved as
        provisional if asked. A string if it can't."""
        game = self.games.today(guild_id)
        answer = await self.games.answer(game)
        if not answer:
            return f"Can't look up Wordle {game} right now. Try again in a bit."

        saved = self.games.db.solve(guild_id, game)
        if saved and saved[2]:
            return game, saved[0], answer
        boards = self.games.db.boards(guild_id, game)
        turns = await self.games.play(game, answer, boards)
        if save:
            self.games.db.save_play(guild_id, game, turns, len(boards))
        return game, turns, answer

    @group.command(name='play', description="Play today's Wordle from the boards so far")
    async def play(self, interaction: discord.Interaction):
        """Colors only, so it spoils nothing. Before the result locks in, it
        plays with whatever boards there are; if the day ends without enough
        boards to lock in, the last of these stands."""
        await interaction.response.defer(thinking=True)
        found = await self.result(interaction.guild.id, save=True)
        if isinstance(found, str):
            # The reply started out public, so swap it for one only they see.
            await interaction.delete_original_response()
            await interaction.followup.send(found, ephemeral=True)
            return
        game, turns, _ = found
        await interaction.followup.send(f'{headline(game, turns)}\n{grid(turns)}')

    @group.command(name='today', description="Today's result with the guesses, just for you")
    async def today(self, interaction: discord.Interaction):
        """Only the person asking sees it, and the words are still spoilered."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        found = await self.result(interaction.guild.id, save=False)
        if isinstance(found, str):
            await interaction.followup.send(found, ephemeral=True)
            return
        game, turns, answer = found
        await interaction.followup.send(
            f'{headline(game, turns)}\n{spoilers(turns, answer)}',
            ephemeral=True)

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
        score = len(turns) if solved(turns) else 'X'
        await interaction.followup.send(f'{word.upper()} {score}/6*\n{board(turns)}')

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
