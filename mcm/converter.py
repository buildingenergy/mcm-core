from pprint import pprint
from reader import CSVParser

from val import And, Convert, Optional, Or, Schema

#BEDES_CSV = '../data/BEDES/V8.4/BEDES_Datamodel-08-20-13.csv'
BEDES_CSV = '../data/BEDES/V8.4/BEDES_REWORKED.csv'

def validate_float(x):
    return float(x)

def validate_enum(x, choices):
    return x in choices

def validate_boolean(x):
    """Example basic boolean validation."""
    if isinstance(x, bool):
        return x

    if x.strip().lower() == 'true' or int(x) == 1:
        return True
    else:
        return False

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

    def convert_to_json(self):
        """Does the business logic of translating our CSV to JSON."""
        self.sanitize_fieldnames()
        table_name = ''
        table = {}

        while 1:
            try:
                row = self.next_as_dict()
                entity = row.get('entity_name')
                attr = row.get(
                    'attribute_name'
                )
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
                    attr = attr.strip().lower().replace(' ', '_')
                    table[attr] = {
                        'type': row.get('data_type'),
                        'description': row.get('description_and_unit'),
                        'priority': row.get('priority'),
                    }

                    entries = row.get('enum_entries')
                    if entries:
                        table[attr]['enum_entries'] = self._parse_enum_entries(
                            entries
                        )

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
