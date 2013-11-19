from PyQt4.QtGui import QApplication
import sys
from qthmi.main.widgets import HMIIndicator

__author__ = 'lehmann'



app = QApplication(sys.argv)
indicator = HMIIndicator()
indicator.show()
app.exec_()
