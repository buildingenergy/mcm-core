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
        # raw key. If it finds a match, it returns the raw_column and score.
        previous_mapping('example field', *map_args) ->
            ('field_1', 0.93)
        ``

    :returns dict: {'raw_column': [('dest_column', score)...],...}

    """
    probable_mapping = {}
    thresh = thresh or 0
    for raw in raw_columns:
        result = []
        conf = 0
        # We want previous mappings to be at the top of the list.
        if previous_mapping and callable(previous_mapping):
            args = map_args or []
            mapping = previous_mapping(raw, *args)
            if mapping:
                result, conf = mapping

        # Only enter this flow if we haven't already selected a result.
        if not result and result is not None:
            best_match, conf  = matchers.best_match(
                raw, dest_columns, top_n=1
            )[0]
            if conf > thresh:
                result = best_match
            else:
                result = None
                conf = 0

        probable_mapping[raw] = [result, conf]

    return probable_mapping


def apply_initial_data(model, initial_data):
    """Set any attributes that are passed in as initial data.

    :param model: instance of your state tracking object.
    :param initial_data: dict, keys should line up with attributes on model.
    :rtype: model instance, modified.

    """
    for item in initial_data:
        value = initial_data[item]
        if hasattr(model, item):
            setattr(model, item, value)
        elif (
            hasattr(model, 'extra_data') and isinstance(model.extra_data, dict)
        ):
            model.extra_data[item] = value

    return model


def map_row(row, mapping, model_class, cleaner=None, *args, **kwargs):
    """Apply mapping of row data to model.

    :param row: dict, parsed row data from csv.
    :param mapping: dict, keys map row columns to model_class attrs.
    :param model_class: class, reference to model class we map against.
    :param cleaner: (optional) inst, cleaner instance for row values.
    :rtype: model_inst, with mapped data attributes; ready to save.

    """
    initial_data = kwargs.get('initial_data', None)
    model = model_class()
    # If there are any initial states we need to set prior to mapping.
    if initial_data:
        model = apply_initial_data(model, initial_data)

    # In case we need to look up cleaner by dynamic field mapping.
    for item in row:
        column_name = item
        if cleaner:
            if item not in (cleaner.float_columns or cleaner.date_columns):
                # Try using a reverse mapping for dynamic maps;
                # default to row name if it's not mapped
                column_name = mapping.get(item, column_name)

            cleaned_value = cleaner.clean_value(row[item], column_name)
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

