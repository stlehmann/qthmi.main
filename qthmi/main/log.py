"""Logging.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-06-11 18:16:58
:last modified by:   Stefan Lehmann
:last modified time: 2018-07-10 15:59:52

"""
from abc import abstractmethod, abstractproperty
from typing import List, Optional, TextIO, cast, Union
import csv
import time
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from .tag import Tag


class _CSVWriter:
    """Helper class for type-annotation."""

    @abstractmethod
    def writerow(self, row: List[str]) -> None:
        pass

    @abstractmethod
    def writerows(self, rows: List[str]) -> None:
        pass

    @abstractproperty
    def dialect(self) -> csv.Dialect:
        pass


class CSVWriter(QObject):
    """Write Tag values in CSV files.

    :type tags: list(Tag)
    :ivar tags: connected Tag objects

    :type dialect: csv.Dialect
    :ivar dialect: Dialect for CSV output

    """

    def __init__(self, parent: QWidget=None, dialect: csv.Dialect=csv.excel()) -> None:
        super().__init__(parent)

        self.tags: List[Tag] = []
        self._file: Optional[TextIO] = None
        self._writer: Optional[_CSVWriter] = None
        self.dialect = dialect

    def open(self, filename: str) -> None:
        """Open file for CSV output."""
        self._file = open(filename, "w")
        self._writer = cast(_CSVWriter, csv.writer(self._file, self.dialect))

        data = ['Timestamp']
        data.extend([tag.name for tag in self.tags])

        self._writer.writerow(data)

    def close(self) -> None:
        """Close file."""
        if self._file is not None:
            self._file.close()

        self._writer = None

    def write_value_to_tag(self) -> None:
        """Write value to tag.

        Dummy method.

        """
        pass

    def read_value_from_tag(self) -> None:
        """Read value from tag.

        Dummy method.

        """
        pass

    def writerow(self) -> None:
        """Write all Tag values in the opened CSV file."""
        if self._writer is None:
            raise IOError("File not open")

        data = [time.time()]
        data.extend([tag.value for tag in self.tags])
        self._writer.writerow([str(x) for x in data])
