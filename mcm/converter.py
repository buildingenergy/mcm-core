from pprint import pprint
from reader import CSVParser

from val import And, Convert, Optional, Or, Schema

#BEDES_CSV = '../data/BEDES/V8.4/BEDES_Datamodel-08-20-13.csv'
BEDES_CSV = '../data/BEDES/V8.4/BEDES_REWORKED.csv'

class CSV2Json(CSVParser):

    def __init__(self, csvfile, ontology_name):
        super(CSV2Json, self).__init__(csvfile)
        self.json = {
            'ontology_name': ontology_name,
            'schema': {
                'tables': {}
            }
        }

    def sanitize_fieldnames(self):
        new_fields = []
        for name in self.fieldnames:
            new_fields.append(
                name.strip().lower().replace(' ', '_')
            )
        self.fieldnames = new_fields

    def _parse_enum_entries(self, attr_data):
        return [item for item in attr_data.split(';') if item]

    def _parse_data_type(self, attr_data, **kwargs):
        """Convert to validators for given data_type."""
        attr_data = attr_data.strip().lower()
        if attr_data == 'boolean':
            return Or(bool, Convert(lambda x: bool(x)))
        elif attr_data == 'enum':
            return And(
                basestring, lambda x: x in kwargs.get('enum_entries', [])
            )
        elif attr_data == 'double':
            return Or(float, basestring, Convert(lambda x: float(x)))
        elif attr_data == 'interger':
            return Or(int, basestring, Convert(lambda x: int(x)))

        return basestring

    def _parse_validation(self, row):
        """Get the parameters for each attribute described by the row.

        Each row here is expected to define an attribute within a table.

        """
        enum_entries = self._parse_enum_entries(row.get('enum_entries'))

        return self._parse_data_type(
            row.get('data_type'), enum_entries=enum_entries
        )

    def convert_to_json(self):
        """Does the business logic of translating our CSV to JSON."""
        self.sanitize_fieldnames()
        table_name = ''
        table = {}

        while 1:
            try:
                row = self.next_as_dict()
                entity = row.get('entity_name')
                attribute = row.get(
                    'attribute_name'
                ).strip().lower().replace(' ', '_')
                if entity:
                    if not table_name:
                        # This is the first run, we haven't been processing yet
                        table_name = entity
                    if table:
                        self.json['schema']['tables'][table_name] = table
                    # Reset our temp vars because we're storing a new table.
                    table_name = entity
                    table = {}

                if attribute:
                    table[attribute] = {
                        'parameters':  self._parse_validation(row),
                        Optional('description'): row.get(
                            'description_and_unit'
                        ),
                        Optional('priority'): int,
                    }

            except StopIteration:
                break

        # To capture the last table we parse.
        self.json['schema']['tables'][table_name] = table

        return Schema(self.json)


def main():

    #
    ## Converter Testing
    ###

    bedes_f = open(BEDES_CSV, 'rb')
    converter = CSV2Json(bedes_f, 'bedes')

    converter.convert_to_json()
    pprint(converter.json)


if __name__ == '__main__':
    main()
