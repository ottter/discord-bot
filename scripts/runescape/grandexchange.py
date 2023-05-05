import requests
import csv
import difflib


# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs
# https://api.weirdgloop.org/

def import_item(game, item="santa hat"):
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
    names = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        names = [row['name'] for row in reader]

    # If an exact* match is entered, return that. Else, get closest match
    search_string = search_string.lower().strip(".,-")
    for name in names:
        if search_string == name.lower().strip(".,-"):
            return [name]

    # Find the top N closest matches to the search string
    closest_matches = difflib.get_close_matches(search_string, names, n=num_matches, cutoff=0.5)
    # Return a list of (up to) num_matches items that closely match the search_string
    return closest_matches

# closest_match = find_item(search_string='shadow of tum')
# print(closest_match)  # Output: "John"