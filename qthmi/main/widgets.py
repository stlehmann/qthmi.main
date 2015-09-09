"""
Access PLC values via common GUI objects

"""
from matplotlib.backends.qt4_editor.formlayout import QLineEdit

from PyQt4.QtCore import QEvent, SIGNAL, QObject, Qt
from PyQt4.QtGui import QDoubleSpinBox, QDialog, QLabel, QComboBox, QWidget, \
    QPushButton, QVBoxLayout, QHBoxLayout, QPixmap, QPicture, QSpinBox, \
    QCheckBox

from input import NumPad
from qthmi.main.connector import abstractmethod
from resources_rc import *


class HMIObject(QObject):

    """
    Basic HMI class

    """

    def __init__(self, tag=None, parent=None):
        super(HMIObject, self).__init__(parent)
        self.tag = tag

    @abstractmethod
    def read_value_from_tag(self):
        pass

    @abstractmethod
    def write_value_to_tag(self):
        pass


class HMIWidget(HMIObject, QWidget):
    """
    Basic HMI Widget class

    """

    def __init__(self, tag=None, parent=None):
        HMIObject.__init__(self, tag, parent)
        QWidget.__init__(self, parent)


class HMISpinBox(QSpinBox, HMIObject):
    def __init__(self, tag=None, parent=None):
        super(HMISpinBox, self).__init__(tag, parent)
        self.lineEdit().installEventFilter(self)
        self.setButtonSymbols(QDoubleSpinBox.NoButtons)
        if tag is not None:
            self.connect(self.tag, SIGNAL("value_changed()"),
                         self.read_value_from_tag)
            self.connect(self, SIGNAL("valueChanged(double)"),
                         self.write_value_to_tag)

    def eventFilter(self, *args, **kwargs):
        sender = args[0]
        event = args[1]

        if event.type() == QEvent.MouseButtonPress:
            if self.isEnabled() and not self.isReadOnly():
                numpad = NumPad(self, sender.text())
                if numpad.exec_() == QDialog.Accepted:
                    (newValue, b) = numpad.outputLineEdit.text().toDouble()
                    if b:
                        self.setValue(newValue)

        return QDoubleSpinBox.eventFilter(self, *args, **kwargs)

    def read_value_from_tag(self):
        self.setValue(self.tag.value)

    def write_value_to_tag(self):
        self.tag.value = self.value()


class HMIDoubleSpinBox(QDoubleSpinBox, HMIObject):
    def __init__(self, tag=None, parent=None):
        super(HMIDoubleSpinBox, self).__init__(tag, parent)
        self.lineEdit().installEventFilter(self)
        self.setButtonSymbols(QDoubleSpinBox.NoButtons)

        self.connect(self.tag, SIGNAL("value_changed()"), self.read_value_from_tag)
        self.connect(self, SIGNAL("valueChanged(double)"), self.write_value_to_tag)

    def eventFilter(self, *args, **kwargs):
        sender = args[0]
        event = args[1]

        if event.type() == QEvent.MouseButtonPress:
            if self.isEnabled() and not self.isReadOnly():
                numpad = NumPad(self, sender.text())
                if numpad.exec_() == QDialog.Accepted:
                    (newValue, b) = numpad.outputLineEdit.text().toDouble()
                    if b:
                        self.setValue(newValue)
                        self.valueChanged.emit(newValue)

        return QDoubleSpinBox.eventFilter(self, *args, **kwargs)

    def read_value_from_tag(self):
        self.setValue(self.tag.value)

    def write_value_to_tag(self):
        self.tag.value = self.value()


class HMIComboBox(QComboBox, HMIObject):
    def __init__(self, tag=None, parent=None):
        super(HMIComboBox, self).__init__(tag, parent)
        self.connect(self.tag, SIGNAL("value_changed()"), self.read_value_from_tag)
        self.connect(self, SIGNAL("currentIndexChanged(int)"), self.write_value_to_tag)
        self._index_changed_first_time = True

    def read_value_from_tag(self):
        self.setCurrentIndex(self.tag.value)

    def write_value_to_tag(self):
        if not self._index_changed_first_time:
            self.tag.value = self.currentIndex()
        self._index_changed_first_time = False


class HMILabel(QLabel, HMIObject):
    def __init__(self, tag=None, parent=None, format_spec="{:03.3f}"):
        super(HMILabel, self).__init__(tag, parent)
        self.format_spec = format_spec
        self.connect(self.tag, SIGNAL("value_changed()"), self.read_value_from_tag)

    def read_value_from_tag(self):
        value = self.tag.value
        self.setText(self.format_spec.format(value))

    def write_value_to_tag(self):
        pass


