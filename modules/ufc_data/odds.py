"""Gather odds of upcoming matchups
Any changes to this should be made to https://github.com/ottter/ufc_scrapper too"""
from bs4 import BeautifulSoup
from modules.ufc_data.events import build_next_card_url

def gather_odds_matchups(next_event=0, mark_favorite=False):
    """Create list of odds for upcoming event, ordered and unlabeled.
    :param int next_event:      X events in future to look up, default 0. Max range varies
    :param bool mark_favorite:  Choose whether to add betting odds favorite indicator
    """
    main_odds_list = []
    prelim_odds_list = []
    soup = BeautifulSoup(build_next_card_url(next_event).content, features="html.parser")
    for event_fighters in [[main_odds_list, 'main-card'], [prelim_odds_list, 'prelims-card']]:
        # Works only for soonest upcoming event. Future events use different format: div class="l-main"
        for odds_matchup in soup.find_all('div', {'id': event_fighters[1]}):
            for matchup in odds_matchup.find_all('span', {'class': "c-listing-fight__odds-amount"}):
                is_favorite = ''
                if mark_favorite and "-" in matchup.text and len(matchup.text) > 1:
                    is_favorite = "*"
                event_fighters[0].append(matchup.text + is_favorite)
    return main_odds_list, prelim_odds_list

def create_odds_matchups(card='main', next_event=0, mark_favorite=False):
    """Match the fighter's odds with respective opponent
    :param str card:            main or prelim
    :param int next_event:      X events in future to look up, default 0. Max range varies
    :param bool mark_favorite:  Choose whether to add betting odds favorite indicator 
    """
    which_card = ['main', 'prelim']
    get_card = [which_card.index(i) for i in which_card if card in i][0]

    if card not in which_card:
        return "Invalid argument. card= 'main' or 'prelim'"

    card_matchup = gather_odds_matchups(next_event=next_event, 
                                        mark_favorite=mark_favorite)[get_card]

    if len(card_matchup) % 2 != 0:
        return "Error: Official website has matchups out of order. Check again later"
    matchups = []
    i = 0
    for x in range(len(card_matchup) // 2):
        matchups.append(f"{card_matchup[i]} vs {card_matchup[i+1]}")
        i = i + 2
    return matchups
