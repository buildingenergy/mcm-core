from matchers import fuzzy_in_set

def default_validator(value, *args):
    """Pass-through validation for strings we don't know about."""
    return value


def float_validator(value, *args):
    try:
        value = float(value)
    except ValueError:
        return None
    return value


def enum_validator(value, choices, *args):
    return fuzzy_in_set(value, choices) or None


def boolean_validator(value, *args):
    if isinstance(value, bool):
        return value

    if value.strip().lower() == 'true' or int(x) == 1:
        return True
    else:
        return False

