from unittest import TestCase

from mcm import cleaners


class TestCleaners(TestCase):
    def setUp(self):
        self.cleaner = cleaners.Cleaner({
            'flat_schema': {
                u'heading1': u'',
                u'heading2': u'',
                u'heading_data1': u'Some unit',
             }
        })

    def test_default_cleaner(self):
        """Make sure we cleanup 'Not Applicables', etc from row data."""
        for item in [u'N/A', u'Not Available', u'not available']:
            self.assertEqual(
                cleaners.default_cleaner(item),
                None
            )

    def test_float_cleaner(self):
        """Test float cleaner."""
        self.assertEqual(cleaners.float_cleaner(u'0.8'), 0.8)
        self.assertEqual(cleaners.float_cleaner(u'wut'), None)
        self.assertEqual(cleaners.float_cleaner(u''), None)
        self.assertEqual(cleaners.float_cleaner(None), None)

    def test_clean_value(self):
        """Test that the ``Cleaner`` object properly routes cleaning."""
        expected = u'Whatever'
        self.assertEqual(
            self.cleaner.clean_value(u'Whatever', u'heading1'),
            expected
        )
        float_expected = 0.7
        self.assertEqual(
            self.cleaner.clean_value(u'0.7', u'heading_data1'),
            float_expected
        )