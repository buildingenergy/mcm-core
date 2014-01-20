import re
import string

from mcm.matchers import fuzzy_in_set


NONE_SYNONYMS = (u'not available', u'not applicable', u'n/a')
BOOL_SYNONYMS = (u'true', u'yes', u'y', u'1')
PUNCT_REGEX = re.compile('[{0}]'.format(
    re.escape(string.punctuation.replace('.', '')))
)


def default_cleaner(value, *args):
    """Pass-through validation for strings we don't know about."""
    if isinstance(value, unicode):
        if fuzzy_in_set(value.lower(), NONE_SYNONYMS):
            return None
    return value


def float_cleaner(value, *args):
    """Try to clean value, coerce it into a float."""
    if not value:
        return None
    try:
        value = PUNCT_REGEX.sub('', value)
        value = float(value)
    except ValueError:

        return None

    return value


def enum_cleaner(value, choices, *args):
    """Do we exist in the set of enum values?"""
    return fuzzy_in_set(value, choices) or None


def bool_cleaner(value, *args):
    if isinstance(value, bool):
        return value

    if fuzzy_in_set(value.strip().lower(), BOOL_SYNONYMS):
        return True
    else:
        return False


class Cleaner(object):
    """Cleans values for a given ontology."""
    def __init__(self, ontology):
        self.ontology = ontology
        self.schema = self.ontology['flat_schema']
        self.float_columns = filter(lambda x: self.schema[x], self.schema)

    def clean_value(self, value, column_name):
        """Clean the value, based on characteristics of its column_name."""
        value = default_cleaner(value)
        if column_name in self.float_columns:
            value = float_cleaner(value)

        return value

