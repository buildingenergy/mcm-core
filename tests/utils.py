def list_has_substring(substring, l):
    """Return True if substring occurs in list l."""
    found_substring = False
    for item in l:
        if substring in item:
            found_substring = True
            break

    return found_substring


