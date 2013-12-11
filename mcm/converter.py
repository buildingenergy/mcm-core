from pprint import pprint
from reader import CSVParser

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
        if attr_data == 'boolean':
            return bool
        elif attr_data == 'ENUM':
            return 'enum'
        elif attr_data == 'double':
            return 0.0
        elif attr_data == 'interger':
            return 0

    def _parse_attribute_data(self, row):
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

    def _parse_row_data(self, table_name, table):
        """NB: presupposes entity or attribute def on a line."""
        self.sanitize_fieldnames()
        row = self.next_as_dict()
        entity = row.get('entity_name')
        attribute = row.get('attribute_name')
        if entity:
            if not table_name:
                table_name = entity
            if table:
                self.json['schema']['tables'][table_name] = table
            table_name = entity
            table = []

        if attribute:
            table.append(self._parse_attribute_data(row))

    def convert_to_json(self, ontology_name):
        """Does the business logic of translating our CSV to JSON."""
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
                self._parse_row_data(table_name, table)
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


if __name__ == '__main__':
    main()
