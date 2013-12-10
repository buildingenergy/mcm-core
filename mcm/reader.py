import csv
import operator

class MCMParser(object):
    """
    This Parser is a wrapper around CSVReader which matches columnar data
    against a set of known ontologies and separates data according
    to those distinctions.

    """
    def __init__(self, csvfile, ontologies, matching_func=None):
        self.csvfile = csvfile
        self.ontologies = ontologies
        self._get_csv_reader()
        if not matching_func:
            # Special note, contains expects argumengs like the following
            # contains(a, b); tests outcome of ``b in a``
            self.matching_func = operator.contains

    def _get_csv_reader(self):
        """Guess CSV dialect, and return CSV reader."""
        dialect = csv.Sniffer().sniff(self.csvfile.read(1024))
        self.csvfile.seek(0)
        self.csvreader = csv.reader(self.csvfile, dialect)

    def get_columns(self):
        """Return just the column names."""
        self.csvfile.seek(0)
        return self.csvreader.next()

    def match_columns(self, raw_columns, ontology):
        """Return matched and unmatched columns."""
        matching = []
        not_matching = []
        for name in raw_columns:
            if self.matching_func(ontology, name):
                matching.append(name)
            else:
                not_matching.append(name)

        return matching, not_matching

    def _get_common_unmatched(self, unmatched):
        """Here unmatched are dicts of lists."""
        return set(unmatched.values()[0]).intersection(*unmatched.values())


    def group_columns_by_ontology(self, raw_columns):
        """Get all of the columns based on the ontology they belong to."""
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
    """Just some test code."""
    # Test ontology column names
    fake_ontology = ('Name', 'Date', 'Location',)
    other_ontology = ('Name', 'Status',)
    ontologies = {'fake': fake_ontology, 'other': other_ontology,}

    f = open('database.csv', 'rb')
    parser = MCMParser(f, ontologies)

    columns_raw = parser.get_columns()
    print 'Raw: {0}'.format(columns_raw)

    columns = parser.match_columns(columns_raw, fake_ontology)
    print 'Matched: {0}, and unmatched {1}'.format(columns[0], columns[1])

    print parser.group_columns_by_ontology(columns_raw)


if __name__ == '__main__':
    main()
