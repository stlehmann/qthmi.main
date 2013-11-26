__author__ = 'Stefan Lehmann'

import unittest
from qthmi.main.connector import AbstractPLCConnector, BufferConnector
from qthmi.main.tag import Tag, TextTag


class RingBufferTestConnector(AbstractPLCConnector):
    def __init__(self):
        super(RingBufferTestConnector, self).__init__()
        self.ringbuffer = range(100)

    def read_from_plc(self, address, datatype):
        return self.ringbuffer[address]

    def write_to_plc(self, address, value, datatype):
        self.ringbuffer[address] = value


class AbstractPLCConnector_Test (unittest.TestCase):

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


class BufferConnector_Test(unittest.TestCase):
    def setUp(self):
        self.connector = RingBufferTestConnector()
        self.connector.add_tag(Tag("first tag", 10, 2, int))
        self.connector.add_tag(Tag("second tag", 20, 4, float))
        self.buffer = BufferConnector(self.connector)
        self.buffer.add_tag(Tag("first tag", "first tag"))

    def test_poll_before_parent_poll_raises_None(self):
        self.buffer.poll()
        self.assertIsNone(self.buffer.tags["first tag"].value)

    def test_poll_tag_value_equals_parent_tag_value(self):
        self.connector.poll()
        self.buffer.poll()
        self.assertEqual(self.buffer.tags["first tag"].value, 10)