class HMILineEdit(QLineEdit, HMIObject):
    def __init__(self, tag=None, parent=None):
        super(HMILineEdit, self).__init__(tag, parent)
        self.connect(self.tag, SIGNAL("value_changed()"), self.read_value_from_tag)
        self.connect(self, SIGNAL("textEdited(QString)"), self.write_value_to_tag)

    def read_value_from_tag(self):
        self.setText(self.tag.value)

    def write_value_to_tag(self):
        self.tag.value = self.text()


class HMIPushButton(QPushButton, HMIObject):
    def __init__(self, tag=None, parent=None):
        super(HMIPushButton, self).__init__(tag, parent)

        QPushButton.setCheckable(self, True)
        self.connect(self, SIGNAL("toggled(bool)"), self.write_value_to_tag)
        self.connect(self.tag, SIGNAL("value_changed()"), self.read_value_from_tag)
        self._checkable = False
        self._next_time_uncheck = False

    def setCheckable(self, value):
        self._checkable = value

    def read_value_from_tag(self):
        if self._checkable:
            self.setChecked(self.tag.value)
        else:
            if self.tag.value:
                self.setChecked(False)

    def write_value_to_tag(self):
        self.tag.value = self.isChecked()


class HMITextMapper(HMIObject):
    """
    Map text messages to keys.

    :type text_definitions: dict
    :ivar text_definitions: defined pairs of numeric values and text messages

    :type text: basestring
    :ivar text: Corresponding text message to the current tag value. Empty if no text for the given
                key is defined.

    """

    def __init__(self, tag, parent=None):
        super(HMITextMapper, self).__init__(tag, parent)
        self.text_definitions = {}
        self.text = ""

        self.connect(self.tag, SIGNAL("value_changed()"), self.read_value_from_tag)

    def add_text(self, key, text):
        """
        Add a text message definition

        :param key: Tag value as key

        :type text: basestring
        :param text: text message

        """
        self.text_definitions[key] = text

    def pop_text(self, key):
        """
        Remove text message for the given key.

        :param key: Tag value as key
        :return: text message
        """
        return self.text_definitions.pop(key)

    def write_value_to_tag(self):
        pass

    def read_value_from_tag(self):
        text = self.text_definitions.get(self.tag.value)
        if text is None:
            self.text = ""
            return
        self.text = text


class HMIIndicator(QWidget, HMIObject):

    def __init__(self, tag, parent=None):
        super(HMIIndicator, self).__init__(tag, parent)
        self.connect(self.tag, SIGNAL("value_changed()"), self.read_value_from_tag)

        #Indicator images
        #----------------------------------------------------
        self.indicator_on = QPixmap(":/img/circle_green.png")
        self.indicator_off = QPixmap(":/img/circle_grey.png")

        #Text label
        #----------------------------------------------------
        self.text_label = QLabel(tag.name)
        font = self.text_label.font()
        font.setPointSize(12)
        self.text_label.setFont(font)

        #Indicator label
        #----------------------------------------------------
        self.indicator_label = QLabel()
        self.indicator_label.setScaledContents(True)
        self.indicator_label.setFixedSize(22, 22)
        self.indicator_label.setPixmap(self.indicator_off)

        #Layout
        #----------------------------------------------------
        layout = QHBoxLayout()
        layout.addWidget(self.indicator_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)

    def read_value_from_tag(self):
        if self.tag.value:
            self.indicator_label.setPixmap(self.indicator_on)
        else:
            self.indicator_label.setPixmap(self.indicator_off)

    def write_value_to_tag(self):
        pass

    def setText(self, text):
        self.text_label.setText(text)


class HMICheckBox(QCheckBox, HMIObject):

    """
    Checkbox for displaying and switching a boolean tag.

    """

    def __init__(self, tag=None, parent=None):
        super(HMICheckBox, self).__init__(tag, parent)
        self.connect(self.tag, SIGNAL("value_changed()"),
                     self.read_value_from_tag)
        self.connect(self, SIGNAL("stateChanged(int)"),
                     self.write_value_to_tag)

    def read_value_from_tag(self):
        self.setCheckState(Qt.Checked if self.tag.value else Qt.Unchecked)

    def write_value_to_tag(self):
        self.tag.value = self.isChecked()
