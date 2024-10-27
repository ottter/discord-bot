"""Gather fighter information 
Any changes to this should generally be made to https://github.com/ottter/ufc_scrapper too"""
from scripts.mma.rankings import build_rankings


def ranked_list():
    """Build ranked list"""
    return sorted([*set(build_rankings()[2])])
