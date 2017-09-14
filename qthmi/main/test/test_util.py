import unittest
from qthmi.main import util


class UtilTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_string_remove_by_index(self):
        s = ''.join(map(str, range(10)))

        self.assertEqual(
            '',
            util.string_remove_by_index(s, 0, 100)
        )

        self.assertEqual(
            '01236789',
            util.string_remove_by_index(s, 4, 2)
        )

    def test_string_insert(self):
        s = ''.join(map(str, range(10)))
        self.assertEqual(
            '01234Hello56789',
            util.string_insert(s, 'Hello', 5)
        )


if __name__ == '__main__':
    unittest.main()
