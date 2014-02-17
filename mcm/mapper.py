import json

from mcm import matchers, utils
from mcm.cleaners import default_cleaner


class MappingError(Exception):
    pass


def get_model_inst(model_class, row, *args, **kwargs):
    """Return a model instance given a class and some row data.

    **Warning**
    Implementation specific code in this function!

    It relies on ``year_end`` and ``property_id``
    to be an interger field on your model, and assumes that those
    have a meta class that defines them as ``unique_together``

    :param model_class: class, reference to model class in question.
    :param row: dict, parsed dictionary from CSV.
    :rtype: tuple, (model_inst, bool)

    """
    property_id = default_cleaner(row.get('Property Id'))
    year_ending = utils.date_str_to_date(
        default_cleaner(row.get('Year Ending'))
    )
    if not year_ending or not property_id:
        raise MappingError('`Year Ending` or `Property Id` not defined')

    get_or_create_criteria = {
        'year_ending': year_ending,
        'property_id': int(property_id),
    }

    extra_criteria = kwargs.get('extra_criteria')
    if extra_criteria:
        get_or_create_criteria.update(extra_criteria)

    return model_class.objects.get_or_create(**get_or_create_criteria)


def build_column_mapping(
    raw_columns, dest_columns, previous_mapping=None, map_args=None
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
    for dest in dest_columns:
        result = []
        # We want previous mappings to be at the top of the list.
        if previous_mapping and callable(previous_mapping):
            args = map_args or []
            result = previous_mapping(dest, *args) or []

        result.extend(
            sorted(
                matchers.best_match(dest, raw_columns, top_n=3),
                key=lambda x: x[1],
                reverse=True
            )
        )

        probable_mapping[dest] = result

    return probable_mapping


def map_row(row, mapping, model_class, cleaner=None, *args, **kwargs):
    """Apply mapping of row data to model.

    :param row: dict, parsed row data from csv.
    :param mapping: dict, keys map row columns to model_class attrs.
    :param model_class: class, reference to model class we map against.
    :param cleaner: (optional) inst, cleaner instance for row values.
    :rtype: model_inst, with mapped data attributes; ready to save.

    """
    model, created = get_model_inst(model_class, row, *args, **kwargs)
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

