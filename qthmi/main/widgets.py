"""Access PLC values via common GUI objects.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-06-11 18:16:58
:last modified by:   Stefan Lehmann
:last modified time: 2018-07-10 08:49:19

"""
from typing import Any, Dict
from PyQt5.QtCore import QEvent, QObject, Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QDialog,
    QLabel,
    QComboBox,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QSpinBox,
    QCheckBox,
    QLineEdit,
)
from PyQt5.QtGui import QPixmap

from .input import NumPad
from .connector import abstractmethod
from .util import string_to_float
from .tag import Tag
from . import resources_rc  # noqa: F401


class HMIObject(QObject):
    """Basic HMI class."""

    def __init__(self, tag: Tag, parent: QWidget = None) -> None:
        super(HMIObject, self).__init__(parent)
        self.tag = tag

    @abstractmethod
    def read_value_from_tag(self) -> None:
        """Read a value from the tag."""
        pass

    @abstractmethod
    def write_value_to_tag(self) -> None:
        """Write a value to the tag."""
        pass


class HMIWidget(HMIObject, QWidget):
    """Basic HMI Widget class."""

    def __init__(self, tag: Tag, parent: QWidget = None) -> None:
        HMIObject.__init__(self, tag, parent)
        QWidget.__init__(self, parent)


class HMISpinBox(QSpinBox, HMIObject):
    """SpinBox for reading and writing a tag value."""

    def __init__(self, tag: Tag, parent: QWidget=None) -> None:
        HMIObject.__init__(self, tag, parent)

        self.lineEdit().installEventFilter(self)
        self.setButtonSymbols(QDoubleSpinBox.NoButtons)

        self.tag.value_changed.connect(self.read_value_from_tag)
        self.valueChanged.connect(self.write_value_to_tag)

    def eventFilter(self, *args: Any, **kwargs: Any) -> bool:
        """Filter MousePressEvent and show num pad."""
        sender = args[0]
        event = args[1]

        if event.type() == QEvent.MouseButtonPress:
            if self.isEnabled() and not self.isReadOnly():
                numpad = NumPad(self, sender.text())
                if numpad.exec_() == QDialog.Accepted:
                    newValue = string_to_float(numpad.outputLineEdit.text())
                    self.setValue(int(newValue))

        return QDoubleSpinBox.eventFilter(self, *args, **kwargs)

    def read_value_from_tag(self) -> None:
        """Read a value from the tag."""
        self.setValue(self.tag.value)

    def write_value_to_tag(self) -> None:
        """Write value to the tag."""
        self.tag.value = self.value()


class HMIDoubleSpinBox(QDoubleSpinBox, HMIObject):
    """DoubleSpinBox for reading and writing a tag value."""

    def __init__(self, tag: Tag, parent: QWidget = None) -> None:
        HMIObject.__init__(self, tag, parent)

        self.lineEdit().installEventFilter(self)
        self.setButtonSymbols(QDoubleSpinBox.NoButtons)

        self.tag.value_changed.connect(self.read_value_from_tag)
        self.valueChanged.connect(self.write_value_to_tag)

    def eventFilter(self, *args: Any, **kwargs: Any) -> bool:
        """Filter MousePressEvent and show num pad."""
        sender = args[0]
        event = args[1]

        if event.type() == QEvent.MouseButtonPress:
            if self.isEnabled() and not self.isReadOnly():
                numpad = NumPad(self, sender.text())
                if numpad.exec_() == QDialog.Accepted:
                    newValue = string_to_float(numpad.outputLineEdit.text())
                    self.setValue(newValue)
                    self.valueChanged.emit(newValue)

        return QDoubleSpinBox.eventFilter(self, *args, **kwargs)

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        self.setValue(self.tag.value)

    def write_value_to_tag(self) -> None:
        """Write value to tag."""
        self.tag.value = self.value()


class HMIComboBox(QComboBox, HMIObject):
    """ComboBox for reading and writing a tag value."""

    def __init__(self, tag: Tag, parent: QWidget = None) -> None:
        HMIObject.__init__(self, tag, parent)

        self.tag.value_changed.connect(self.read_value_from_tag)
        self.currentIndexChanged.connect(self.write_value_to_tag)

        self._index_changed_first_time = True

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        self.setCurrentIndex(self.tag.value)

    def write_value_to_tag(self) -> None:
        """Write value to tag."""
        if not self._index_changed_first_time:
            self.tag.value = self.currentIndex()

        self._index_changed_first_time = False


