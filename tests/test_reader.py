from unittest import TestCase, skip

import unicodecsv

from mcm import reader

def _list_has_substring(substring, l):
    """Return True if substring occurs in list l."""
    found_substring = False
    for item in l:
        if substring in item:
            found_substring = True
            break

    return found_substring


class FakeModel(object):
    """Used for testing purposes, only."""
    def save(self):
        pass


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
        self.assertTrue(_list_has_substring(
            escape, self.parser.csvreader.unicode_fieldnames
        ))

        self.parser.clean_super_scripts()

        self.assertFalse(_list_has_substring(
            escape, self.parser.csvreader.unicode_fieldnames
        ))

    @skip('We never call sanitize')
    def test_sanitize_fieldnames(self):
        """Trim whitepsace, lowercase, and remove spaces for all column names."""
        pass


class TestMCMParser(TestCase):
    def setUp(self):
        self.csv_f = open('test_data/test_espm.csv', 'rb')
        self.parser = reader.MCMParser(self.csv_f)

    def tearDown(self):
        self.csv_f.close()

    def test_clean_values(self):
        """Make sure we cleanup 'Not Applicables', etc from row data."""
        # The column name isn't used by the default cleaner.
        self.assertEqual(
            self.parser.clean_value(u'Not Available', u''),
            None
        )

    def test_map_row(self):
        """Test the mapping between csv values and python objects."""
        fake_row = {
            'heading1': 'value1', 'heading2': 'value2', 'heading3': 'value3'
        }
        fake_mapping = {
            'heading1': 'heading_1',
            'heading2': 'heading_2',
        }
        fake_model = FakeModel()

        modified_model = self.parser._map_row(
            fake_row, fake_mapping, fake_model
        )

        expected_extra = {'heading3': 'value3'}

        self.assertEqual(getattr(modified_model, 'heading_1'), 'value1')
        self.assertEqual(getattr(modified_model, 'heading_2'), 'value2')
        self.assertTrue(
            isinstance(getattr(modified_model, 'extra_data'), dict)
        )
        self.assertEqual(modified_model.extra_data, expected_extra)


class TestEspmMCMParser(TestCase):
    def setUp(self):
        self.csv_f = open('test_data/test_espm.csv', 'rb')
        self.parser = reader.EspmMCMParser(self.csv_f)

    def tearDown(self):
        self.csv_f.close()

    def test_clean_value_w_floats(self):
        """Make sure we cleanup values that should be floats, too."""
        pass
