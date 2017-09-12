"""
Created on 28.10.2013
@author: lehmann

"""
import sys
from PyQt5.QtWidgets import QWidget, QTableView, QApplication, QPushButton, \
    QGridLayout, QLabel, QComboBox
from qthmi.main.alarmservermodel import AlarmServerModel


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

        self.acknowledgeButton.pressed.connect(self.acknowledge_alarm)
        self.alarmComingButton.pressed.connect(self.alarm_coming)
        self.alarmGoingButton.pressed.connect(self.alarm_going)
        self.acknowledgeAllButton.pressed.connect(self.acknowledge_all)
        self.clearButton.pressed.connect(self.clear_alarm)
        self.clearAllButton.pressed.connect(self.clear_all)

    def acknowledge_alarm(self):
        alarm_nr = int(self.alarmNrComboBox.currentText())
        self.alarmserverModel.acknowledge(alarm_nr)

    def acknowledge_all(self):
        self.alarmserverModel.acknowledge_all()

    def alarm_coming(self):
        alarm_nr = int(self.alarmNrComboBox.currentText())
        self.alarmserverModel.alarm_coming(alarm_nr)

    def alarm_going(self):
        alarm_nr = int(self.alarmNrComboBox.currentText())
        self.alarmserverModel.alarm_going(alarm_nr)

    def clear_alarm(self):
        alarm_nr = int(self.alarmNrComboBox.currentText())
        self.alarmserverModel.clear(alarm_nr)

    def clear_all(self):
        self.alarmserverModel.clear_all()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    frm = MainWindow()
    frm.show()
    app.exec_()
