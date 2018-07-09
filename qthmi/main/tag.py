"""Tag module.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-06-11 18:16:58
:last modified by:   Stefan Lehmann
:last modified time: 2018-07-09 17:02:19

"""
from typing import Any, Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal


RAW_VALUE_TYPE = Any


class Tag(QObject, object):
    """
    An instance of Tag represents a buffered connection between GUI and PLC.

    :type name: str
    :ivar name: tag name

    :ivar address: PLC memory address

    :type datatype: type
    :ivar datatype: python datatype

    :type dirty: bool
    :ivar dirty: is set if the tag value has been changed

    :ivar plc_datatype: identifier for the datatype the data is stored in the
                        PLC

    :ivar raw_value: the raw PLC value

    """

    value_changed = pyqtSignal()

    def __init__(
        self, name: str, address: int, plc_datatype: int = None, datatype: type = float
    ) -> None:
        super(Tag, self).__init__()
        self.name = name
        self.address = address
        self.datatype = datatype
        self.dirty = False
        self.plc_datatype = plc_datatype
        self._raw_value: Any = None

    @property
    def value(self) -> Any:
        """Return value.

        If value is set the new value will be transferred to the PLC the next
        time the C{poll()} function of the C{BufferedPLCConnector} object is
        called.

        """
        if self.raw_value is None:
            return

        return self.datatype(self._raw_value)

    @value.setter
    def value(self, value: Any) -> None:
        self._raw_value = value
        self.dirty = True

    @property
    def raw_value(self) -> Any:
        """Return the raw PLC value."""
        return self._raw_value

    @raw_value.setter
    def raw_value(self, value: Any) -> None:
        self._raw_value = value
        self.value_changed.emit()


class ScaledTag(Tag):
    """Tag that supplies a converted, scaled and offset value.

        >>> tag = ScaledTag("scaled_tag", 0)
        >>> tag.scale_factor = 2
        >>> tag.scale_offset = 5
        >>> tag._raw_value = 10
        >>> tag.value
        25.0

    :type scale: numeric value
    :ivar scale: factor for scaling the raw_value

    :type offset: numeric value
    :ivar offset: offset added to the raw_value

    """

    def __init__(
        self, name: str, address: int, plc_datatype: int = None, datatype: type = float
    ) -> None:
        super(ScaledTag, self).__init__(name, address, plc_datatype, datatype)
        self.scale_factor = 1
        self.scale_offset = 0

    @property
    def value(self) -> Optional[float]:
        """Return converted, scaled and offset value for use in GUI.

        If value is set the new value will be transferred to the PLC the
        next time the C{poll()} function of the C{BufferedPLCConnector}
        object is called.

        """
        if self._raw_value is not None:
            value = self._raw_value * self.scale_factor + self.scale_offset
            value = self.datatype(value)
        else:
            value = None

        return value

    @value.setter
    def value(self, value: float) -> None:
        self._raw_value = (value - self.scale_offset) / self.scale_factor
        self.dirty = True


class TextTag(Tag):
    """Tag that supplies defined texts constraint to integer values."""

    def __init__(self, name: str, address: int, plc_datatype: int=None) -> None:
        super(TextTag, self).__init__(name, address, plc_datatype)
        self.datatype = int
        self.text_definitions: Dict[int, str] = {}
        self.text = ""

    def add_text(self, key: int, text: str) -> None:
        """Add a text message definition.

        :param key: Tag value as key

        :type text: basestring
        :param text: text message

        """
        self.text_definitions[key] = text

    def pop_text(self, key: int) -> str:
        """Remove text message for the given key.

        :param key: Tag value as key
        :return: text message
        """
        return self.text_definitions.pop(key)

    def get_text(self, key: int) -> str:
        """Return text for the given key."""
        text = self.text_definitions.get(key)
        if text is None:
            text = ""
        return text

    @property
    def value(self) -> str:
        """Return the current text value."""
        return self.get_text(self.raw_value)

    @value.setter  # just a dummy setter to avoid mypy error
    def value(self, value: str) -> None:
        pass
