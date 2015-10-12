"""
:copyright: (c) 2014 Building Energy Inc
:license: see LICENSE for more details.
"""
import dateutil
from datetime import datetime, date
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
    """Try to clean value, coerce it into a float.
    Usage:
        float_cleaner('1,123.45')       # 1123.45
        float_cleaner('1,123.45 ?')     # 1123.45
        float_cleaner(50)               # 50.0
        float_cleaner(None)             # None
        float_cleaner(Decimal('30.1'))  # 30.1
        float_cleaner(my_date)          # raises TypeError
    """
    # API breakage if None does not return None
    if value is None:
        return None
    if isinstance(value, basestring):
        value = PUNCT_REGEX.sub('', value)

    try:
        value = float(value)
    except ValueError:
        value = None
    except TypeError:
        message = 'float_cleaner cannot convert {} to float'.format(
            type(value)
        )
        raise TypeError(message)

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


def date_cleaner(value, *args):
    """Try to clean value, coerce it into a python datetime."""
    if not value:
        return None
    if isinstance(value, datetime) or isinstance(value, date):
        return value
    try:
        value = dateutil.parser.parse(value)
    except (TypeError, ValueError):
        return None
    except OverflowError:
        try:
            value = datetime.utcfromtimestamp(float(value))
        except ValueError:
            value = datetime.utcfromtimestamp(float(value) / 1000.0)

    return value


class Cleaner(object):
    """Cleans values for a given ontology."""
    def __init__(self, ontology):
        self.ontology = ontology
        self.schema = self.ontology.get(u'types', {})
        self.float_columns = filter(
            lambda x: self.schema[x] == u'float', self.schema
        )
        self.date_columns = filter(
            lambda x: self.schema[x] == u'date', self.schema
        )

    def clean_value(self, value, column_name):
        """Clean the value, based on characteristics of its column_name."""
        value = default_cleaner(value)
        if column_name in self.float_columns:
            return float_cleaner(value)

        if column_name in self.date_columns:
            return date_cleaner(value)

        return value
