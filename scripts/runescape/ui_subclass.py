"""Runescape items Embed UI"""
import discord
import requests
from discord.ui import Button, View
from discord import ButtonStyle, Embed

from config import timestamp as TIME


def import_item(game, item):
    """Contact API to gather item information"""
    base_url = f"https://api.weirdgloop.org/exchange/history/{game}/latest?name={item}"
    headers = {
        # Owners of API request for a custom user-agent
        'User-Agent': 'github/ottter-discord-bot' }
    response = requests.get(url=base_url, headers=headers, timeout=10).json()
    return response

def preselect_embed(item, game):
    game_full = "Old School Runescape" if game == "osrs" else "Runescape 3"
    thumb_url = "https://raw.githubusercontent.com/ottter/discord-bot/main/data/runescape/"
    embed = GrandExchangeEmbed(title=f"{game_full} Grand Exchange",
                               description=f"Search Request: **{item}**\n"
                               "Click on the button or try to refine your search")
    if game == "osrs":
        embed.set_footer(text="OSRS database contains untradeable items. Those buttons won't work")
    embed.set_thumbnail(url=f"{thumb_url}icon-{game}.png")
    return embed

def create_embed(pressed_button, game):
    """Create the embed from the selected item via class:GrandExchangeView"""
    game_url = "oldschool." if game == "osrs" else ''
    game_full = "Old School Runescape" if game == "osrs" else "Runescape 3"
    core_url = f"https://{game_url}runescape.wiki"

    output = import_item(game, pressed_button)
    embed = GrandExchangeEmbed(title=pressed_button,
                               url=f"{core_url}/w/{pressed_button.replace(' ', '_')}",
                               description=pressed_button)
    embed.set_thumbnail(url=f"{core_url}/images/{pressed_button.replace(' ', '_')}.png")
    embed.add_field(name="Price", value='{:,}'.format(output[pressed_button]['price']), inline=True)
    embed.add_field(name="Trade Volume", value=output[pressed_button]['volume'], inline=True)
    embed.set_footer(text=f"{game_full} Grand Exchange")
    return embed

class GrandExchangeEmbed(Embed):
    """Create the GE embed response"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = discord.Color.purple()


class GrandExchangeView(View):
    """View of the GE embed"""
    def __init__(self, message_author, closest_items, game):
        super().__init__(timeout=15)

        self.buttons = []

        for value in closest_items:
            button = Button(label=value, style=ButtonStyle.blurple, custom_id=value)
            self.buttons.append(button)

        for button in self.buttons:
            self.add_item(button)

        self.message_author = message_author
        self.game = game

        for x in range(len(closest_items)):
            self.buttons[x].callback = self.callback

    async def callback(self, interaction: discord.Interaction):
        """Actions to take when button is pressed"""
        pressed_button = interaction.data['custom_id']
        embed = create_embed(pressed_button, self.game)

        print(f"{TIME()}: {interaction.user} pressed the '{pressed_button}' button called by {self.message_author}")

        # Only user to initiated the buttons can activate them
        if interaction.user != self.message_author:
            return

        await interaction.response.edit_message(embed=embed, view=None)