class HMILabel(QLabel, HMIObject):
    """Label for reading from a tag value."""

    def __init__(
        self, tag: Tag, parent: QWidget = None, format_spec: str = "{:03.3f}"
    ) -> None:
        super(HMILabel, self).__init__(tag, parent)
        self.format_spec = format_spec
        self.tag.value_changed.connect(self.read_value_from_tag)

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        if self.tag is not None:
            value = self.tag.value
            self.setText(self.format_spec.format(value))


class HMILineEdit(QLineEdit, HMIObject):
    """LineEdit for reading and writing a tag value."""

    def __init__(self, tag: Tag, parent: QWidget=None) -> None:
        super(HMILineEdit, self).__init__(tag, parent)

        self.tag.value_changed.connect(self.read_value_from_tag)
        self.textEdited.connect(self.write_value_to_tag)

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        if self.tag is not None:
            self.setText(self.tag.value)

    def write_value_to_tag(self) -> None:
        """Write value to tag."""
        if self.tag is not None:
            self.tag.value = self.text()


class HMIPushButton(QPushButton, HMIObject):
    """PushButton for reading and writing a tag value."""

    def __init__(self, tag: Tag, parent: QWidget=None) -> None:
        super(HMIPushButton, self).__init__(tag, parent)

        QPushButton.setCheckable(self, True)

        self.tag.value_changed.connect(self.read_value_from_tag)
        self.toggled.connect(self.write_value_to_tag)

        self._checkable = False
        self._next_time_uncheck = False

    def setCheckable(self, value: bool) -> None:
        """Set the objects checkable state."""
        self._checkable = value

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        if self._checkable:
            self.setChecked(self.tag.value)
        else:
            if self.tag.value:
                self.setChecked(False)

    def write_value_to_tag(self) -> None:
        """Write value to tag."""
        self.tag.value = self.isChecked()


class HMITextMapper(HMIObject):
    """
    Map text messages to keys.

    :type text_definitions: dict
    :ivar text_definitions: defined pairs of numeric values and text messages

    :type text: basestring
    :ivar text: Corresponding text message to the current tag value. Empty if
                no text for the given key is defined.

    """

    def __init__(self, tag: Tag, parent: QWidget=None) -> None:
        super(HMITextMapper, self).__init__(tag, parent)
        self.text_definitions: Dict[Any, str] = {}
        self.text = ""
        self.tag.value_changed.connect(self.read_value_from_tag)

    def add_text(self, key: Any, text: str) -> None:
        """Add a text message definition.

        :param key: Tag value as key
        :param text: text message

        """
        self.text_definitions[key] = text

    def pop_text(self, key: Any) -> str:
        """Remove text message for the given key.

        :param key: Tag value as key
        :return: text message
        """
        return self.text_definitions.pop(key)

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        text = self.text_definitions.get(self.tag.value)
        if text is None:
            self.text = ""
            return
        self.text = text


class HMIIndicator(QWidget, HMIObject):
    """Indicator light to display state of a bool tag."""

    def __init__(self, tag: Tag, parent: QWidget=None) -> None:
        HMIObject.__init__(self, tag, parent)
        self.tag.value_changed.connect(self.read_value_from_tag)

        # Indicator images
        # ----------------------------------------------------
        self.indicator_on = QPixmap(":/img/circle_green.png")
        self.indicator_off = QPixmap(":/img/circle_grey.png")

        # Text label
        # ----------------------------------------------------
        self.text_label = QLabel(tag.name)
        font = self.text_label.font()
        font.setPointSize(12)
        self.text_label.setFont(font)

        # Indicator label
        # ----------------------------------------------------
        self.indicator_label = QLabel()
        self.indicator_label.setScaledContents(True)
        self.indicator_label.setFixedSize(22, 22)
        self.indicator_label.setPixmap(self.indicator_off)

        # Layout
        # ----------------------------------------------------
        layout = QHBoxLayout()
        layout.addWidget(self.indicator_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        if self.tag.value:
            self.indicator_label.setPixmap(self.indicator_on)
        else:
            self.indicator_label.setPixmap(self.indicator_off)

    def setText(self, text: str) -> None:
        """Set label text."""
        self.text_label.setText(text)


class HMICheckBox(QCheckBox, HMIObject):
    """Checkbox for displaying and switching a boolean tag."""

    def __init__(self, tag: Tag, parent: QWidget=None) -> None:
        super(HMICheckBox, self).__init__(tag, parent)
        self.tag.value_changed.connect(self.read_value_from_tag)
        self.stateChanged.connect(self.write_value_to_tag)

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        self.setCheckState(Qt.Checked if self.tag.value else Qt.Unchecked)

    def write_value_to_tag(self) -> None:
        """Write value to tag."""
        self.tag.value = self.isChecked()
