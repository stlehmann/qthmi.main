__author__ = 'Stefan Lehmann'

import unittest
from qthmi.main.connector import AbstractPLCConnector
from qthmi.main.tag import Tag, TextTag


class RingBufferTestConnector(AbstractPLCConnector):
    def __init__(self):
        super(RingBufferTestConnector, self).__init__()
        self.ringbuffer = range(100)

    def read_from_plc(self, address, datatype):
        return self.ringbuffer[address]

    def write_to_plc(self, address, value, datatype):
        self.ringbuffer[address] = value


class PLCConnector_Test (unittest.TestCase):

    def setUp(self):
        self.connector = RingBufferTestConnector()
        self.connector.add_tag(Tag("first tag", 10, 2, int))
        self.connector.add_tag(Tag("second tag", 20, 4, float))

    def test_get_first_tag_by_key(self):
        self.assertIsNotNone(self.connector.tags["first tag"].name)

    def test_get_tag_name(self):
        self.assertEqual(self.connector.tags["first tag"].name, "first tag")

    def test_get_tag_address(self):
        self.assertEqual(self.connector.tags["first tag"].address, 10)

    def test_get_tag_datatype(self):
        self.assertEqual(self.connector.tags["first tag"].datatype, int)

    def test_get_tag_plc_datatype(self):
        self.assertEqual(self.connector.tags["first tag"].plc_datatype, 2)

    def test_change_value_makes_tag_dirty(self):
        self.assertFalse(self.connector.tags["first tag"].dirty)
        self.connector.tags["first tag"].value = 100
        self.assertTrue(self.connector.tags["first tag"].dirty)

    def test_poll_data_from_connector(self):
        self.connector.poll()
        self.assertEqual(self.connector.tags["first tag"].value, 10)
        self.assertEqual(self.connector.tags["second tag"].value, 20)

    def test_write_data_first_when_polling(self):
        self.connector.tags["first tag"].value = 15
        self.connector.poll()
        self.assertEqual(self.connector.tags["first tag"].value, 15)


class TextTag_Test(unittest.TestCase):

    class AddOneTestConnector(AbstractPLCConnector):
        def __init__(self):
            super(TextTag_Test.AddOneTestConnector, self).__init__()
            self.keys = (x + 1 for x in range(-1, 10))

        def write_to_plc(self, *args, **kwargs):
            pass

        def read_from_plc(self, *args, **kwargs):
            return self.keys.next()

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


