import requests
import csv
import difflib
from config import timestamp as TIME
from scripts.runescape.ui_subclass import GrandExchangeView, create_embed, preselect_embed


# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs
# https://api.weirdgloop.org/

def grandexchange_builder(author, game, file_path, item):
    """Build the opening embed that user is prompted with with the buttons"""
    closest_items = find_item(item, file_path=file_path)

    print(f"{TIME()}: {author} requests for {game.upper()} [{item}] returned: {closest_items}")
    content, embed, view = None, None, None
    if len(closest_items) == 0:
        content="Try again"
    if len(closest_items) == 1:
        embed = create_embed(closest_items[0], game)
    if len(closest_items) > 1:
        view = GrandExchangeView(author, closest_items, game)
        embed = preselect_embed(item=item, game=game)
    return content, embed, view

def import_item(game, item):
    """
    Contact API to gather item information
    game= 'osrs' or 'rs3'
    item= string that should be the item name
    """
    base_url = f"https://api.weirdgloop.org/exchange/history/{game}/latest?name={item}"
    headers = {
        # Owners of API request for a custom user-agent
        'User-Agent': 'github/ottter-discord-bot' }
    response = requests.get(url=base_url, headers=headers).json()
    return response

def find_item(search_string, file_path='data/runescape/rs3items.tsv', num_matches=4):
    """Read the TSV file and extract the 'name' column"""
    # NOTE: Ill move this to pandas eventually
    item_list = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        item_list = [row['name'] for row in reader]

    # If an exact* match is entered, return that. Else, get closest match
    search_string = search_string.lower().strip(".,-")
    for item in item_list:
        if search_string == item.lower().strip(".,-"):
            return [item]

    # Find the top N closest matches to the search string
    closest_matches = difflib.get_close_matches(search_string, item_list, n=num_matches, cutoff=0.5)
    # Return a list of (up to) num_matches items that closely match the search_string
    return closest_matches

# closest_match = find_item(search_string='shadow of tum')
# print(closest_match)  # Output: "John"