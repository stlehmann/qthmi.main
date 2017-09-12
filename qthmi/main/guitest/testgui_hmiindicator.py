from PyQt5.QtWidgets import QApplication
import sys
from qthmi.main.widgets import HMIIndicator
from qthmi.main.tag import Tag

__author__ = 'lehmann'

tag = Tag('test', 0)
app = QApplication(sys.argv)
indicator = HMIIndicator(tag)
indicator.show()
app.exec_()
