import sys
import pylab
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtRemoveInputHook
from qthmi.main.plot import HMIPlot, Observer
from qthmi.main.connector import AbstractPLCConnector
from qthmi.main.tag import Tag


__author__ = 'Stefan Lehmann'


class TestConnector(AbstractPLCConnector):
    def __init__(self):
        super(TestConnector, self).__init__()
        self.base = 0
        self.sinewave_generator = SinwaveGenerator()

    def read_from_plc(self, address, datatype):
        return float(address) / 1000.0 * self.sinewave_generator.next()


class SinwaveGenerator():
    def __init__(self):
        self.Ta = 0.01
        self.fa = 1.0 / self.Ta
        self.fcos = 3.5

        self.Konstant = pylab.cos(2 * pylab.pi * self.fcos * self.Ta)
        self.t0 = 1.0
        self.t1 = self.Konstant

        self.values = [0 for x in range(100)]

    def next(self):
        Tnext = ((self.Konstant * self.t1) * 2) - self.t0
        if len(self.values) % 100 > 70:
            self.values.append(pylab.random() * 2 - 1)
        else:
            self.values.append(Tnext)
        self.t0 = self.t1
        self.t1 = Tnext
        return self.values[-1]

pyqtRemoveInputHook()

app = QApplication(sys.argv)
connector = TestConnector()
connector.add_tag(Tag("Signal 1", 1000))
connector.add_tag(Tag("Signal 2", 2000))
connector.start_autopoll(100)

hmi_plot = HMIPlot(connector)
hmi_plot.add_observer(Observer(connector.tags["Signal 1"], 50))
hmi_plot.add_observer(Observer(connector.tags["Signal 2"], 200))
hmi_plot.delta_x = 100
hmi_plot.fig.autofmt_xdate()
hmi_plot.axes[0].legend(("Test", "Test2"))
hmi_plot.axes[0].set_ylim(-5, 5)
hmi_plot.axes[0].grid(True)
hmi_plot.show()
app.exec_()
