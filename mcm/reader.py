"""
:copyright: (c) 2014 Building Energy Inc
:license: see LICENSE for more details.


The Reader module is intended to contain only code which reads data
out of CSV files. Fuzzy matches, application to data models happens
elsewhere.

"""
import operator
import sys

from unicodecsv import DictReader, Sniffer

from mcm import mapper, utils


class CSVParser(object):
    # Character escape sequences to replace
    CLEAN_SUPER = [u'\ufffd', u'\xb2']

    def __init__(self, csvfile, *args, **kwargs):
        self.csvfile = csvfile
        self.csvreader = self._get_csv_reader(csvfile, **kwargs)

    def _get_csv_reader(self, *args, **kwargs):
        """Guess CSV dialect, and return CSV reader."""
        # Skip the first line, as csv headers are more likely to have weird
        # character distributions than the actual data.
        self.csvfile.readline()

        # Read a significant chunk of the data to improve the odds of
        # determining the dialect.  MCM is often run on very wide csv files.
        dialect = Sniffer().sniff(self.csvfile.read(16384))
        self.csvfile.seek(0)

        if 'reader_type' not in kwargs:
            return DictReader(self.csvfile, errors='replace')

        else:
            reader_type = kwargs.get('reader_type')
            del kwargs['reader_type']
            return reader_type(self.csvfile, dialect, **kwargs)

    def _clean_super(self, col, replace=u'2'):
        """Cleans up various superscript unicode escapes.

        :param col: str, column name as read from the file.
        :param replace: (optional) str, string to replace superscripts with.
        :rtype: str, cleaned row name.

        """
        for item in self.CLEAN_SUPER:
            col = col.replace(item, unicode(replace))

        return col

    def clean_super_scripts(self):
        """Replaces column names with clean ones."""
        new_fields = []
        for col in self.csvreader.unicode_fieldnames:
            new_fields.append(self._clean_super(col))

        self.csvreader.unicode_fieldnames = new_fields

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
        if 'matching_func' not in kwargs:
            # Special note, contains expects argumengs like the following
            # contains(a, b); tests outcome of ``b in a``
            self.matching_func = operator.contains

        else:
            self.matching_func = kwargs.get('matching_func')

    def split_rows(self, chunk_size, callback, *args, **kwargs):
        """Break up the CSV into smaller pieces for parallel processing."""
        row_num = 0
        for batch in utils.batch(self.next(), chunk_size):
            row_num += len(batch)
            callback(batch, *args, **kwargs)

        return row_num

    def map_rows(self, mapping, model_class):
        """Convenience method to call ``mapper.map_row`` on all rows.

        :param mapping: dict, keys map columns to model_class attrs.
        :param model_class: class, reference to model class.

        """
        for row in self.next():
            # Figure out if this is an inser or update.
            # e.g. model.objects.get('some canonical id') or model_class()
            yield mapper.map_row(row, mapping, model_class)


def main():
    """Just some contrived test code."""
    from mcm.mappings import espm
    from mcm.tests.utils import FakeModel

    if len(sys.argv) < 2:
        sys.exit('You need to specify a CSV file path.')

    with open(sys.argv[1], 'rb') as f:
        parser = MCMParser(f)
        mapping = espm.MAP
        model_class = FakeModel
        for m in parser.map_rows(mapping, model_class):
            m.save()


if __name__ == '__main__':
    main()
