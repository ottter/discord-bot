"""Gather fighter information"""
from modules.ufc_data.rankings import build_rankings


def ranked_list():
    """"""
    return sorted([*set(build_rankings()[2])])
