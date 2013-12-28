import json
from pprint import pprint
import sys

from reader import CSVParser

from val import And, Convert, Optional, Or, Schema

BEDES_CSV = '../data/BEDES/V8.4/BEDES_REWORKED.csv'
ESPM_CSV = '../data/ESPM/ESPM_all_fields.csv'

class EspmCsv2Json(CSVParser):
    def __init__(self, csvfile, ontology_name):
        super(EspmCsv2Json, self).__init__(csvfile)
        # Note here that we don't have tables.
        self.json = {
            'ontology_name': ontology_name,
            'flat_schema': {}
        }

    def convert_to_json(self):
        self.sanitize_fieldnames()
        self.flat_schema = {}
        while 1:
            try:
                row = self.csvreader.next()
                attr = row.get('field_name')
                if attr:
                    # Some hyphens get unicode escaped.
                    if u'\u2013' in attr:
                        attr = attr.replace(u'\u2013', u'-')
                units = row.get('units')
                self.json['flat_schema'][attr] = units

            except StopIteration:
                break

        return self.json


class BedesCsv2Json(CSVParser):

    def __init__(self, csvfile, ontology_name):
        super(BedesCsv2Json, self).__init__(csvfile)
        self.json = {
            'ontology_name': ontology_name,
            'schema': {
                'tables': {}
            },
            'flat_schema': []
        }

    def _parse_enum_entries(self, attr_data):
        return [item.strip() for item in attr_data.split(';') if item]

    def _extract_enums_into_flat_schema(self, enums, table, attr):
        """Pull out the enum values into the flat schema."""
        entry_values = self._parse_enum_entries(entries)
        table[attr_new]['enum_entries'] = entry_values
        # Break out the enums into the flat hierarchy.
        for e in entry_values:
            self.json['flat_schema'].append(
                '{0}: {1}: {2}'.format(table_name, attr, e)
            )

    def _handle_attr(self, table, row):
        attr_new = attr.strip().lower().replace(' ', '_')
        table[attr_new] = {
            'type': row.get('data_type'),
            'description': row.get('description_and_unit'),
            'priority': row.get('priority'),
            'human_readable': attr,
        }
        # Create a flat schema, too for easier comparison
        # to other ontologies
        self.json['flat_schema'].append(
                '{0}: {1}'.format(table_name, attr)
        )

    def convert_to_json(self):
        """Does the business logic of translating our CSV to JSON."""
        self.sanitize_fieldnames()
        table_name = ''
        table = {}

        while 1:
            try:
                row = self.csvreader.next()
                entity = row.get('entity_name')
                attr = row.get('attribute_name')
                if entity:
                    if not table_name:
                        # This is the first run, we haven't been processing yet
                        table_name = entity
                    if table:
                        self.json['schema']['tables'][table_name] = table
                    # Reset our temp vars because we're storing a new table.
                    table_name = entity
                    table = {}

                if attr:
                    self._handle_attr(table, row)
                    entries = row.get('enum_entries')
                    if entries:
                        self._extract_enums_into_flat_schema(entries, table, attr)

            except StopIteration:
                break

        # To capture the last table we parse.
        self.json['schema']['tables'][table_name] = table

        return self.json


def main():

    #
    ## Converter Testing
    ###

    if 'help' in sys.argv:
        print 'run `python convert.py bedes|espm`'
    elif 'bedes' in sys.argv:
        csv_f = open(BEDES_CSV, 'rb')
        converter = BedesCsv2Json(csv_f, 'bedes')
    else:
        csv_f = open(ESPM_CSV, 'rb')
        converter = EspmCsv2Json(csv_f, 'espm')

    converter.convert_to_json()

    print(json.dumps(converter.json))

if __name__ == '__main__':
    main()
