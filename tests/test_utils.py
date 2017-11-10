from mock import patch, mock_open, MagicMock
from random import choice
from unittest import TestCase
from yaml import dump, load

from bgkube.errors import RequiredOptionError
from bgkube.utils import require, dot_env_dict, read_with_merge_vars, timestamp
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

    def test_utils_dot_env_dict_returns_parsed_file_content_as_dictionary(self):
        values = get_values()
        open_mock = mock_open(read_data='\n'.join(get_lines(values)))

        with patch('bgkube.utils.open'.format(__name__), open_mock):
            vars_dict = dict(dot_env_dict('some-filename'))
            self.assertEqual(len(values), len(vars_dict))

            for k, v in vars_dict.items():
                expected = values[k]

                if isinstance(expected, str):
                    expected = expected.strip()

                self.assertEqual(v, expected)

    def test_utils_read_with_merge_vars_returns_file_content_with_vars_replaced_from_source_dictionary(self):
        merge_vars = {'ABC': 1, 'DEF': 2, 'GHI': 3, 'JKL': 4, 'MNO': 5, }
        open_mock = mock_open(read_data=dump({
            'a': '$ABC',
            'b': {
                'c': '$DEF',
                'd': 'word-$GHI',
                'e': [{
                    'f': 'words-in-list$JKL',
                    'g': '$MNO'
                }]
            }
        }))
        with patch('bgkube.utils.open'.format(__name__), open_mock):
            result = load(read_with_merge_vars('some-filename', merge_vars))
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
