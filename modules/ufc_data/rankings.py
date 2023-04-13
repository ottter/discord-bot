"""Gather rankings information. 
Any changes to this should generally be made to https://github.com/ottter/ufc_scrapper too"""
from bs4 import BeautifulSoup
import requests
import re

HEADERS = {
    'User-Agent': 'goofcon 3'
    }

WEIGHTCLASS_ALIAS = {
    "Men's Pound-for-Pound Top Rank": ["pfp", "p4p", "overall"],
    "Flyweight": ["fly", "flyweight"],
    "Bantamweight": ["bw", "bantam", "bantamweight"],
    "Featherweight": ["feather", "featherweight"],
    "Lightweight": ["lw", "light", "lightweight"],
    "Welterweight": ["ww", "welter", "welterweight"],
    "Middleweight": ["mw", "middle", "middleweight"],
    "Light Heavyweight": ["lhw"],
    "Heavyweight": ["hw", "heavy", "heavyweight"],
    "Women's Pound-for-Pound Top Rank": ["wpfp", "wp4p"],
    "Women's Strawweight": ["sw", "wsw"],
    "Women's Flyweight": ["wfly"],
    "Women's Bantamweight": ["wbw"],
    "Women's Featherweight": ["wfeather"],
}

def build_ranking_url():
    """Send request to the UFC events page"""
    base_url = "https://www.ufc.com/rankings"
    return requests.get(base_url, headers = HEADERS)

def gather_champions(mark_champion=False):
    champions = []
    is_champion = ''
    soup = BeautifulSoup(build_ranking_url().content, features="html.parser")
    for grouping in soup.find_all('div', {'class': 'rankings--athlete--champion'}):
        for group in grouping.find_all('h5'):
            if mark_champion:
                is_champion = " (Champion)"
            champions.append(group.text + is_champion)
    return champions

def build_rankings(mark_champion=False, numerate_fighters=False):
    weightclass = []
    fighter_rank = []
    is_numerate = ''
    soup = BeautifulSoup(build_ranking_url().content, features="html.parser")
    for grouping in soup.find_all('div', {'class': 'view-athlete-rankings'}):
        # Create the weightclass list
        for group in grouping.find_all('div', {'class': 'view-grouping-header'}):
            weightclass.append(group.text)
        # Create the fighter list
        for group in grouping.find_all('td', {'class': 'views-field-title'}):
            fighter_rank.append(group.text)

    # 'i' and 'k' are for weight classes. 'j' is for list of fighters
    i, j, k = 0, 0, 0
    rankings_dict = {}
    for x in range(len(fighter_rank) // 15):
        # sublist is meant to be emptied after each 15 are iterated through
        sublist = []
        for y in range(15):
            if numerate_fighters:
                is_numerate = f"{y+1} - "
            # loop that creates a list of 15 and adds it to matching weightclass
            sublist.append(is_numerate + fighter_rank[k])
            k = k + 1
        sublist.insert(0, gather_champions(mark_champion)[j])
        # Update the dictionary with the list of ranked fighters
        rankings_dict[weightclass[j]] = sublist
        # Iterate through list by +15 (fighters) and +1 (classes)
        i = i + 15
        j = j + 1

    return weightclass, rankings_dict, fighter_rank

def weightclass_rankings(weightclass='pfp', mark_champion=False, numerate_fighters=False):
    if weightclass == 'ranklist':
        return build_rankings()[0]
    if weightclass == 'all':
        return build_rankings(mark_champion=mark_champion, numerate_fighters=numerate_fighters)[1]
    for key, value in WEIGHTCLASS_ALIAS.items():
        if weightclass.lower() in value:
            # Returning "key" to be used to label the data, the official name for weightclass
            return build_rankings(mark_champion=mark_champion, numerate_fighters=numerate_fighters)[1][key], key
