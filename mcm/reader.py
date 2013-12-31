import json
import operator
from pprint import pprint
import sys

from unicodecsv import DictReader, Sniffer

from mcm.mappings import espm
from mcm import cleaners, matchers

""" The Reader module is intended to contain only code which reads data
out of CSV files. Fuzzy matches, application to data models happens
elsewhere.

"""

def load_ontology(filename):
    """Load json structure from a file."""
    with open(filename, 'rb') as f:
        return json.loads(f.read())


class CSVParser(object):
    # Character escape sequences to replace
    CLEAN_SUPER = [u'\ufffd', u'\xb2', u'_']

    def __init__(self, csvfile, *args, **kwargs):
        self.csvfile = csvfile
        self.csvreader = self._get_csv_reader(csvfile, **kwargs)

    def _get_csv_reader(self, *args, **kwargs):
        """Guess CSV dialect, and return CSV reader."""
        dialect = Sniffer().sniff(self.csvfile.read(1024))
        self.csvfile.seek(0)

        if not 'reader_type' in kwargs:
            return DictReader(self.csvfile, errors='remove')

        else:
            reader_type = kwargs.get('reader_type')
            del kwargs['reader_type']
            return reader_type(self.csvfile, dialect, **kwargs)

    def _clean_super(self, col, replace=u'2'):
        """Cleans up various superscript unicode escapes."""
        for item in self.CLEAN_SUPER:
            col = col.replace(item, unicode(replace))

        return col

    def clean_super_scripts(self):
        """Replaces column names with clean ones."""
        new_fields = []
        for col in self.csvreader.unicode_fieldnames:
            new_fields.append(self._clean_super(col))

        self.csvreader.unicode_fieldnames = sorted(new_fields)

    def sanitize_fieldnames(self):
        new_fields = []
        for name in self.fieldnames:
            new_fields.append(
                self._clean_super(name).strip().lower().replace(' ', '_')
            )
        self.csvreader.fieldnames = sorted(new_fields)
        self.csvreader.unicode_fieldnames = sorted(
            [unicode(s) for s in new_fields]
        )

    def next(self):
        """Wouldn't it be nice to get iterables form csvreader?"""
        while 1:
            try:
                yield self.csvreader.next()
            except StopIteration:
                break

class MCMParser(CSVParser):
    """
    This Parser is a wrapper around CSVReader which matches columnar data
    against a set of known ontologies and separates data according
    to those distinctions.

    Map: mapping the columns to known ontologies, then colating data by these.
    Clean: coerce data according to ontology schema.
    Merge: merging the data from multiple sources into one ontology.

    """
    def __init__(self, csvfile, *args, **kwargs):
        super(MCMParser, self).__init__(csvfile, args, kwargs)
        self.clean_super_scripts()
        if not 'matching_func' in kwargs:
            # Special note, contains expects argumengs like the following
            # contains(a, b); tests outcome of ``b in a``
            self.matching_func = operator.contains

        else:
            self.matching_func = kwargs.get('matching_func')

    def _get_columns(self):
        """Return just the column names."""
        self.csvfile.seek(0)
        return self.csvreader.next()

    def clean_value(self, value, column_name):
        """Try to convert the value to one matching the column's type."""
        return cleaners.default_cleaner(value)

    def _map_row(self, row, mapping, model):
        """Apply mapping of row data to model."""
        for item in row:
            cleaned_value = self.clean_value(row[item], item)
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

    def map_rows(self, mapping, model_class):
        """Map predefined columns to attributes in a model object."""
        for row in self.next():
            # Figure out if this is an inser or update.
            # e.g. model.objects.get('some canonical id') or model_class()
            yield self._map_row(row, mapping, model_class())


class EspmMCMParser(MCMParser):
    """ESPM-specific flavor."""

    def __init__(self, csvfile, *args, **kwargs):
        super(EspmMCMParser, self).__init__(csvfile, args, kwargs)
        self.schema = load_ontology('../data/espm/espm.json')['flat_schema']
        # Basically anything that has units is a float number.
        self.float_columns = filter(lambda x: self.schema[x], self.schema)

    def clean_value(self, value, column_name):
        # Apply default cleaning, turning it into a None if need be, etc.
        value = super(EspmMCMParser, self).clean_value(value, column_name)
        if column_name in self.float_columns:
            return cleaners.float_cleaner(value)


def main():
    """Just some contrived test code."""
    #
    ## Test ontology column names
    ###
    class FakeModel(object):
        def save(self):
            pass

    if len(sys.argv) < 2:
        sys.exit('You need to specify a CSV file path.')

    with open(sys.argv[1], 'rb') as f:
        parser = EspmMCMParser(f)
        mapping = espm.MAP
        model_class = FakeModel
        #TODO(gavin): currently saving everything as strings
        for m in parser.map_rows(mapping, model_class):
            m.save()

        import ipdb; ipdb.set_trace()

if __name__ == '__main__':
    main()
