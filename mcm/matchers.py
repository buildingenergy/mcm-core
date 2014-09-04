"""
:copyright: (c) 2014 Building Energy Inc
:license: see LICENSE for more details.
"""
from fuzzywuzzy import fuzz


def best_match(s, categories, top_n=5):
    """Return the top N best matches from your categories."""
    scores = []
    for cat in categories:
        scores.append((cat, fuzz.ratio(s.upper(), cat.upper())))

    scores = sorted(scores, key=lambda x: x[1])
    return scores[-top_n:]


def fuzzy_in_set(column_name, ontology, percent_confidence=95):
    """Return True if column_name is in the ontology."""
    match, percent = best_match(
        column_name, ontology, top_n=1
    )[0]

    return percent > percent_confidence
