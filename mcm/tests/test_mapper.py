import copy
from unittest import TestCase

from mcm import cleaners
from mcm import mapper
from mcm.tests.utils import FakeModel


class TestMapper(TestCase):
    # Pre-existing static mapping
    fake_mapping = {
        u'Property Id': u'property_id',
        u'Year Ending': u'year_ending',
        u'heading1': u'heading_1',
        u'heading2': u'heading_2',
    }

    # Columns we get from the user's CSV
    raw_columns = [
        u'Address',
        u'Name',
        u'City',
        u'BBL',
        u'Building ID',
    ]
    # Columns we'll try to create a mapping to dynamically
    dest_columns = [
        u'address_line_1',
        u'name',
        u'city',
        u'tax_lot_id',
        u'custom_id_1'
    ]


    expected = {
        u'Address': [u'address_line_1', 67],
        u'BBL': [u'tax_lot_id', 15],
        u'Building ID': [u'tax_lot_id', 29],
        u'City': [u'city', 100],
        u'Name': [u'name', 100]
    }

    test_cleaning_schema = {'types': {
        'property_id': 'float',
    }}

    test_cleaner = cleaners.Cleaner(test_cleaning_schema)

    def test_map_row(self):
        """Test the mapping between csv values and python objects."""
        fake_row = {
            u'Property Id': u'234235423',
            u'Year Ending': u'2013/03/13',
            u'heading1': u'value1',
            u'heading2': u'value2',
            u'heading3': u'value3'
        }
        fake_model_class = FakeModel

        modified_model = mapper.map_row(
            fake_row, self.fake_mapping, fake_model_class
        )

        expected_extra = {u'heading3': u'value3'}

        self.assertEqual(getattr(modified_model, u'property_id'), u'234235423')
        self.assertEqual(
            getattr(modified_model, u'year_ending'), u'2013/03/13'
        )
        self.assertEqual(getattr(modified_model, u'heading_1'), u'value1')
        self.assertEqual(getattr(modified_model, u'heading_2'), u'value2')
        self.assertTrue(
            isinstance(getattr(modified_model, 'extra_data'), dict)
        )
        self.assertEqual(modified_model.extra_data, expected_extra)

    def test_build_column_mapping(self):
        """Create a useful set of suggestions for mappings."""
        dyn_mapping = mapper.build_column_mapping(
            self.raw_columns, self.dest_columns
        )

        self.assertDictEqual(dyn_mapping, self.expected)

    def test_build_column_mapping_w_callable(self):
        """Callable result at the begining of the list."""
        expected = copy.deepcopy(self.expected)
        # This should be the result of our "previous_mapping" call.
        expected[u'Building ID'] = [u'custom_id_1', 27]

        # Here we pretend that we're doing a query and returning
        # relevant results.
        def get_mapping(raw, *args, **kwargs):
            if raw == u'Building ID':
                return [u'custom_id_1', 27]

        dyn_mapping = mapper.build_column_mapping(
            self.raw_columns,
            self.dest_columns,
            previous_mapping=get_mapping,
        )

        self.assertDictEqual(dyn_mapping, expected)

    def test_build_column_mapping_w_null_saved(self):
        """We handle explicit saves of null, and return those dutifully."""
        expected = copy.deepcopy(self.expected)
        # This should be the result of our "previous_mapping" call.
        expected[u'Building ID'] = [None, 1]

        # Here we pretend that we're doing a query and returning
        # relevant results.
        def get_mapping(raw, *args, **kwargs):
            if raw == u'Building ID':
                return [None, 1]

        dyn_mapping = mapper.build_column_mapping(
            self.raw_columns,
            self.dest_columns,
            previous_mapping=get_mapping,
        )

        self.assertDictEqual(dyn_mapping, expected)

    def test_build_column_mapping_w_no_match(self):
        """We return None if there's no good match."""
        expected = copy.deepcopy(self.expected)
        # This should be the result of our "previous_mapping" call.
        null_result = [None, 0]
        expected[u'BBL'] = null_result

        dyn_mapping = mapper.build_column_mapping(
            self.raw_columns,
            self.dest_columns,
            thresh=28
        )

        self.assertDictEqual(dyn_mapping, expected)


    def test_map_row_dynamic_mapping_with_cleaner(self):
        """Run type-based cleaners on dynamic fields based on reverse-mapping"""
        dyn_mapping = mapper.build_column_mapping(
            self.raw_columns, self.dest_columns
        )
        fake_row = {
            u'Property Id': u'234,235,423',
            u'heading1': u'value1',
        }
        fake_model_class = FakeModel

        modified_model = mapper.map_row(
            fake_row,
            self.fake_mapping,
            fake_model_class,
            cleaner=self.test_cleaner
        )

        self.assertEqual(modified_model.property_id, 234235423.0)

    def test_map_row_handle_unmapped_columns(self):
        """No KeyError when we check mappings for our column."""
        test_mapping = copy.deepcopy(self.fake_mapping)
        del(test_mapping[u'Property Id'])
        fake_row = {
            u'Property Id': u'234,235,423',
            u'heading1': u'value1',
        }
        fake_model_class = FakeModel
        modified_model = mapper.map_row(
            fake_row,
            test_mapping,
            fake_model_class,
            cleaner=self.test_cleaner
        )

        self.assertEqual(getattr(modified_model, 'property_id', None), None)
        self.assertEqual(getattr(modified_model, 'heading_1'), u'value1')

    def test_map_row_w_initial_data(self):
        """Make sure that we apply initial data before mapping."""
        test_mapping = copy.deepcopy(self.fake_mapping)
        initial_data = {'property_name': 'Example'}
        fake_row = {
            u'Property Id': u'234,235,423',
            u'heading1': u'value1',
        }
        fake_model_class = FakeModel
        modified_model = mapper.map_row(
            fake_row,
            test_mapping,
            fake_model_class,
            cleaner=self.test_cleaner,
            initial_data=initial_data
        )

        # Our data is set by initial_data
        self.assertEqual(
            getattr(modified_model, 'property_name', None), 'Example'
        )
        # Even though we have no explicit mapping for it.
        self.assertTrue('property_name' not in test_mapping)

