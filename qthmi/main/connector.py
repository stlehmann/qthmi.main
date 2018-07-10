"""Abstract class for PLC connection.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-06-11 18:16:58
:last modified by:   Stefan Lehmann
:last modified time: 2018-07-10 08:31:59

"""
from typing import Callable, Any, Dict, Iterable
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from .tag import Tag


class ConnectionError(Exception):
    """Error class for connection errors."""

    pass


def abstractmethod(method: Callable) -> Callable:
    """Make a function an abstact method.

    Decorator

    """
    def default_abstract_method(*args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError('call to abstract method ' + repr(method))

    default_abstract_method.__name__ = method.__name__

    return default_abstract_method


class AbstractPLCConnector(QObject, object):
    """Connector with buffered PLC access.

    The access is not done directly via PLC addresses but instead with Tags. Data is
    exchanged with the PLC when the C{poll()} function is called or C{autopoll} is
    enabled.

    :type tags: dict
    :ivar tags: holds the Tag objects, the key is the tag name

    :type poll_interval: int
    :ivar poll_interval: interval for auto-polling in ms
    """

    polled = pyqtSignal()
    connectionError = pyqtSignal(str)

    def __init__(self) -> None:
        super(AbstractPLCConnector, self).__init__()
        self.tags: Dict[str, Tag] = dict()
        self.autopoll_timer = QTimer(self)
        self.autopoll_timer.timeout.connect(self.poll)

    def add_tag(self, tag: Tag) -> Tag:
        """Add a Tag to the list."""
        self.tags[tag.name] = tag
        return tag

    def add_tags(self, tags: Iterable) -> None:
        """Add multiple tags to the internal list."""
        list(map(self.add_tag, tags))

    @property
    def cycletime(self) -> int:
        """Return current cycletime."""
        return self.autopoll_timer.interval()

    def remove_tag(self, tag_name: str) -> None:
        """Remove a Tag from the list."""
        self.tags.pop(tag_name)

    def poll(self) -> None:
        """Exchange data with PLC.

        If a Tag value has been modified in the GUI the value is first written
        to the PLC and then read again.

        The pyqtSignal C{polled()} is emitted when finished.

        """
        for tag in self.tags.values():
            try:
                if tag.dirty:
                    self.write_to_plc(tag.address, tag.raw_value,
                                      tag.plc_datatype)
                    tag.dirty = False

                tag.raw_value = self.read_from_plc(tag.address,
                                                   tag.plc_datatype)

            except ConnectionError as e:
                self.connectionError.emit(str(e))

        self.polled.emit()

    @abstractmethod
    def write_to_plc(self, *args: Any, **kwargs: Any) -> None:
        """Write data to the plc.

        B{Abstract method. Overwrite when inherited.}

        """
        pass

    @abstractmethod
    def read_from_plc(self, *args: Any, **kwargs: Any) -> None:
        """Read data from the plc.

        B{Abstract method. Overwrite when inherited.}

        """
        pass

    def start_autopoll(self, poll_interval: int) -> None:
        """Enable auto-polling data.

        :param poll_interval: interval for autopolling in ms

        """
        self.autopoll_timer.start(poll_interval)

    def stop_autopoll(self) -> None:
        """Disable auto-polling data."""
        self.autopoll_timer.stop()


class BufferConnector(AbstractPLCConnector):
    """Connect to other Connectors.

    Buffer Tag values for Plotting or Logging independently from the poll
    interval of the original Connector. So all processdata can still be
    collected continuously while some HMIWidgets like plotters or loggers are
    only refreshed when asked for.

    :ivar connector: data source

    """

    def __init__(self, connector: AbstractPLCConnector) -> None:
        super(BufferConnector, self).__init__()
        self.connector = connector

    def write_to_plc(self, *args: Any, **kwargs: Any) -> None:
        """Write all data to PLC."""
        super(BufferConnector, self).write_to_plc(*args, **kwargs)

    def read_from_plc(self, address: str, datatype: type) -> None:
        """Read all data from PLC."""
        tag = self.tags[address]
        primarytag = self.connector.tags[str(tag.address)]
        return primarytag.value
