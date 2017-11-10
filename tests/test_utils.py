from mock import patch, mock_open, MagicMock
from random import choice
from unittest import TestCase
from yaml import dump, load

from bgkube.errors import RequiredOptionError
from bgkube.utils import require, read_vars, replace_vars, timestamp
from tests.__mocks__ import get_options, get_values, get_lines


class TestUtils(TestCase):
    def test_utils_require_returns_named_attribute(self):
        obj = get_options()
        key = choice(list(obj.keys()))

        self.assertEqual(require(obj, key), getattr(obj, key))

    def test_utils_require_raises_error_when_attribute_missing(self):
        obj = get_options()
        key = choice(list(obj.keys()))
        setattr(obj, key, None)

        self.assertRaises(RequiredOptionError, require, obj, key)

    def test_utils_read_vars_parses_file_values_with_valid_types(self):
        values = get_values()
        open_mock = mock_open(read_data='\n'.join(get_lines(values)))

        with patch('bgkube.utils.open'.format(__name__), open_mock):
            vars_dict = dict(read_vars('some-filename'))
            self.assertEqual(len(values), len(vars_dict))

            for k, v in vars_dict.items():
                expected = values[k]
                if isinstance(expected, str):
                    expected = expected.strip()
                self.assertEqual(v, expected)

    def test_utils_replace_vars_updates_values_from_source_dictionary(self):
        values = {'ABC': 1, 'DEF': 2, 'GHI': 3, 'JKL': 4, 'MNO': 5, }
        config = {
            'a': '$ABC',
            'b': {
                'c': '$DEF',
                'd': 'word-$GHI',
                'e': [{
                    'f': 'words-in-list$JKL',
                    'g': '$MNO'
                }]
            }
        }
        result = load(replace_vars(dump(config), values))
        self.assertEqual(result, {
            'a': 1,
            'b': {
                'c': 2,
                'd': 'word-3',
                'e': [{
                    'f': 'words-in-list4',
                    'g': 5
                }]
            }
        })

    @patch('bgkube.utils.time')
    def test_utils_timestamp_returns_time_int_representation(self, time_mock):
        time = 1510277303.472768
        time_mock.time = MagicMock(return_value=time)

        self.assertEqual(timestamp(), int(time))
