from unittest import TestCase

from mcm import mapper
from mcm.tests.utils import FakeModel


class TestMapper(TestCase):

    def setUp(self):
        self.fake_mapping = {
            u'Property Id': u'property_id',
            u'Year Ending': u'year_ending',
            u'heading1': u'heading_1',
            u'heading2': u'heading_2',
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
