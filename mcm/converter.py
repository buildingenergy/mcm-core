from pprint import pprint
from reader import CSVParser

from val import Optional

BEDES_CSV = '../data/BEDES/V8.4/BEDES_Datamodel-08-20-13.csv'

class CSV2Json(CSVParser):

    def sanitize_fieldnames(self):
        new_fields = []
        for name in self.fieldnames:
            new_fields.append(
                name.strip().lower().replace(' ', '_')
            )
        self.fieldnames = new_fields

    def _parse_enum_entries(self, attr_data):
        return [item for item in attr_data.split(';') if item]

    def _parse_data_type(self, attr_data):
        """Convert to python types for validation."""
        if attr_data == 'boolean':
            return bool
        elif attr_data == 'ENUM':
            return 'enum'
        elif attr_data == 'double':
            return float
        elif attr_data == 'interger':
            return int

    def _parse_attribute_data(self, row):
        """Get the parameters for each attribute described by the row.

        Each row here is expected to define an attribute within a table.

        """
        results = {}
        for item in row:
            attribute_handler = getattr(
                self, '_parse_{0}'.format(item), None
            )

            if attribute_handler:
                attribute_val = attribute_handler(row[item])
                if attribute_val:
                    results[item] = attribute_val
            elif row[item]:
                results[item] = row[item]

        return results

    def convert_to_json(self, ontology_name):
        """Does the business logic of translating our CSV to JSON."""
        self.sanitize_fieldnames()
        self.json = {
            'ontology_name': ontology_name,
            'schema': {
                'tables': {}
            }
        }
        table_name = ''
        table = []

        while 1:
            try:
                row = self.next_as_dict()
                entity = row.get('entity_name')
                attribute = row.get('attribute_name')
                if entity:
                    if not table_name:
                        # This is the first run, we haven't been processing yet
                        table_name = entity
                    if table:
                        self.json['schema']['tables'][table_name] = table
                    # Reset our temp vars because we're storing a new table.
                    table_name = entity
                    table = []

                if attribute:
                    table.append(self._parse_attribute_data(row))

            except StopIteration:
                break

        # To capture the last table we parse.
        self.json['schema']['tables'][table_name] = table

def main():

    #
    ## Converter Testing
    ###

    bedes_f = open(BEDES_CSV, 'rb')
    converter = CSV2Json(bedes_f)

    converter.convert_to_json('bedes')
    pprint(converter.json)
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main()
