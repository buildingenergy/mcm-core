import json

from mcm import matchers, utils
from mcm.cleaners import default_cleaner


def build_column_mapping(
    raw_columns, dest_columns, previous_mapping=None, map_args=None, thresh=None
    ):
    """Build a probabalistic mapping structure for mapping raw to dest.

    :param raw_columns: list of str. The column names we're trying to map.
    :param dest_columns: list of str. The columns we're mapping to.
    :param previous_mapping: callable. Used to return the previous mapping
        for a given field.

        Example:
        ``
        # The expectation is that our callable always gets passed a
        # dest key. If it finds a match, it returns the raw_column and score.
        previous_mapping('example field', *map_args) ->
            ('Field1', 0.93)
        ``

    :returns dict: {'dest_column': [('raw_column', score)...],...}

    """
    probable_mapping = {}
    thresh = thresh or 0
    for dest in dest_columns:
        result = []
        # We want previous mappings to be at the top of the list.
        if previous_mapping and callable(previous_mapping):
            args = map_args or []
            mapping = previous_mapping(dest, *args)
            if mapping:
                result, conf = mapping
                conf *= 100

        # Only enter this flow if we haven't already selected a result.
        if not result:
            best_match, conf  = matchers.best_match(
                dest, raw_columns, top_n=1
            )[0]
            if conf > thresh:
                result = best_match

        probable_mapping[dest] = [result, conf]

    return probable_mapping


def map_row(row, mapping, model_class, cleaner=None, *args, **kwargs):
    """Apply mapping of row data to model.

    :param row: dict, parsed row data from csv.
    :param mapping: dict, keys map row columns to model_class attrs.
    :param model_class: class, reference to model class we map against.
    :param cleaner: (optional) inst, cleaner instance for row values.
    :rtype: model_inst, with mapped data attributes; ready to save.

    """
    model = model_class()
    for item in row:
        if cleaner:
            cleaned_value = cleaner.clean_value(row[item], item)
        else:
            cleaned_value = default_cleaner(row[item])
        if item in mapping:
            setattr(model, mapping.get(item), cleaned_value)
        elif hasattr(model, 'extra_data'):
            if not isinstance(model.extra_data, dict):
                # sometimes our dict is returned as JSON string.
                # TODO: Need to resolve this upstream with djorm-ext-jsonfield.
                model.extra_data = json.loads(model.extra_data)
            model.extra_data[item] = cleaned_value
        else:
            model.extra_data = {item: cleaned_value}

    return model

