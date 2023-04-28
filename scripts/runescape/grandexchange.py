import discord
import requests

# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs
# https://api.weirdgloop.org/

def import_item(game, item):
    """Contact API to gather item information"""
    base_url = f"https://api.weirdgloop.org/exchange/history/{game}/latest?name={item}"
    headers = {
        # Owners of API request for a custom user-agent
        'User-Agent': 'github/ottter-discord-bot' }
    response = requests.get(url=base_url, headers=headers).json()
    return response

def validate_item(output):
    """Check if the requested item is valid"""
    try:
        if output['success'] is False:
            return False
    except KeyError:
        return True

def search_grandexchange(context, game, item, embed=True):
    """Search the GE for requested item and return results to chat"""
    output = import_item(game, item)
    # Example: {'Cannonball': {'id': '2', 'timestamp': '2023-03-19T03:00:45.000Z',
    #                          'price': 160, 'volume': 20665706}}
    item_name = list(output.keys())[0]
    if validate_item(output) is False:
        other_game = 'rs' if game.startswith('os') else 'os'
        return context.send(f'Item not in the {game.upper()} DB. '
                            f'Try `.{other_game}ge` instead or improving search request')
    if not embed:
        return create_text(context, output, item_name)
    embed = create_embed(output, game, item_name)
    return context.send(embed=embed)

def create_text(context, output, item_name):
    """Create the textblock for output, if embed argument is false"""
    price = '{:,}'.format(output[item_name]['price'])
    volume = output[item_name]['volume']
    textblock = f"**{item_name}**\nPrice: {price}\t Volume: {volume}"
    return context.send(textblock)

def create_embed(output, game, item_name):
    """Create the embed that gets returned to Discord. Embed by default"""
    game = "oldschool." if game == "osrs" else ''
    core_url = f"https://{game}runescape.wiki"
    embed=discord.Embed(title=item_name, url=f"{core_url}/w/{item_name.replace(' ', '_')}")
    embed.set_thumbnail(url=f"{core_url}/images/{item_name.replace(' ', '_')}.png")
    embed.add_field(name="price", value='{:,}'.format(output[item_name]['price']), inline=True)
    embed.add_field(name="volume", value=output[item_name]['volume'], inline=True)
    return embed