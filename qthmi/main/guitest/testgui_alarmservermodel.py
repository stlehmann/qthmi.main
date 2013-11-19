"""
Created on 28.10.2013
@author: lehmann

"""
import sys

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget, QTableView, QApplication, QPushButton, QVBoxLayout, QSpinBox, QGridLayout, QLabel, QComboBox

from alarmserver.gui import AlarmServerModel


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.alarmserverModel = AlarmServerModel()
        self.alarmserverModel.define_alarm(1, "alarm 1")
        self.alarmserverModel.define_alarm(2, "alarm 2")
        self.alarmserverModel.define_alarm(3, "alarm 3")

        self.alarmTableView = QTableView()
        self.alarmTableView.setModel(self.alarmserverModel)

        self.alarmNrLabel = QLabel("alarm number:")
        self.alarmNrComboBox = QComboBox()
        for alarm_nr in self.alarmserverModel.defined_alarms.keys():
            self.alarmNrComboBox.addItem(str(alarm_nr))

        self.alarmComingButton = QPushButton("alarm comin")
        self.alarmGoingButton = QPushButton("alarm going")
        self.acknowledgeButton = QPushButton("acknowledge")
        self.acknowledgeAllButton = QPushButton("acknowledge all")
        self.clearButton = QPushButton("clear")
        self.clearAllButton = QPushButton("clear all")

        layout = QGridLayout()
        layout.addWidget(self.alarmTableView, 0, 0, 1, 3)
        layout.addWidget(self.alarmNrLabel, 1, 0)
        layout.addWidget(self.alarmNrComboBox, 1, 1)
        layout.addWidget(self.alarmComingButton, 2, 0)
        layout.addWidget(self.alarmGoingButton, 3, 0)
        layout.addWidget(self.acknowledgeButton, 2, 1)
        layout.addWidget(self.acknowledgeAllButton, 3, 1)
        layout.addWidget(self.clearButton, 2, 2)
        layout.addWidget(self.clearAllButton, 3, 2)
        self.setLayout(layout)
        self.resize(600, 300)

        self.connect(self.acknowledgeButton, SIGNAL("pressed()"), self.acknowledge_alarm)
        self.connect(self.alarmComingButton, SIGNAL("pressed()"), self.alarm_coming)
        self.connect(self.alarmGoingButton, SIGNAL("pressed()"), self.alarm_going)
        self.connect(self.acknowledgeAllButton, SIGNAL("pressed()"), self.acknowledge_all)
        self.connect(self.clearButton, SIGNAL("pressed()"), self.clear_alarm)
        self.connect(self.clearAllButton, SIGNAL("pressed()"), self.clear_all)

    def acknowledge_alarm(self):
        alarm_nr = self.alarmNrComboBox.currentText().toInt()[0]
        self.alarmserverModel.acknowledge(alarm_nr)

    def acknowledge_all(self):
        self.alarmserverModel.acknowledge_all()

    def alarm_coming(self):
        alarm_nr = self.alarmNrComboBox.currentText().toInt()[0]
        self.alarmserverModel.alarm_coming(alarm_nr)

    def alarm_going(self):
        alarm_nr = self.alarmNrComboBox.currentText().toInt()[0]
        self.alarmserverModel.alarm_going(alarm_nr)

    def clear_alarm(self):
        alarm_nr = self.alarmNrComboBox.currentText().toInt()[0]
        self.alarmserverModel.clear(alarm_nr)

    def clear_all(self):
        self.alarmserverModel.clear_all()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    frm = MainWindow()
    frm.show()
    app.exec_()
