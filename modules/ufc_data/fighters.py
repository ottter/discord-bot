"""Gather fighter information 
Any changes to this should generally be made to https://github.com/ottter/ufc_scrapper too"""
from modules.ufc_data.rankings import build_rankings


def ranked_list():
    """"""
    return sorted([*set(build_rankings()[2])])
