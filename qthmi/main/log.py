__author__ = 'Stefan Lehmann'


import csv
import time
from .widgets import HMIObject


class CSVWriter(HMIObject):
    """
    Write Tag values in CSV files.
    :type tags: list(Tag)
    :ivar tags: connected Tag objects

    :type dialect: csv.Dialect
    :ivar dialect: Dialect for CSV output

    """

    def __init__(self, parent=None, dialect=csv.excel()):
        super(CSVWriter, self).__init__(None, parent)

        self.tags = []
        self._file = None
        self._writer = None
        self.dialect = dialect

    def open(self, filename):
        """
        Open file for CSV output.

        """
        self._file = open(filename, "w")
        self._writer = csv.writer(self._file, self.dialect)

        data = ['Timestamp']
        data.extend([tag.name for tag in self.tags])

        self._writer.writerow(data)

    def close(self):
        """
        Close file.

        """
        self._file.close()
        self._writer = None

    def write_value_to_tag(self):
        pass

    def read_value_from_tag(self):
        pass

    def writerow(self):
        """
        Write all Tag values in the opened CSV file.

        """
        if self._writer is None:
            raise IOError("File not open")

        data = [time.time()]
        data.extend([tag.value for tag in self.tags])
        self._writer.writerow(data)
