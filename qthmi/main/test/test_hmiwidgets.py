import unittest
from qthmi.main.connector import AbstractPLCConnector
from qthmi.main.tag import Tag
from qthmi.main.widgets import HMITextMapper


__author__ = 'Stefan Lehmann'


class AddOneTestConnector(AbstractPLCConnector):
    def __init__(self):
        super(AddOneTestConnector, self).__init__()
        self.keys = (x + 1 for x in range(-1, 10))

    def write_to_plc(self, *args, **kwargs):
        pass

    def read_from_plc(self, *args, **kwargs):
        return next(self.keys)


class HMITextMapper_Test(unittest.TestCase):
    def setUp(self):
        self.connector = AddOneTestConnector()
        self.textmapper = HMITextMapper(self.connector.add_tag(Tag("text", 0)))
        self.textdefinitions = ["Standby", "Text1", "Text2", "Text3"]

        for i, t in enumerate(self.textdefinitions):
            self.textmapper.add_text(i, t)

    def test_number_of_defined_texts_is_four(self):
        self.assertEqual(len(self.textmapper.text_definitions), 4)

    def test_empty_string_if_not_polled(self):
        self.assertEqual(self.textmapper.text, "")

    def test_reading_from_connector(self):
        self.connector.poll()
        self.assertEqual(self.textmapper.text, self.textdefinitions[0])

    def test_all_key_value_pairs(self):
        for t in self.textdefinitions:
            self.connector.poll()
            self.assertEqual(self.textmapper.text, t)

    def test_return_empty_string_for_unknown_key(self):
        for i in range(len(self.textdefinitions)):
            self.connector.poll()

        self.connector.poll()
        self.assertEqual(self.textmapper.text, "")


if __name__ == '__main__':
    unittest.main()