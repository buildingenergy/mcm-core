import csv
import operator

""" The Reader module is intended to contain only code which reads data
out of CSV files. Fuzzy matches, application to data models happens
elsewhere.

NB: This is spike code so far.

"""


class CSVParser(object):
    def __init__(self, csvfile, *args, **kwargs):
        self.csvfile = csvfile
        self.csvreader = self._get_csv_reader(csvfile, **kwargs)
        self.fieldnames = self.get_columns()

    def _get_csv_reader(self, *args, **kwargs):
        """Guess CSV dialect, and return CSV reader."""
        dialect = csv.Sniffer().sniff(self.csvfile.read(1024))
        self.csvfile.seek(0)

        if not 'reader_type' in kwargs:
            return csv.reader(self.csvfile, dialect, **kwargs)

        else:
            reader_type = kwargs.get('reader_type')
            del kwargs['reader_type']
            return reader_type(self.csvfile, dialect, **kwargs)

    def get_columns(self):
        """Return just the column names."""
        self.csvfile.seek(0)
        return self.csvreader.next()

    def next_as_dict(self):
        return dict(zip(self.fieldnames, self.csvreader.next()))


class MCMParser(CSVParser):
    """
    This Parser is a wrapper around CSVReader which matches columnar data
    against a set of known ontologies and separates data according
    to those distinctions.

    Map: mapping the columns to known ontologies, then colating data by these.
    Clean: coerce data according to ontology schema.
    Merge: merging the data from multiple sources into one ontology.

    """
    def __init__(self, csvfile, ontologies, *args, **kwargs):
        super(MCMParser, self).__init__(csvfile, args, kwargs)
        self.ontologies = self._prepare_column_ontologies(ontologies)
        if not 'matching_func' in kwargs:
            # Special note, contains expects argumengs like the following
            # contains(a, b); tests outcome of ``b in a``
            self.matching_func = operator.contains

        else:
            self.matching_func = kwargs.get('matching_func')

    def _prepare_column_ontologies(self, ontologies):
        """Strip, and lowercase each of the column name definitions.

        :param ontologies: dict of iterables containing strings, the names.
        :returns: dict, cleaned up version of column names.

        """
        for ontology in ontologies:
            for item in ontologies[ontology]:
                item = item.strip().lower()

        return ontologies

    def get_columns(self):
        """Return just the column names."""
        self.csvfile.seek(0)
        return self.csvreader.next()

    def match_columns(self, raw_columns, ontology):
        """Return matched and unmatched columns.

        :param raw_columns: iterable of str, the read names.
        :ontology: iterable of str, the column names we match against.
        :returns: tuple of iterables, matching the ones that match this
        ontology, not_matching, the rest of the column names.

        """
        matching = []
        not_matching = []
        for name in raw_columns:
            if self.matching_func(ontology, name):
                matching.append(name)
            else:
                not_matching.append(name)

        return matching, not_matching

    def _get_common_unmatched(self, unmatched):
        """Returns a set of all common unmatched items.

        :param unmatched: dictionary of lists, keys ontologies, values lists.
        :returns: set of names which belong to no ontology.

        """
        return set(unmatched.values()[0]).intersection(*unmatched.values())


    def group_columns_by_ontology(self, raw_columns):
        """Get all of the columns based on the ontology they belong to.

        :param raw_columns: iterable of str, the read values from a file.
        :returns: matched_result, a dict keyed by ontology name whose values
        are the matched column names, common_unmatched are all the columns
        that weren't matched into any ontology.

        """
        matched_result = {}
        unmatched_result = {}
        for ontology in self.ontologies:
            matched, unmatched = self.match_columns(
                raw_columns, self.ontologies[ontology]
            )
            matched_result[ontology] = matched
            unmatched_result[ontology] = unmatched

        common_unmatched = self._get_common_unmatched(unmatched_result)

        return matched_result, common_unmatched


def main():
    """Just some contrived test code."""
    #
    ## Test ontology column names
    ###

    fake_ontology = ('Name', 'Date', 'Location',)
    other_ontology = ('Name', 'Status',)
    ontologies = {'fake': fake_ontology, 'other': other_ontology,}

    f = open('../data/test/database.csv', 'rb')
    parser = MCMParser(f, ontologies)

    columns_raw = parser.get_columns()
    print 'Raw: {0}'.format(columns_raw)

    columns = parser.match_columns(columns_raw, fake_ontology)
    print 'Matched: {0}, and unmatched {1}'.format(columns[0], columns[1])

    print parser.group_columns_by_ontology(columns_raw)


if __name__ == '__main__':
    main()
