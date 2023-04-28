"""Gather information about all scheduled upcoming UFC events 
Any changes to this should generally be made to https://github.com/ottter/ufc_scrapper too"""
from bs4 import BeautifulSoup
import requests

HEADERS = {
    'User-Agent': 'goofcon 3'
    }

def build_events_url():
    """Send request to the UFC events page"""
    base_url = "https://www.ufc.com/events"
    return requests.get(base_url, headers = HEADERS)

def build_next_card_url(event):
    """Send request to the event page of upcoming card"""
    base_url = "https://www.ufc.com"
    next_card = gather_all_upcoming_cards()[event]
    return requests.get(base_url + next_card, headers = HEADERS)

def gather_all_upcoming_cards(schedule=False):
    """Return a list of all upcoming cards"""
    upcoming_cards = []
    soup = BeautifulSoup(build_events_url().content, features="html.parser")
    for link in soup.find_all('details', {'id': 'events-list-upcoming'}):
        for href in link.find_all('a', href=True):
            if href.has_attr('href') and href['href'].startswith('/event/') and "#" not in href['href']:
                upcoming_cards.append(href['href'])
    if schedule:
        upcoming_cards = [str(i)
                          .replace( '/event/', '')
                          .replace( '-', ' ')
                          .title()
                          .replace( 'Ufc', 'UFC') for i in upcoming_cards]
        # upcoming_cards = [str(i).replace( '-', ' ').title() for i in upcoming_cards]
    return list(dict.fromkeys(upcoming_cards))

def gather_event_info(next_event=0):
    """ Gather info about a requested upcoming event
    :param int future_event: X events in future to look up, default 0. Max range varies
    """
    main_fighter_list = []
    prelim_fighter_list = []
    if next_event not in range(len(gather_all_upcoming_cards())):
        return "Requested event is not in range of scheduled events"
    soup = BeautifulSoup(build_next_card_url(next_event).content, features="html.parser")
    for x in [[main_fighter_list, 'main-card'], [prelim_fighter_list, 'prelims-card']]:
        # NOTE: Works only for soonest upcoming event. Future events use different format: div class="l-main"
        for matchup in soup.find_all('div', {'id': x[1]}):
            for matchup in matchup.find_all('a', href=True):
                if '/athlete/' in matchup['href']:
                    x[0].append(matchup['href']
                                        .removeprefix('https://www.ufc.com/athlete/')
                                        .replace("-", " ")
                                        .title())
    return list(dict.fromkeys(main_fighter_list)), list(dict.fromkeys(prelim_fighter_list))

def create_fight_matchups(card):
    """ Match the fighters with respective opponent (since scraper gets the fighter names and not matchups)
    :param str card: 
    """
    if len(card) % 2 != 0:
        return "Error: Official website has matchups out of order. Check again later"
    matchups = []
    i = 0
    # Merge list of fights to matchup (0 vs 1, 2 vs 3, etc)
    for fight_count in range(len(card) // 2):
        matchups.append(f"{card[i]} vs {card[i+1]}")
        i = i + 2
    return matchups

def get_event(card='main', display_format='matchups', next_event=0):
    """ User friendly method of gathering info. If I wanted fast I wouldn't use Python
    :param str card:        main or prelim
    :param str format:      fighters or matchups
    :param int next_event:  0 for soonest event. Further out events won't have cards scheduled yet
    """
    which_card = ['main', 'prelim']
    which_format = ['matchups', 'fighters']

    if card not in which_card or display_format not in which_format:
        return "Invalid argument. card='main' or 'prelim'. format='matchups' or 'fighters'"

    get_card = [which_card.index(i) for i in which_card if card in i][0]
    get_format = [which_format.index(i) for i in which_format if display_format in i][0]

    if get_format == 0:
        return create_fight_matchups(gather_event_info(next_event=next_event)[get_card])
    elif get_format == 1:
        return gather_event_info(next_event=next_event)[get_card]