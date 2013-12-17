from fuzzywuzzy import fuzz


def best_match(s, categories, top_n=5):
    """Return the top N best matches from your categories."""
    scores = []
    for cat in categories:
        scores.append((cat, fuzz.token_set_ratio(s, cat)))

    scores = sorted(scores, key=lambda x: x[1])
    return scores[-top_n:]
