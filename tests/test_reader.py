from unittest import TestCase, skip

import unicodecsv

from mcm import reader
from mcm.tests import utils


class TestCSVParser(TestCase):
    def setUp(self):
        self.csv_f = open('test_data/test_espm.csv', 'rb')
        self.parser = reader.CSVParser(self.csv_f)

    def tearDown(self):
        self.csv_f.close()

    def test_get_csv_reader(self):
        """Defaults to DictReader."""
        self.assertTrue(
            isinstance(self.parser.csvreader, unicodecsv.DictReader)
        )

    def test_clean_super(self):
       """Make sure we clean out unicode escaped super scripts."""
       expected = u'Testing 2. And 2. And 2'
       test = u'Testing \xb2. And \ufffd. And _'
       self.assertEqual(
            self.parser._clean_super(test),
            expected
        )

       # Test that our replace keyword works
       new_expected = expected.replace('2', '3')
       self.assertEqual(
            self.parser._clean_super(test, replace=u'3'),
            new_expected
        )

    def test_clean_super_scripts(self):
        """Call _clean_super on all fieldnames."""
        escape = u'\xb2'
        # We know we have one of these escapes in our columns...
        self.assertTrue(utils.list_has_substring(
            escape, self.parser.csvreader.unicode_fieldnames
        ))

        self.parser.clean_super_scripts()

        self.assertFalse(utils.list_has_substring(
            escape, self.parser.csvreader.unicode_fieldnames
        ))

