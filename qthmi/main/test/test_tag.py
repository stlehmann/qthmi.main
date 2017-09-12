from qthmi.main.connector import AbstractPLCConnector
from qthmi.main.tag import TextTag

__author__ = 'Stefan Lehmann'

import unittest


class TextTag_Test(unittest.TestCase):

    class AddOneTestConnector(AbstractPLCConnector):
        def __init__(self):
            super(TextTag_Test.AddOneTestConnector, self).__init__()
            self.keys = (x + 1 for x in range(-1, 10))

        def write_to_plc(self, *args, **kwargs):
            pass

        def read_from_plc(self, *args, **kwargs):
            return next(self.keys)

    def setUp(self):
        self.connector = TextTag_Test.AddOneTestConnector()
        self.texttag = self.connector.add_tag(TextTag("texttag", 0))
        self.textdefinitions = ["Standby", "Text1", "Text2", "Text3"]
        for i, t in enumerate(self.textdefinitions):
            self.texttag.add_text(i, t)

    def test_len_of_defined_texts_is_4(self):
        self.assertEqual(len(self.texttag.text_definitions), 4)

    def test_empty_string_if_not_polled(self):
        self.assertEqual(self.texttag.value, "")

    def test_reading_from_connector(self):
        self.connector.poll()
        self.assertEqual(self.texttag.value, self.textdefinitions[0])

    def test_all_key_value_pairs(self):
        for i, t in enumerate(self.textdefinitions):
            self.connector.poll()
            self.assertEqual(self.texttag.value, t)

    def test_return_empty_string_for_unknown_key(self):
        for i in range(len(self.textdefinitions)):
            self.connector.poll()

        self.connector.poll()
        self.assertEqual(self.texttag.value, "")


if __name__ == '__main__':
    unittest.main()