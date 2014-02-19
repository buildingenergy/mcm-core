import copy
from unittest import TestCase

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
        u'custom_id_1': [
            (u'City', 27), (u'Building ID', 27), (u'Name', 13)
        ],
        u'city': [
            (u'City', 100), (u'Building ID', 13), (u'BBL', 0)
        ],
        u'tax_lot_id': [
            (u'Building ID', 29), (u'Address', 24), (u'BBL', 15)
        ],
        u'name': [
            (u'Name', 100), (u'Address', 36), (u'Building ID', 13)
        ],
        u'address_line_1': [
            (u'Address', 67), (u'Building ID', 24), (u'Name', 22)
        ]
    }

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

    def test_map_row_missing_required_columns(self):
        """Throw an exception when either required column is missing."""
        # Row is missing `Property Id` and `Year Ending` columns.
        fake_row = {u'heading1': u'value1'}
        fake_model_class = FakeModel
        self.assertRaises(mapper.MappingError, mapper.map_row, *(
            fake_row, self.fake_mapping, fake_model_class,
        ))

    def test_build_column_mapping(self):
        """Create a useful set of suggestions for mappings."""
        dyn_mapping = mapper.build_column_mapping(
            self.raw_columns, self.dest_columns
        )

        self.assertDictEqual(dyn_mapping, self.expected)

    def test_build_column_mapping_w_callable(self):
        """Callable result at the begining of the list."""

        expected = copy.deepcopy(self.expected)
        expected['custom_id_1'] = [
            # This should be the result of our "previous_mapping" call.
            (u'Building ID', 1.0),
            (u'City', 27),
            (u'Building ID', 27),
            (u'Name', 13)
        ]

        # Here we pretend that we're doing a query and returning
        # relevant results.
        def get_mapping(dest, *args, **kwargs):
            if dest == u'custom_id_1':
                return [(u'Building ID', 1.0)]

        dyn_mapping = mapper.build_column_mapping(
            self.raw_columns,
            self.dest_columns,
            previous_mapping=get_mapping,
            map_args=(u'custom_id_1',)
        )

        self.assertDictEqual(dyn_mapping, expected)
