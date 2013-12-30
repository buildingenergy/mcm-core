from mcm.matchers import fuzzy_in_set


NONE_SYNONYMS = (u'not available', u'n/a')
BOOL_SYNONYMS = (u'true', u'yes', u'y', u'1')


def default_cleaner(value, *args):
    """Pass-through validation for strings we don't know about."""
    if isinstance(value, unicode):
        if fuzzy_in_set(value.lower(), NONE_SYNONYMS):
            return None
    return value


def float_cleaner(value, *args):
    """Try to determine if we're a boolean."""
    try:
        value = float(value)
    except ValueError:
        return None
    return value


def enum_cleaner(value, choices, *args):
    """Do we exist in the set of enum values?"""
    return fuzzy_in_set(value, choices) or None


def boolean_cleaner(value, *args):
    if isinstance(value, bool):
        return value

    if fuzzy_in_set(value.strip().lower(), BOOL_SYNONYMS):
        return True
    else:
        return False
