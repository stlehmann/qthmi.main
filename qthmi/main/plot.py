"""
Realtime data plotting
======================

Plot PLC data in Realtime.

For HMIPlot to work we need the following packages::

    >>> import sys
    >>> from PyQt4.QtGui import QApplication
    >>> from qthmi.main.connector import AbstractPLCConnector
    >>> from qthmi.main.tag import Tag
    >>> app = QApplication(sys.argv)

Now we create a new Connector and the HMIPlot object::

    >>> connector = AbstractPLCConnector()
    >>> plot = HMIPlot(connector)
    >>> type(plot)
    <class 'qthmi.main.plot.HMIPlot'>

The C{add_observer()} method is used to creat an Observer object collecting
data from the given Tag::

    >>> tag1 = connector.add_tag(Tag("tag1", 0))
    >>> plot.add_observer(tag1, "Tag1", ax=0, style="b-")
    >>> type(plot.observers[0])
    <class 'qthmi.main.plot.Observer'>

The HMIPlot object is inherited from C{QWidget} and can be displayed on its own
by calling the C{show()} function or embedded in a second QWidget object.

"""
from datetime import datetime

__author__ = "Stefan Lehmann"


import time
import pylab
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from qthmi.main.widgets import HMIWidget


class Observer(HMIWidget):
    """
    Binding object between a Tag and HMIPlot

    """

    def __init__(self, tag, buffer_size=100, label="", ax=0, style="-"):
        super(Observer, self).__init__()
        self.buffer_size = buffer_size
        self.y = []
        self.x = []
        self.tag = tag
        self.label = tag.name if label == "" else label
        self.ax = ax
        self.style = style
        self.starttime = None

    def read_value_from_tag(self):
        self.x.append(datetime.now())
        self.y.append(self.tag.value)

        if len(self.x) > self.buffer_size:
            self.x = self.x[-self.buffer_size:]
            self.y = self.y[-self.buffer_size:]

    def write_value_to_tag(self):
        pass


class TimeDeltaObserver(Observer):
    def read_value_from_tag(self):
        if len(self.x) == 0:
            self.starttime = datetime.now()

        delta = datetime.now() - self.starttime
        self.x.append(delta.total_seconds())
        self.y.append(self.tag.value)

        if len(self.x) > self.buffer_size:
            self.x = self.x[-self.buffer_size:]
            self.y = self.y[-self.buffer_size:]


class HMIPlot (QWidget, object):
    """
    Realtime Plot

    @type connector: connector.PLCConnector
    @ivar connector: connector instance for plc communication
    """

    def __init__(self, connector, parent=None, buffer_size=100):
        """
        @type connector: qthmi.main.connector.AbstractPLCConnector

        """
        super(HMIPlot, self).__init__(parent)
        self.connector = connector
        self.buffer_size = buffer_size
        self.observers = []
        self.lines = []

        #Init matplotlib objects
        #----------------------------------------------------
        self.fig = pylab.figure(1)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.axes = [self.fig.add_subplot(111)]
        self.axes.append(self.axes[0].twinx())

        #Layout
        #----------------------------------------------------
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.connect(self.connector, SIGNAL("polled()"), self.refresh)

    def add_observer(self, observer):
        """
        Add observer to HMIPlot.
        @type observer: Observer

        """
        self.observers.append(observer)

        self.lines.append(
            self.axes[observer.ax].plot([], [], observer.style,
                                                label=observer.label)[0])

    def autoscale_xaxis(self):
        self.axes[0].set_xlim(
            datetime.datetime.now() - datetime.timedelta(
                milliseconds=self.buffer_size * self.connector.cycletime),
            datetime.datetime.now()
        )

    def refresh(self):
        """
        Plot current data.

        """

        prim_observer = self.observers[0]
        if len(prim_observer.x) > 1:
            self.axes[0].set_xlim(prim_observer.x[0], prim_observer.x[-1])

        for i, observer in enumerate(self.observers):
            observer.read_value_from_tag()
            self.lines[i].set_data(observer.x, observer.y)

    def draw(self):
        self.canvas.draw()
