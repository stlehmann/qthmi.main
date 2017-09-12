import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QApplication
from qthmi.main.connector import AbstractPLCConnector
from qthmi.main.tag import Tag
from qthmi.main.widgets import HMIDoubleSpinBox, HMILabel, HMIComboBox, \
    HMIPushButton, HMIIndicator


__author__ = 'Stefan Lehmann'


class BufferedTestConnector(AbstractPLCConnector):

    def __init__(self):
        super(BufferedTestConnector, self).__init__()
        self.ringbuffer = [0] * 100

    def read_from_plc(self, address, datatype):
        return self.ringbuffer[address]

    def write_to_plc(self, address, value, datatype):
        self.ringbuffer[address] = value


class TestDialog(QDialog):

    def __init__(self, parent=None):
        super(TestDialog, self).__init__(parent)

        self.connector = BufferedTestConnector()
        tag1 = self.connector.add_tag(Tag("first", 10))
        tag1.scale_factor = 2.0
        self.connector.add_tag(Tag("second", 10))
        booltag = self.connector.add_tag(Tag("bool", 20, 0, datatype=bool))

        self.dspinbox1 = HMIDoubleSpinBox(tag1)
        self.label = HMILabel(booltag, format_spec="{:b}")
        self.combobox = HMIComboBox(tag1)
        self.combobox.addItems([str(x) for x in range(100)])
        self.button = HMIPushButton(booltag)
        self.button.setCheckable(True)

        self.indicator = HMIIndicator(booltag)

        layout = QVBoxLayout()
        layout.addWidget(self.dspinbox1)
        layout.addWidget(self.label)
        layout.addWidget(self.combobox)
        layout.addWidget(self.button)
        layout.addWidget(self.indicator)

        self.setLayout(layout)
        self.connector.start_autopoll(100)


app = QApplication(sys.argv)
dlg = TestDialog()
dlg.show()
app.exec_()
