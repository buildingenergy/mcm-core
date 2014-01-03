import json

from cleaners import default_cleaner, utils


class MappingError(Exception):
    pass


def get_model_inst(model_class, row):
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

    return model_class.objects.get_or_create(
        year_ending=year_ending, property_id=int(property_id)
    )


def map_row(row, mapping, model_class, cleaner=None):
    """Apply mapping of row data to model.

    :param row: dict, parsed row data from csv.
    :param mapping: dict, keys map row columns to model_class attrs.
    :param model_class: class, reference to model class we map against.
    :param cleaner: (optional) inst, cleaner instance for row values.
    :rtype: model_inst, with mapped data attributes; ready to save.

    """
    model, created = get_model_inst(model_class, row)
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

