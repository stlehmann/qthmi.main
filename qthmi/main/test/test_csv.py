import csv
import unittest
import sys
import os
from PyQt4.QtCore import SIGNAL, QObject
from PyQt4.QtGui import QWidget, QApplication
import _csv
from qthmi.main.connector import AbstractPLCConnector
from qthmi.main.log import CSVWriter
from qthmi.main.tag import Tag

__author__ = 'Stefan Lehmann'

FILENAME = "test.csv"

class RingBufferTestConnector(AbstractPLCConnector):
    def __init__(self):
        super(RingBufferTestConnector, self).__init__()
        self.ringbuffer = range(100)

    def read_from_plc(self, address, datatype):
        return self.ringbuffer[address]

    def write_to_plc(self, address, value, datatype):
        self.ringbuffer[address] = value


class CSVWriter_Test(unittest.TestCase):

    def setUp(self):
        self.connector = RingBufferTestConnector()
        self.csvwriter = CSVWriter()

        self.tag1 = self.connector.add_tag(Tag("Tag1", 1))
        self.tag2 = self.connector.add_tag(Tag("Tag2", 2))
        self.tag3 = self.connector.add_tag(Tag("Tag3", 3))

    def tearDown(self):
        if os.path.exists(FILENAME):
            #os.remove(FILENAME)
            pass

    def test_open_file(self):
            self.csvwriter.tags.append(self.tag1)
            self.csvwriter.tags.append(self.tag2)
            self.csvwriter.tags.append(self.tag3)

            self.csvwriter.open(FILENAME)
            self.assertIsNotNone(self.csvwriter._writer)
            self.csvwriter.close()

    def test_close_file(self):
        self.csvwriter.open(FILENAME)
        self.csvwriter.close()
        self.assertIsNone(self.csvwriter._writer)

    def test_poll_and_write_row(self):
        self.csvwriter.tags.append(self.tag1)
        self.csvwriter.tags.append(self.tag2)
        self.csvwriter.tags.append(self.tag3)

        self.csvwriter.dialect.delimiter = ";"
        self.csvwriter.open(FILENAME)

        self.connector.poll()
        self.csvwriter.writerow()

        self.csvwriter.close()

    def test_raise_ioerror_writing_in_closed_file(self):
        self.csvwriter.tags.append(self.tag1)
        self.assertRaises(IOError, self.csvwriter.writerow)
